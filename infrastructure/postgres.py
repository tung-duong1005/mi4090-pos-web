from __future__ import annotations
import psycopg
from psycopg.pq import TransactionStatus
from psycopg.rows import dict_row
from datetime import datetime
from dataclasses import fields
from contextlib import contextmanager
from infrastructure.setup_db import install
from uuid import uuid4
from application.ports import ITonKho, IPosStore
from domain.common import luc, yeu_cau
from domain import (NhanVien, TaiKhoan, NhatKy, HangHoa, CaThuNgan, PhieuBan, DongBan, PhieuTra, DongTra, ThuChiKhac, PhieuNhap, DongNhap, PhieuKiem, DongKiem, BaoCaoCa)

BANG = {
    NhanVien: ('nhan_vien', 'ma_nv'),
    TaiKhoan: ('tai_khoan', 'ma_tk'),
    NhatKy: ('nhat_ky', 'ma_log'),
    HangHoa: ('hang_hoa', 'ma_hang'),
    CaThuNgan: ('ca_thu_ngan', 'ma_ca'),
    PhieuBan: ('phieu_ban', 'ma_ban'),
    DongBan: ('dong_ban', 'ma_dong_ban'),
    PhieuTra: ('phieu_tra', 'ma_tra'),
    DongTra: ('dong_tra', 'ma_dong_tra'),
    ThuChiKhac: ('thu_chi_khac', 'ma_tc'),
    PhieuNhap: ('phieu_nhap', 'ma_nhap'),
    DongNhap: ('dong_nhap', 'ma_dong_nhap'),
    PhieuKiem: ('phieu_kiem', 'ma_kiem'),
    DongKiem: ('dong_kiem', 'ma_kiem'),
}
CHI_TIET = {PhieuBan: DongBan, PhieuTra: DongTra, PhieuNhap: DongNhap, PhieuKiem: DongKiem}


def _thuoc_tinh(lop, row):
    # DTO miền dùng chuỗi ISO như 4.1. Adapter đổi từ TIMESTAMPTZ có múi giờ.
    values = {}
    for field in fields(lop):
        if field.name == "dong":
            continue
        value = row[field.name]
        values[field.name] = value.isoformat(timespec="microseconds") if isinstance(value, datetime) else value
    return values


class KhoDuLieu(IPosStore):
    def __init__(self, dsn):
        self.db = psycopg.connect(dsn, autocommit=True, row_factory=dict_row, connect_timeout=5)
        self.db.execute("SET TIME ZONE 'UTC'")

    def khoi_tao(self):
        install(self.db)

    @contextmanager
    def giao_dich(self, chi_doc=False):
        ngoai = self.db.info.transaction_status == TransactionStatus.IDLE
        with self.db.transaction():
            if ngoai and chi_doc:
                self.db.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
            elif ngoai:
                self.db.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                self.db.execute("SET LOCAL lock_timeout = '5s'")
                self.db.execute("SELECT pos_khoa_ghi()")
            yield

    def mot(self, sql, *args):
        r = self.db.execute(sql, args).fetchone()
        yeu_cau(r is not None, 'Không tìm thấy dữ liệu')
        return r

    def lay(self, lop, ma):
        bang, pk = BANG[lop]
        if lop is DongKiem:
            row = self.mot("SELECT * FROM dong_kiem WHERE ma_kiem=%s AND ma_hang=%s", *ma)
        else:
            row = self.mot(f"SELECT * FROM {bang} WHERE {pk}=%s", ma)
        attrs = _thuoc_tinh(lop, row)
        if lop in CHI_TIET:
            con = CHI_TIET[lop]
            bang_con = BANG[con][0]
            attrs['dong'] = tuple(con(**_thuoc_tinh(con, d)) for d in self.db.execute(
                f"SELECT * FROM {bang_con} WHERE {pk}=%s ORDER BY thu_tu", (ma,)))
        return lop(**attrs)

    def ghi_nhat_ky(self, tk, uc, loai, ma):
        self.db.execute("INSERT INTO nhat_ky VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (uuid4().hex, tk, luc(), uc, loai, ma, 'THANH_CONG'))

    def ca_dang_mo(self, nv):
        return self.db.execute("""SELECT ma_ca, nguoi_mo, tien_dau::text AS tien_dau
                                  FROM ca_thu_ngan WHERE nguoi_mo=%s AND trang_thai='MO'""",
                               (nv,)).fetchone()

    def tao_ca(self, ma, nv, dau):
        self.db.execute("""INSERT INTO ca_thu_ngan(ma_ca,nguoi_mo,gio_mo,tien_dau,trang_thai)
                                     VALUES(%s,%s,%s,%s,'MO')""", (ma,nv,luc(),dau))

    def tao_ban_nhap(self, ma, ca, pt):
        self.db.execute("INSERT INTO phieu_ban VALUES(%s,%s,%s,%s,0,'NHAP')", (ma,ca,luc(),pt))

    def them_dong_ban(self, ma, hang, sl, gia, giam):
        self.db.execute("INSERT INTO dong_ban(ma_dong_ban,ma_ban,ma_hang,sl,don_gia,giam) VALUES(%s,%s,%s,%s,%s,%s)",
                                           (uuid4().hex,ma,hang,sl,gia,giam))

    def chot_ban(self, ma, tong):
        self.db.execute("UPDATE phieu_ban SET tien_thu=%s,trang_thai='XONG' WHERE ma_ban=%s",
                                       (tong,ma))

    def tao_tra_nhap(self, ma, ca, goc, pt):
        self.db.execute("INSERT INTO phieu_tra VALUES(%s,%s,%s,%s,%s,0,'NHAP')",(ma,ca,goc,luc(),pt))

    def them_dong_tra(self, ma, ma_dong, sl, tinh_trang):
        self.db.execute("INSERT INTO dong_tra(ma_dong_tra,ma_tra,ma_dong_ban,sl,tinh_trang) VALUES(%s,%s,%s,%s,%s)",
                                           (uuid4().hex,ma,ma_dong,sl,tinh_trang))

    def chot_tra(self, ma, tong):
        self.db.execute("UPDATE phieu_tra SET tien_hoan=%s,trang_thai='XONG' WHERE ma_tra=%s", (tong,ma))

    def ghi_thu_chi(self, ma, ca, loai, tien, ly_do):
        self.db.execute("INSERT INTO thu_chi_khac VALUES(%s,%s,%s,%s,%s,%s,'XONG')",
                                       (ma,ca,luc(),loai,tien,ly_do))

    def ghi_ban_giao(self, ma, quy, dem, giai_trinh):
        self.db.execute("""UPDATE ca_thu_ngan SET du_kien=%s,thuc_dem=%s,giai_trinh=%s,
                                      trang_thai='BAN_GIAO' WHERE ma_ca=%s""",(quy,dem,giai_trinh,ma))

    def ghi_chot_ca(self, ma, nv):
        return self.db.execute("""UPDATE ca_thu_ngan SET nguoi_chot=%s,gio_dong=%s,trang_thai='DONG'
                                          WHERE ma_ca=%s AND trang_thai='BAN_GIAO'""",(nv,luc(),ma)).rowcount

    def ghi_gia(self, hang, gia):
        self.db.execute('UPDATE hang_hoa SET gia=%s WHERE ma_hang=%s',(gia,hang))

    def tao_nhap(self, ma, nv, ncc):
        self.db.execute("INSERT INTO phieu_nhap VALUES(%s,%s,%s,%s,'NHAP')",(ma,nv,luc(),ncc))

    def them_dong_nhap(self, ma, hang, sl, gia):
        self.db.execute("INSERT INTO dong_nhap(ma_dong_nhap,ma_nhap,ma_hang,sl,don_gia) VALUES(%s,%s,%s,%s,%s)",(uuid4().hex,ma,hang,sl,gia))

    def chot_nhap(self, ma):
        self.db.execute("UPDATE phieu_nhap SET trang_thai='XONG' WHERE ma_nhap=%s", (ma,))

    def tao_kiem(self, ma, nv):
        self.db.execute("""INSERT INTO phieu_kiem(ma_kiem,nguoi_lap,luc_lap,trang_thai)
                                       VALUES(%s,%s,%s,'NHAP')""",(ma,nv,luc()))

    def them_dong_kiem(self, ma, hang, thoi_diem, ton, moc, dem, ly_do):
        self.db.execute("INSERT INTO dong_kiem(ma_kiem,ma_hang,luc_dem,ton_so,moc_so,thuc_dem,giai_trinh) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                           (ma,hang,thoi_diem,ton,moc,dem,ly_do))

    def gui_phieu_kiem(self, ma):
        self.db.execute("UPDATE phieu_kiem SET trang_thai='CHO',luc_gui=%s WHERE ma_kiem=%s", (luc(),ma))

    def ghi_xet_kiem(self, ma, trang_thai, nv, ly_do):
        self.db.execute("""UPDATE phieu_kiem SET trang_thai=%s,nguoi_xet=%s,luc_xet=%s,ly_do=%s
                                         WHERE ma_kiem=%s""",(trang_thai,nv,luc(),ly_do,ma))

    def tong_da_tra(self, ma_dong, ma):
        return self.mot("""SELECT coalesce(sum(d.sl),0)::bigint AS sl FROM dong_tra d
                          JOIN phieu_tra p USING(ma_tra) WHERE d.ma_dong_ban=%s
                          AND (p.trang_thai='XONG' OR p.ma_tra=%s)""", ma_dong,ma)["sl"]

    def chung_tu_ca(self, ma):
        chung_tu = []
        for lop in (PhieuBan, PhieuTra, ThuChiKhac):
            bang, pk = BANG[lop]
            for r in self.db.execute(f"SELECT {pk} FROM {bang} WHERE ma_ca=%s", (ma,)):
                chung_tu.append(self.lay(lop,r[pk]))
        return tuple(chung_tu)

    def tim_yeu_cau(self, ma_tk, uc, khoa):
        row = self.db.execute("""SELECT bam_noi_dung,coalesce(ma_ban,ma_tra) AS ma FROM web_yeu_cau
        WHERE ma_tk=%s AND nghiep_vu=%s AND khoa=%s""", (ma_tk,uc,khoa)).fetchone()
        return dict(row) if row is not None else None

    def luu_yeu_cau(self, ma_tk, uc, khoa, digest, ma):
        self.db.execute("INSERT INTO web_yeu_cau VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (ma_tk,uc,khoa,digest,ma if uc=="02" else None,ma if uc=="03" else None,luc()))

class SoKhoPostgreSQL(ITonKho):
    def __init__(self, du_lieu: KhoDuLieu):
        self.du_lieu = du_lieu

    def so_du(self, ma_hang: str) -> tuple[int, int]:
        r = self.du_lieu.mot('SELECT ton,moc FROM v_ton WHERE ma_hang=%s', ma_hang)
        return r['ton'], r['moc']

    def hang_ban(self, ma_hang: str) -> HangHoa:
        h = self.du_lieu.lay(HangHoa, ma_hang)
        yeu_cau(h.trang_thai == 'HOAT_DONG', 'Hàng ngừng bán')
        return h


@contextmanager
def ket_noi_request(dsn):
    dl = KhoDuLieu(dsn)
    try:
        yield dl
    finally:
        dl.db.close()
