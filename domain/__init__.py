"""Các lớp miền của POS. Đơn giá, tiền thu và tiền hoàn tính bằng đồng."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace

class ChungTuQuy(ABC):
    """Hợp đồng tính tác động tiền mặt của một chứng từ."""
    @abstractmethod
    def tac_dong_quy(self) -> int:
        ...

@dataclass(frozen=True)
class NhanVien:
    ma_nv: str
    ho_ten: str
    trang_thai: str


@dataclass(frozen=True)
class TaiKhoan:
    ma_tk: str
    ma_nv: str
    ten_dn: str
    mat_khau_bam: str
    vai_tro: str
    trang_thai: str

    def kiem_tra_quyen(self, vai):
        if self.trang_thai != 'HOAT_DONG' or self.vai_tro not in vai:
            raise PermissionError('Tài khoản không có quyền thao tác')


@dataclass(frozen=True)
class NhatKy:
    ma_log: str
    ma_tk: str
    thoi_diem: str
    thao_tac: str
    loai_dt: str
    ma_dt: str
    ket_qua: str


@dataclass(frozen=True)
class HangHoa:
    ma_hang: str
    ma_vach: str
    ten: str
    quy_cach: str
    don_vi: str
    gia: int
    ton_dau: int
    trang_thai: str

    def gia_sau_cap_nhat(self, moi):
        if type(moi) is not int or moi < 0:
            raise ValueError("Giá phải là số nguyên đồng không âm")
        return replace(self, gia=moi)


@dataclass(frozen=True)
class CaThuNgan:
    ma_ca: str
    nguoi_mo: str
    nguoi_chot: str | None
    gio_mo: str
    gio_dong: str | None
    tien_dau: int
    du_kien: int | None
    thuc_dem: int | None
    giai_trinh: str | None
    trang_thai: str

    def kiem_tra_ca_mo(self, nguoi):
        if self.trang_thai != 'MO' or self.nguoi_mo != nguoi:
            raise ValueError('Phải dùng ca đang mở của thu ngân')


@dataclass(frozen=True)
class PhieuBan(ChungTuQuy):
    ma_ban: str
    ma_ca: str
    thoi_diem: str
    pt_thu: str
    tien_thu: int
    trang_thai: str
    dong: tuple[DongBan, ...] = ()

    def tinh_tong(self):
        return sum(d.thanh_tien() for d in self.dong)

    def tac_dong_quy(self):
        return self.tien_thu if self.pt_thu == 'TM' and self.trang_thai == 'XONG' else 0


@dataclass(frozen=True)
class DongBan:
    ma_dong_ban: str
    ma_ban: str
    ma_hang: str
    sl: int
    don_gia: int
    giam: int

    def thanh_tien(self):
        return self.sl * (self.don_gia - self.giam)

    def luong_con_tra(self, da_tra):
        return self.sl - da_tra


@dataclass(frozen=True)
class PhieuTra(ChungTuQuy):
    ma_tra: str
    ma_ca: str
    ma_ban: str
    thoi_diem: str
    pt_hoan: str
    tien_hoan: int
    trang_thai: str
    dong: tuple[DongTra, ...] = ()

    def tac_dong_quy(self):
        return -self.tien_hoan if self.pt_hoan == 'TM' and self.trang_thai == 'XONG' else 0


@dataclass(frozen=True)
class DongTra:
    ma_dong_tra: str
    ma_tra: str
    ma_dong_ban: str
    sl: int
    tinh_trang: str

    def luong_nhap_lai(self):
        return self.sl if self.tinh_trang == 'TOT' else 0


@dataclass(frozen=True)
class ThuChiKhac(ChungTuQuy):
    ma_tc: str
    ma_ca: str
    thoi_diem: str
    loai: str
    so_tien: int
    ly_do: str
    trang_thai: str

    def tac_dong_quy(self):
        if self.trang_thai != 'XONG':
            return 0
        return self.so_tien if self.loai == 'THU' else -self.so_tien


@dataclass(frozen=True)
class PhieuNhap:
    ma_nhap: str
    nguoi_lap: str
    thoi_diem: str
    nha_cung_cap: str
    trang_thai: str
    dong: tuple[DongNhap, ...] = ()

    def gia_tri_nhap(self):
        return sum(d.thanh_tien() for d in self.dong)


@dataclass(frozen=True)
class DongNhap:
    ma_dong_nhap: str
    ma_nhap: str
    ma_hang: str
    sl: int
    don_gia: int

    def thanh_tien(self):
        return self.sl * self.don_gia


@dataclass(frozen=True)
class PhieuKiem:
    ma_kiem: str
    nguoi_lap: str
    nguoi_xet: str | None
    luc_lap: str
    luc_gui: str | None
    luc_xet: str | None
    trang_thai: str
    ly_do: str | None
    dong: tuple[DongKiem, ...] = ()

    def cho_phep_xet(self):
        return self.trang_thai == 'CHO'


@dataclass(frozen=True)
class DongKiem:
    ma_kiem: str
    ma_hang: str
    luc_dem: str
    ton_so: int
    moc_so: int
    thuc_dem: int | None
    giai_trinh: str | None

    def chenh_lech(self):
        if self.thuc_dem is None:
            raise ValueError('Chưa đếm')
        return self.thuc_dem - self.ton_so


@dataclass(frozen=True)
class BaoCaoCa:
    ca: CaThuNgan
    chung_tu: tuple[ChungTuQuy, ...]

    def tien_du_kien(self):
        return self.ca.tien_dau + sum(ct.tac_dong_quy() for ct in self.chung_tu)
