from domain import BaoCaoCa, CaThuNgan, DongBan, PhieuBan, TaiKhoan
from application.ports import ITonKho
from application.phien import PhienPOS
from domain.common import luc, yeu_cau

class CaDaMo(ValueError):
    def __init__(self, ca):
        super().__init__('Thu ngân đã có ca đang mở.' if ca else 'Quầy đang có ca mở hoặc chờ bàn giao.')
        self.ca = ca


class QuayService:
    def __init__(self, phien: PhienPOS, kho: ITonKho):
        self.phien = phien
        self.kho = kho
        self.dl = phien.du_lieu

    def _ca_cua_thu_ngan(self, nv):
        ca = self.dl.ca_tai_quay()
        if ca and (ca['nguoi_mo'] != nv or ca['trang_thai'] != 'MO'):
            raise CaDaMo(None)
        return ca

    def mo_ca(self, ma, dau):
        with self.dl.giao_dich():
            nv = self.phien.kiem_quyen('01')
            yeu_cau(type(dau) is int and 0 <= dau <= 2**63 - 1,
                    'Tiền đầu ca phải là số nguyên không âm trong phạm vi BIGINT.')
            hien_tai = self._ca_cua_thu_ngan(nv)
            if hien_tai:
                raise CaDaMo(hien_tai)
            self.dl.tao_ca(ma, nv, dau)
            return self._ca_cua_thu_ngan(nv)

    def ca_dang_mo(self):
        with self.dl.giao_dich(chi_doc=True):
            return self._ca_cua_thu_ngan(self.phien.kiem_quyen('01'))

    def ban(self, ma, ca, pt, cac_dong):
        with self.dl.giao_dich():
            nv = self.phien.kiem_quyen('02')
            self.dl.lay(CaThuNgan, ca).kiem_tra_ca_mo(nv)
            self.dl.tao_ban_nhap(ma, ca, pt)
            for hang, sl, giam in cac_dong:
                h = self.kho.hang_ban(hang)
                yeu_cau(sl <= self.kho.so_du(hang)[0], 'Không đủ hàng')
                self.dl.them_dong_ban(ma, hang, sl, h.gia, giam)
            phieu = self.dl.lay(PhieuBan, ma)
            self.dl.chot_ban(ma, phieu.tinh_tong())
            self.dl.ghi_nhat_ky(self.phien.ma_tk,'02','phieu_ban',ma)
        return ma

    def tra(self, ma, ca, goc, pt, cac_dong):
        with self.dl.giao_dich():
            nv = self.phien.kiem_quyen('03')
            self.dl.lay(CaThuNgan, ca).kiem_tra_ca_mo(nv)
            self.dl.tao_tra_nhap(ma, ca, goc, pt)
            tong = 0
            for ma_dong, sl, tinh_trang in cac_dong:
                ban = self.dl.lay(DongBan, ma_dong)
                yeu_cau(ban.ma_ban == goc, 'Sai phiếu gốc')
                da_tra = self.dl.tong_da_tra(ma_dong, ma)
                yeu_cau(sl <= ban.luong_con_tra(da_tra), 'Vượt lượng còn trả')
                self.dl.them_dong_tra(ma, ma_dong, sl, tinh_trang)
                tong += sl*(ban.don_gia-ban.giam)
            self.dl.chot_tra(ma, tong)
            self.dl.ghi_nhat_ky(self.phien.ma_tk,'03','phieu_tra',ma)
        return ma

    def thu_chi(self, ma, ca, loai, tien, ly_do):
        with self.dl.giao_dich():
            nv = self.phien.kiem_quyen('04')
            self.dl.lay(CaThuNgan, ca).kiem_tra_ca_mo(nv)
            self.dl.ghi_thu_chi(ma, ca, loai, tien, ly_do)

    def bao_cao_ca(self, ma):
        with self.dl.giao_dich(chi_doc=True):
            nv = self.phien.kiem_quyen('12')
            ca = self.dl.lay(CaThuNgan, ma)
            if self.dl.lay(TaiKhoan,self.phien.ma_tk).vai_tro == 'TN' and nv != ca.nguoi_mo:
                raise PermissionError('Chỉ xem ca của mình')
            return BaoCaoCa(ca,self.dl.chung_tu_ca(ma))

    def ban_giao(self, ma, dem, giai_trinh=None):
        with self.dl.giao_dich():
            nv = self.phien.kiem_quyen('05a')
            self.dl.lay(CaThuNgan,ma).kiem_tra_ca_mo(nv)
            quy = self.bao_cao_ca(ma).tien_du_kien()
            self.dl.ghi_ban_giao(ma, quy, dem, giai_trinh)

    def chot_ca(self, ma):
        with self.dl.giao_dich():
            nv = self.phien.kiem_quyen('05b')
            r = self.dl.ghi_chot_ca(ma, nv)
            yeu_cau(r == 1,'Ca chưa bàn giao')
