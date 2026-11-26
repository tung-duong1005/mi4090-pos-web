"""Chạy: python -B kiem_chung.py. Mỗi ca dùng một schema PostgreSQL riêng."""
from pathlib import Path
import ast
import re
import psycopg
from test_support import test_schema
import unittest
from domain import *
from pos import BANG, KhoDuLieu, QuayService, KhoService, SoKhoPostgreSQL, PhienPOS

ROOT = Path(__file__).parent
class Muc41(unittest.TestCase):
    def setUp(self):
        ctx = test_schema()
        self.file = ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)
        self.dl = KhoDuLieu(self.file)
        self.db = self.dl.db
        self.addCleanup(self.db.close)
        self.dl.khoi_tao()
        for nv,vai in [('N1','TN'),('N2','KHO'),('N3','QL'),('N4','QT')]:
            self.db.execute("INSERT INTO nhan_vien VALUES(%s,%s,'HOAT_DONG')",(nv,nv))
            self.db.execute("INSERT INTO tai_khoan VALUES(%s,%s,%s,'fixture-no-login',%s,'HOAT_DONG')",
                            (nv,nv,'user'+nv,vai))
        self.db.execute("INSERT INTO hang_hoa VALUES('S','8900','Sữa','Hộp 180 ml','hộp',25000,20,'HOAT_DONG')")
        self.so = SoKhoPostgreSQL(self.dl)
        self.tn = QuayService(PhienPOS(self.dl,'N1'),self.so)
        self.kho = KhoService(PhienPOS(self.dl,'N2'),self.so)
        self.ql = KhoService(PhienPOS(self.dl,'N3'),self.so)
        self.chot = QuayService(PhienPOS(self.dl,'N3'),self.so)
        self.tn.mo_ca('C',200000)

    def ban_mau(self):
        self.tn.ban('B','C','CK',[('S',2,0)])
        return self.dl.lay(PhieuBan,'B').dong[0].ma_dong_ban

    def test_01_bang_va_khoa_ngoai(self):
        tables = {r["tablename"] for r in self.db.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname=current_schema()")}
        self.assertEqual(tables, {t for t, _ in BANG.values()} | {"web_yeu_cau"})
        count = self.db.execute("""SELECT count(*) FROM pg_constraint
                WHERE connamespace=current_schema()::regnamespace AND contype='f'""").fetchone()["count"]
        self.assertEqual(count, 22)

    def test_02_ban_ck_in_lai_va_rollback(self):
        self.ban_mau()
        phieu = self.dl.lay(PhieuBan,'B')
        self.assertEqual((phieu.tinh_tong(),phieu.tien_thu,phieu.tac_dong_quy()),(50000,50000,0))
        self.assertEqual(self.so.so_du('S'),(18,1))
        self.assertEqual(self.tn.bao_cao_ca('C').tien_du_kien(),200000)
        with self.assertRaises(psycopg.IntegrityError):
            self.tn.ban('X','C','TM',[('S',11,0),('S',10,0)])
        with self.assertRaises(psycopg.IntegrityError):
            self.tn.ban('B','C','CK',[('S',2,0)])
        self.assertEqual(self.so.so_du('S'),(18,1))
        self.assertEqual(self.db.execute("SELECT count(*) FROM dong_ban").fetchone()["count"],1)

    def test_03_tra_gia_cu_khac_ca_hong_va_vuot(self):
        d = self.ban_mau()
        self.ql.doi_gia('S',30000)
        self.tn.ban_giao('C',200000)
        self.chot.chot_ca('C')
        self.tn.mo_ca('C2',80000)
        self.tn.tra('R','C2','B','TM',[(d,1,'TOT')])
        self.assertEqual(self.dl.lay(PhieuTra,'R').tien_hoan,25000)
        with self.assertRaises(ValueError):
            self.tn.tra('X','C2','B','TM',[(d,1,'TOT'),(d,1,'TOT')])
        self.tn.tra('R2','C2','B','CK',[(d,1,'HONG')])
        self.assertEqual(self.tn.bao_cao_ca('C2').tien_du_kien(),55000)
        self.assertEqual(self.so.so_du('S'),(19,2))
        self.assertEqual(self.db.execute("SELECT count(*) FROM phieu_tra").fetchone()["count"],2)

    def test_04_xoa_cha_qua_bien(self):
        d = self.ban_mau()
        for sql in ["DELETE FROM hang_hoa WHERE ma_hang='S'","DELETE FROM nhan_vien WHERE ma_nv='N1'",
                    "DELETE FROM dong_ban","UPDATE dong_ban SET don_gia=1","DELETE FROM phieu_ban"]:
            with self.assertRaises(psycopg.IntegrityError):
                self.db.execute(sql)
        self.db.execute("UPDATE hang_hoa SET trang_thai='NGUNG' WHERE ma_hang='S'")
        self.tn.tra('R','C','B','TM',[(d,1,'HONG')])
        self.assertEqual(self.dl.lay(DongBan,d).don_gia,25000)

    def test_05_nhap_va_kiem_0_duyet_mot_lan(self):
        self.kho.nhap('N','NCC A',[('S',3,10000)])
        self.assertEqual(self.dl.lay(PhieuNhap,'N').gia_tri_nhap(),30000)
        moc = self.kho.moc_dem('S')
        with self.assertRaises(psycopg.IntegrityError):
            self.kho.gui_kiem('E',[('S',moc,None,None)])
        self.kho.gui_kiem('K',[('S',moc,0,'Không thấy hàng')])
        for tk in ('N1','N2','N4'):
            with self.assertRaises(PermissionError):
                KhoService(PhienPOS(self.dl,tk),self.so).xet_kiem('K',True)
        self.assertEqual(self.so.so_du('S')[0],23)
        self.ql.xet_kiem('K',True)
        self.assertEqual(self.so.so_du('S')[0],0)
        self.assertEqual(self.dl.lay(DongKiem,('K','S')).chenh_lech(),-23)
        with self.assertRaises(ValueError):
            self.ql.xet_kiem('K',True)

    def test_06_phat_sinh_sau_dem(self):
        self.kho.gui_kiem('K',[('S',self.kho.moc_dem('S'),18,None)])
        self.ban_mau()
        with self.assertRaises(psycopg.IntegrityError):
            self.ql.xet_kiem('K',True)
        self.assertTrue(self.dl.lay(PhieuKiem,'K').cho_phep_xet())
        self.ql.xet_kiem('K',False,'Đếm lại')
        self.assertEqual(self.so.so_du('S')[0],18)

    def test_07_giam_gia_va_ban_giao(self):
        self.tn.ban('B','C','TM',[('S',4,1000)])
        d = self.dl.lay(PhieuBan,'B').dong[0]
        self.tn.tra('R','C','B','TM',[(d.ma_dong_ban,1,'TOT')])
        self.tn.thu_chi('P','C','CHI',10000,'Giấy in')
        self.assertEqual(self.tn.bao_cao_ca('C').tien_du_kien(),262000)
        with self.assertRaises(psycopg.IntegrityError):
            self.tn.ban_giao('C',260000)
        self.tn.ban_giao('C',260000,'Thiếu 2000')
        self.chot.chot_ca('C')
        self.assertEqual(self.dl.lay(CaThuNgan,'C').nguoi_chot,'N3')
        with self.assertRaises(ValueError):
            self.tn.ban('X','C','TM',[('S',1,0)])

    def test_08_huy_nhap_va_lich_su(self):
        self.db.execute("INSERT INTO phieu_ban VALUES('X','C','2026-01-01','TM',0,'NHAP')")
        self.db.execute("INSERT INTO dong_ban VALUES('d','X','S',2,25000,0)")
        self.db.execute("UPDATE phieu_ban SET trang_thai='HUY' WHERE ma_ban='X'")
        self.assertEqual(self.so.so_du('S'),(20,0))
        self.assertEqual(self.tn.bao_cao_ca('C').tien_du_kien(),200000)

    def test_chieu_cot_voi_lop_mien(self):
        for model,(table,_) in BANG.items():
            fields={r['column_name'] for r in self.db.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_schema=current_schema() "
                "AND table_name=%s AND column_name<>'thu_tu'", (table,))}
            self.assertEqual(fields,set(model.__annotations__) - {'dong'})


class SoDo(unittest.TestCase):
    def test_uml_va_code(self):
        text=(ROOT/'UML.md').read_text(encoding='utf-8').split('```mermaid')[1].split('```')[0]
        shown={}
        for name, body in re.findall(r'class (\w+) \{\n(.*?)\n  \}',text,re.S):
            shown[name]=set(line.strip() for line in body.splitlines() if line.strip() and '<<' not in line)
        actual={}
        for file in ['domain/__init__.py', 'application/ports.py', 'application/phien.py', 'application/quay.py', 'application/kho.py', 'infrastructure/postgres.py']:
            for node in ast.parse((ROOT/file).read_text(encoding='utf-8')).body:
                if not isinstance(node,ast.ClassDef): continue
                members=set()
                for f in node.body:
                    if isinstance(f,ast.AnnAssign):
                        members.add('+'+f.target.id)
                    if isinstance(f,ast.FunctionDef):
                        if f.name=='__init__':
                            for a in f.body:
                                if isinstance(a,ast.Assign):
                                    for target in a.targets:
                                        if (isinstance(target,ast.Attribute) and isinstance(target.value,ast.Name)
                                                and target.value.id=='self'):
                                            members.add('+'+target.attr)
                        elif not f.name.startswith('_'):
                            names=[x.arg for x in f.args.args[1:]]
                            if f.args.vararg:
                                names.append('*'+f.args.vararg.arg)
                            members.add('+'+f.name+'('+', '.join(names)+')')
                actual[node.name]=members
        self.assertEqual(shown,actual)
        self.assertEqual(len(actual),24)
        self.assertTrue(all(k in text for k in ['*--','o--','..>','..|>','--|>',' -- ']))

if __name__=='__main__':
    unittest.main(verbosity=2)
