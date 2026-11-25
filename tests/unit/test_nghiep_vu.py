"""Kiểm thử miền độc lập với PostgreSQL."""
import unittest

from domain import DongBan, DongTra, HangHoa, PhieuBan, PhieuTra


class NghiepVu(unittest.TestCase):
    def test_tien_dong_ban_dung_gia_lich_su(self):
        dong = DongBan("D", "P", "S", 3, 25000, 1000)
        self.assertEqual(dong.thanh_tien(), 72000)

    def test_tra_het_thi_luong_con_tra_bang_khong(self):
        dong = DongBan("D", "P", "S", 3, 25000, 0)
        self.assertEqual(dong.luong_con_tra(3), 0)

    def test_chuyen_khoan_khong_tang_quy(self):
        phieu = PhieuBan("P", "C", "2026-01-15", "CK", 43000, "XONG")
        self.assertEqual(phieu.tac_dong_quy(), 0)

    def test_hoan_tien_mat_giam_quy(self):
        phieu = PhieuTra("T", "C", "P", "2026-01-15", "TM", 25000, "XONG")
        self.assertEqual(phieu.tac_dong_quy(), -25000)

    def test_hang_hong_khong_nhap_lai(self):
        dong = DongTra("DT", "T", "D", 2, "HONG")
        self.assertEqual(dong.luong_nhap_lai(), 0)

    def test_doi_gia_am_bi_chan(self):
        hang = HangHoa("S", "89", "Sữa", "180 ml", "hộp", 25000, 100, "HOAT_DONG")
        with self.assertRaises(ValueError):
            hang.gia_sau_cap_nhat(-1)
