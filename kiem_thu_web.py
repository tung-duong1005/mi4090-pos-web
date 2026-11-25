from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from threading import Barrier
import psycopg
from test_support import test_schema
from infrastructure.setup_db import install
import unittest

from web_db import ghi_phieu, ket_noi_request, XungDotYeuCau

ROOT = Path(__file__).resolve().parent
class POSWeb(unittest.TestCase):
    def setUp(self):
        ctx = test_schema()
        self.path = ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)
        with psycopg.connect(self.path, autocommit=True) as db:
            install(db)
            db.execute("INSERT INTO nhan_vien VALUES('N','Thu ngân','HOAT_DONG')")
            db.execute("INSERT INTO tai_khoan VALUES('T','N','tn','fixture','TN','HOAT_DONG')")
            db.execute("INSERT INTO hang_hoa VALUES('S','89','Sữa','180 ml','hộp',25000,2,'HOAT_DONG')")
            db.execute("INSERT INTO ca_thu_ngan(ma_ca,nguoi_mo,gio_mo,tien_dau,trang_thai) VALUES('C','N','2026-11-25',0,'MO')")


    def ban(self, khoa, sl):
        with ket_noi_request(self.path) as dl:
            return ghi_phieu(dl,'T','02',khoa,ca='C',pt='CK',dong=[('S',sl,0)])

    def ket_qua(self):
        with ket_noi_request(self.path) as dl:
            row = dl.mot("""SELECT (SELECT count(*) FROM phieu_ban) AS ban,
                         (SELECT count(*) FROM web_yeu_cau) AS yeu_cau,(SELECT ton FROM v_ton) AS ton""")
            return row["ban"], row["yeu_cau"], row["ton"]

    def test_01_khoi_tao(self):
        with ket_noi_request(self.path) as dl:
            n = dl.mot("""SELECT count(*) AS n FROM information_schema.tables
                          WHERE table_schema=current_schema() AND table_type='BASE TABLE'""")
            self.assertEqual(n["n"], 15)

    def test_02_tra_va_gui_lai(self):
        ma,_ = self.ban('B',2)
        with ket_noi_request(self.path) as dl:
            d = dl.mot("SELECT ma_dong_ban FROM dong_ban WHERE ma_ban=%s",ma)['ma_dong_ban']
            args = dict(ca='C',pt='CK',dong=[(d,1,'TOT')],goc=ma)
            tra,moi = ghi_phieu(dl,'T','03','R',**args)
            self.assertTrue(moi)
            self.assertEqual(ghi_phieu(dl,'T','03','R',**args),(tra,False))
            self.assertEqual(dl.mot("SELECT tien_hoan FROM phieu_tra")['tien_hoan'],25000)
        self.assertEqual(self.ket_qua(),(1,2,1))

    def test_03_gui_cung_khoa_dong_thoi(self):
        barrier = Barrier(2)
        def gui(_):
            barrier.wait(timeout=5)
            return self.ban('B',2)
        with ThreadPoolExecutor(2) as pool:
            a,b = pool.map(gui,range(2))
        self.assertEqual(a[0],b[0])
        self.assertEqual({a[1],b[1]},{True,False})
        self.assertEqual(self.ket_qua(),(1,1,0))
        with self.assertRaises(XungDotYeuCau):
            self.ban('B',1)

    def test_04_khac_khoa_tranh_ton(self):
        barrier = Barrier(2)
        def gui(k):
            barrier.wait(timeout=5)
            try:
                self.ban(k,2)
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(2) as pool:
            self.assertEqual(sorted(pool.map(gui,['A','B'])),[False,True])
        self.assertEqual(self.ket_qua(),(1,1,0))

    def test_05_loi_sau_ghi_phieu(self):
        with ket_noi_request(self.path) as dl:
            dl.db.execute("ALTER TABLE web_yeu_cau ADD CHECK (khoa <> 'B')")
        with self.assertRaises(psycopg.IntegrityError):
            self.ban('B',1)
        self.assertEqual(self.ket_qua(),(0,0,2))

    def test_06_khoa_tai_khoan(self):
        self.ban('B',1)
        with ket_noi_request(self.path) as dl:
            dl.db.execute("UPDATE tai_khoan SET trang_thai='NGUNG'")
        with self.assertRaises(PermissionError):
            self.ban('B',1)

if __name__=='__main__':
    unittest.main(verbosity=2)
