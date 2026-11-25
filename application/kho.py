from domain import HangHoa, PhieuKiem
from application.ports import ITonKho
from application.phien import PhienPOS
from domain.common import luc, yeu_cau

class KhoService:
    def __init__(self, phien: PhienPOS, kho: ITonKho):
        self.phien = phien
        self.dl = phien.du_lieu
        self.kho = kho

    def doi_gia(self, hang, moi):
        with self.dl.giao_dich():
            self.phien.kiem_quyen('06')
            h = self.dl.lay(HangHoa,hang).gia_sau_cap_nhat(moi)
            self.dl.ghi_gia(hang, h.gia)
            self.dl.ghi_nhat_ky(self.phien.ma_tk,'06','hang_hoa',hang)

    def nhap(self, ma, ncc, cac_dong):
        with self.dl.giao_dich():
            nv = self.phien.kiem_quyen('07')
            self.dl.tao_nhap(ma, nv, ncc)
            for hang, sl, gia in cac_dong:
                self.dl.them_dong_nhap(ma, hang, sl, gia)
            self.dl.chot_nhap(ma)

    def moc_dem(self, hang):
        self.phien.kiem_quyen('08')
        ton, moc = self.kho.so_du(hang)
        return ton, moc, luc()

    def gui_kiem(self, ma, cac_dong):
        with self.dl.giao_dich():
            nv = self.phien.kiem_quyen('08')
            self.dl.tao_kiem(ma, nv)
            for hang, (ton, moc, thoi_diem), dem, ly_do in cac_dong:
                self.dl.them_dong_kiem(ma, hang, thoi_diem, ton, moc, dem, ly_do)
            self.dl.gui_phieu_kiem(ma)

    def xet_kiem(self, ma, duyet, ly_do=None):
        with self.dl.giao_dich():
            nv = self.phien.kiem_quyen('09')
            yeu_cau(type(duyet) is bool, 'Quyết định không hợp lệ')
            yeu_cau(self.dl.lay(PhieuKiem,ma).cho_phep_xet(),'Phiếu chưa gửi hoặc đã xét')
            self.dl.ghi_xet_kiem(ma, 'DUYET' if duyet else 'TU_CHOI', nv, ly_do)
