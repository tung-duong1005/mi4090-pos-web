from domain import NhanVien, TaiKhoan
from application.ports import IPosStore

QUYEN = {
    '01': {'TN'}, '02': {'TN'}, '03': {'TN'}, '04': {'TN'}, '05a': {'TN'}, '05b': {'QL'},
    '06': {'QL'}, '07': {'KHO'}, '08': {'KHO'}, '09': {'QL'}, '10': {'QT'},
    '11': {'QL'}, '12': {'TN','QL'}, '13': {'KHO','QL'}, '14': {'KHO','QL'},
    '15': {'QL'}, '16': {'QT'}, '17': {'QT'}, '18': {'QL'}, '19': {'QL'}
}

class PhienPOS:
    def __init__(self, du_lieu: IPosStore, ma_tk: str):
        self.du_lieu = du_lieu
        self.ma_tk = ma_tk  # lấy từ thành phần đăng nhập

    def kiem_quyen(self, uc):
        tk = self.du_lieu.lay(TaiKhoan, self.ma_tk)
        tk.kiem_tra_quyen(QUYEN.get(uc, set()))
        nv = self.du_lieu.lay(NhanVien, tk.ma_nv)
        if nv.trang_thai != 'HOAT_DONG':
            raise PermissionError('Nhân viên đã ngừng hoạt động')
        return nv.ma_nv
