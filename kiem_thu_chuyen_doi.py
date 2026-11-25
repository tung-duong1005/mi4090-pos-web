import shutil
import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import psycopg
from infrastructure.import_sqlite import import_from
from infrastructure.postgres import ket_noi_request
from bootstrap import ghi_phieu
from test_support import test_schema
from hashlib import sha256

FIXTURE = Path(__file__).parent / "fixtures" / "legacy_empty.sqlite"


class ChuyenDoi(unittest.TestCase):
    def test_phieu_cu_va_gui_lai(self):
        with TemporaryDirectory() as directory, test_schema() as dsn:
            src = Path(directory) / "pos.sqlite"
            shutil.copyfile(FIXTURE, src)
            old = sqlite3.connect(src)
            try:
                with old:
                    old.execute("INSERT INTO nhan_vien VALUES ('N','Thu ngân','HOAT_DONG')")
                    old.execute("INSERT INTO tai_khoan VALUES ('T','N','tn','fixture','TN','HOAT_DONG')")
                    old.execute("INSERT INTO hang_hoa VALUES ('S','89','Sữa','180 ml','hộp',5000,5,'HOAT_DONG')")
                    old.execute("""INSERT INTO ca_thu_ngan(ma_ca,nguoi_mo,gio_mo,tien_dau,trang_thai)
                                   VALUES ('C','N','2026-01-01',0,'MO')""")
                    old.execute("INSERT INTO phieu_ban VALUES ('B','C','2026-01-01','TM',0,'NHAP')")
                    old.execute("INSERT INTO dong_ban VALUES ('z','B','S',1,5000,0)")
                    old.execute("INSERT INTO dong_ban VALUES ('a','B','S',1,5000,0)")
                    old.execute("UPDATE phieu_ban SET tien_thu=10000,trang_thai='XONG' WHERE ma_ban='B'")
                    digest = sha256(b'["C","TM",null,[["S",1,0],["S",1,0]]]').hexdigest()
                    old.execute("INSERT INTO web_yeu_cau VALUES ('T','02','retry',?,'B',NULL,'2026-01-01')",(digest,))
            finally:
                old.close()
            with psycopg.connect(dsn, autocommit=True) as dest:
                counts = import_from(src, dest)
                self.assertEqual(counts["dong_ban"], 2)
                self.assertEqual(dest.execute("SELECT ton,moc FROM v_ton").fetchone(), (3,2))
                self.assertEqual(dest.execute("SELECT ma_dong_ban FROM dong_ban ORDER BY thu_tu").fetchall(),
                                 [("z",),("a",)])
            with ket_noi_request(dsn) as dl:
                result = ghi_phieu(dl,"T","02","retry",ca="C",pt="TM",dong=[("S",1,0),("S",1,0)])
                self.assertEqual(result, ("B",False))
                self.assertEqual(dl.mot("SELECT count(*) AS n FROM phieu_ban")["n"],1)

    def test_loi_hoan_tac_va_bao_toan_nguon(self):
        with TemporaryDirectory() as directory, test_schema() as dsn:
            src = Path(directory) / "bad.sqlite"
            shutil.copyfile(FIXTURE, src)
            old = sqlite3.connect(src)
            try:
                with old:
                    old.execute("INSERT INTO nhan_vien VALUES ('N','N','HOAT_DONG')")
                    old.execute("""INSERT INTO ca_thu_ngan(ma_ca,nguoi_mo,gio_mo,tien_dau,trang_thai)
                                   VALUES ('C','N','khong-phai-ngay',0,'MO')""")
            finally:
                old.close()
            with psycopg.connect(dsn, autocommit=True) as dest:
                with self.assertRaises(ValueError):
                    import_from(src, dest)
                self.assertIsNone(dest.execute("SELECT to_regclass('ca_thu_ngan')").fetchone()[0])
            with sqlite3.connect(f"{src.as_uri()}?mode=ro",uri=True) as old:
                self.assertEqual(old.execute("SELECT gio_mo FROM ca_thu_ngan").fetchone()[0],"khong-phai-ngay")


if __name__ == "__main__":
    unittest.main(verbosity=2)
