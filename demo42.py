"""Kịch bản bảo vệ 4.2. Chạy: python -B demo42.py TV1 (hoặc TV2)."""
import argparse
import psycopg
from test_support import test_schema
import sys
from contextlib import contextmanager

from domain import CaThuNgan, PhieuBan, PhieuKiem, PhieuNhap, PhieuTra
from pos import KhoDuLieu, KhoService, PhienPOS, QuayService, SoKhoPostgreSQL


@contextmanager
def bi_chan(loi, tinh_huong):
    try:
        yield
    except loi as exc:
        print(f"CHẶN | {tinh_huong} | {type(exc).__name__}: {exc}")
    else:
        raise AssertionError(f"Đáng lẽ phải chặn: {tinh_huong}")


def tao_phien(dl):
    dl.khoi_tao()
    for ma, vai in [('T','TN'), ('K','KHO'), ('Q','QL')]:
        dl.db.execute("INSERT INTO nhan_vien VALUES(%s,%s,'HOAT_DONG')", (ma,ma))
        dl.db.execute("INSERT INTO tai_khoan VALUES(%s,%s,%s,'fixture-no-login',%s,'HOAT_DONG')",
                      (ma, ma, 'demo'+ma, vai))
    dl.db.execute("INSERT INTO hang_hoa VALUES('S','8900','Sữa','180 ml','hộp',25000,20,'HOAT_DONG')")
    so = SoKhoPostgreSQL(dl)
    tn = QuayService(PhienPOS(dl,'T'),so)
    tn.mo_ca('C1',200000)
    return tn, KhoService(PhienPOS(dl,'K'),so), KhoService(PhienPOS(dl,'Q'),so), QuayService(PhienPOS(dl,'Q'),so), so


def tv1(dl):
    tn, _, ql, quan_ly_ca, so = tao_phien(dl)
    tn.ban('PB015','C1','CK',[('S',2,0)])
    pb = dl.lay(PhieuBan,'PB015')
    dong = pb.dong[0].ma_dong_ban
    assert (pb.trang_thai,pb.tien_thu,so.so_du('S')[0],tn.bao_cao_ca('C1').tien_du_kien()) == ('XONG',50000,18,200000)
    print("UC02 | PB015 XONG | thu CK 50.000 | tồn 18 | quỹ 200.000")
    with bi_chan(psycopg.IntegrityError,'hai dòng cùng mã, tổng 20 > tồn 18'):
        tn.ban('PB-LOI','C1','TM',[('S',10,0),('S',10,0)])
    assert dl.mot("SELECT count(*) FROM phieu_ban WHERE ma_ban='PB-LOI'")["count"] == 0
    assert dl.mot("SELECT count(*) FROM dong_ban WHERE ma_ban='PB-LOI'")["count"] == 0
    assert so.so_du('S')[0] == 18
    with bi_chan(psycopg.IntegrityError,'thử XONG → HUY trên PB015 đã ghi sổ'):
        with dl.giao_dich():
            dl.db.execute("UPDATE phieu_ban SET trang_thai='HUY' WHERE ma_ban='PB015'")
    assert (dl.lay(PhieuBan,'PB015').trang_thai,so.so_du('S')[0]) == ('XONG',18)
    print("SAU KHI CHẶN | PB015 vẫn XONG | tồn 18")
    tn.ban_giao('C1',200000)
    quan_ly_ca.chot_ca('C1')
    with bi_chan(ValueError,'chốt lại C1: DONG → DONG'):
        quan_ly_ca.chot_ca('C1')
    with bi_chan(ValueError,'xác nhận bán vào ca DONG'):
        tn.ban('PB-DONG','C1','TM',[('S',1,0)])
    assert dl.lay(CaThuNgan,'C1').trang_thai == 'DONG'
    assert dl.mot("SELECT count(*) FROM phieu_ban WHERE ma_ban='PB-DONG'")["count"] == 0
    ql.doi_gia('S',30000)
    tn.mo_ca('C2',80000)
    tn.tra('PT1','C2','PB015','TM',[(dong,1,'TOT')])
    assert dl.lay(PhieuTra,'PT1').tien_hoan == 25000
    assert so.so_du('S')[0] == 19
    with bi_chan(ValueError,'trả tiếp 2 khi chỉ còn được trả 1'):
        tn.tra('PT-LOI','C2','PB015','TM',[(dong,2,'TOT')])
    assert dl.mot("SELECT count(*) FROM phieu_tra WHERE ma_tra='PT-LOI'")["count"] == 0
    tn.tra('PT2','C2','PB015','CK',[(dong,1,'HONG')])
    assert (dl.lay(PhieuTra,'PT2').tien_hoan,so.so_du('S')[0],tn.bao_cao_ca('C2').tien_du_kien()) == (25000,19,55000)
    print("UC03 | 2 lần hoàn theo giá gốc 25.000 | TOT +1, HONG +0 | tồn 19 | quỹ ca nhận trả 55.000")


def tv2(dl):
    tn, kho, ql, _, so = tao_phien(dl)
    with bi_chan(psycopg.IntegrityError,'nhập 2 dòng, dòng thứ hai có lượng 0'):
        kho.nhap('PN-LOI','NCC A',[('S',3,10000),('S',0,10000)])
    assert dl.mot("SELECT count(*) FROM phieu_nhap WHERE ma_nhap='PN-LOI'")["count"] == 0
    assert dl.mot("SELECT count(*) FROM dong_nhap WHERE ma_nhap='PN-LOI'")["count"] == 0
    assert so.so_du('S')[0] == 20
    kho.nhap('PN1','NCC A',[('S',3,10000)])
    assert (dl.lay(PhieuNhap,'PN1').gia_tri_nhap(),so.so_du('S')[0]) == (30000,23)
    print("UC07 | PN1 XONG | giá trị nhập 30.000 | tồn 20 → 23")
    kho.gui_kiem('PK1',[('S',kho.moc_dem('S'),21,'Kiểm cuối buổi')])
    assert (dl.lay(PhieuKiem,'PK1').trang_thai,so.so_du('S')[0]) == ('CHO',23)
    tn.ban('PB1','C1','CK',[('S',1,0)])
    with bi_chan(psycopg.IntegrityError,'đã bán 1 sau khi đếm'):
        ql.xet_kiem('PK1',True)
    assert (dl.lay(PhieuKiem,'PK1').trang_thai,so.so_du('S')[0]) == ('CHO',22)
    ql.xet_kiem('PK1',False,'Cần đếm lại theo mốc mới')
    assert dl.lay(PhieuKiem,'PK1').trang_thai == 'TU_CHOI'
    kho.gui_kiem('PK2',[('S',kho.moc_dem('S'),20,'Kiểm lại')])
    with bi_chan(PermissionError,'nhân viên kho tự duyệt'):
        kho.xet_kiem('PK2',True)
    ql.xet_kiem('PK2',True)
    assert (dl.lay(PhieuKiem,'PK2').trang_thai,so.so_du('S')[0]) == ('DUYET',20)
    with bi_chan(ValueError,'xét lại PK2: DUYET → TU_CHOI'):
        ql.xet_kiem('PK2',False,'Thử xét lần hai')
    k = dl.lay(PhieuKiem,'PK2')
    assert (k.trang_thai,k.nguoi_xet,k.ly_do,so.so_du('S')[0]) == ('DUYET','Q',None,20)
    print("UC08–09 | PK1 từ chối; PK2 duyệt | tồn cuối 20 | giữ quyết định sau lần xét bị cấm")


def chay(vai):
    with test_schema() as dsn:
        dl = KhoDuLieu(dsn)
        try:
            (tv1 if vai == 'TV1' else tv2)(dl)
            print(f"PASS {vai}")
        finally:
            dl.db.close()


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('vai',choices=['TV1','TV2'])
    chay(parser.parse_args().vai)
