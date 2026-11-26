-- PostgreSQL 16+. Tiền tính theo đồng. Thứ tự dòng dùng khi in lại phiếu.
CREATE TABLE nhan_vien (
  ma_nv TEXT PRIMARY KEY NOT NULL,
  ho_ten TEXT NOT NULL CHECK(length(trim(ho_ten))>0),
  trang_thai TEXT NOT NULL CHECK(trang_thai IN ('HOAT_DONG','NGUNG'))
);

CREATE TABLE tai_khoan (
  ma_tk TEXT PRIMARY KEY NOT NULL,
  ma_nv TEXT NOT NULL REFERENCES nhan_vien(ma_nv) ON DELETE RESTRICT,
  ten_dn TEXT NOT NULL CHECK(length(trim(ten_dn))>0),
  mat_khau_bam TEXT NOT NULL CHECK(length(trim(mat_khau_bam))>0),
  vai_tro TEXT NOT NULL CHECK(vai_tro IN ('TN','KHO','QL','QT')),
  trang_thai TEXT NOT NULL CHECK(trang_thai IN ('HOAT_DONG','NGUNG')),
  UNIQUE(ma_nv),
  UNIQUE(ten_dn)
);

CREATE TABLE nhat_ky (
  ma_log TEXT PRIMARY KEY NOT NULL,
  ma_tk TEXT NOT NULL REFERENCES tai_khoan(ma_tk) ON DELETE RESTRICT,
  thoi_diem TIMESTAMPTZ NOT NULL,
  thao_tac TEXT NOT NULL CHECK(length(trim(thao_tac))>0),
  loai_dt TEXT NOT NULL CHECK(length(trim(loai_dt))>0),
  ma_dt TEXT NOT NULL CHECK(length(trim(ma_dt))>0),
  ket_qua TEXT NOT NULL CHECK(length(trim(ket_qua))>0)
);

CREATE TABLE hang_hoa (
  ma_hang TEXT PRIMARY KEY NOT NULL,
  ma_vach TEXT UNIQUE NOT NULL,
  ten TEXT NOT NULL CHECK(length(trim(ten))>0),
  quy_cach TEXT NOT NULL CHECK(length(trim(quy_cach))>0),
  don_vi TEXT NOT NULL CHECK(length(trim(don_vi))>0),
  gia BIGINT NOT NULL CHECK(gia>=0),
  ton_dau BIGINT NOT NULL CHECK(ton_dau>=0),
  trang_thai TEXT NOT NULL CHECK(trang_thai IN ('HOAT_DONG','NGUNG'))
);

CREATE TABLE ca_thu_ngan (
  ma_ca TEXT PRIMARY KEY NOT NULL,
  nguoi_mo TEXT NOT NULL REFERENCES nhan_vien(ma_nv) ON DELETE RESTRICT,
  nguoi_chot TEXT REFERENCES nhan_vien(ma_nv) ON DELETE RESTRICT,
  gio_mo TIMESTAMPTZ NOT NULL,
  gio_dong TIMESTAMPTZ,
  tien_dau BIGINT NOT NULL CHECK(tien_dau>=0),
  du_kien BIGINT,
  thuc_dem BIGINT CHECK(thuc_dem>=0),
  giai_trinh TEXT,
  trang_thai TEXT NOT NULL CHECK(trang_thai IN ('MO','BAN_GIAO','DONG')),
  CHECK ((trang_thai='MO' AND du_kien IS NULL AND thuc_dem IS NULL) OR (trang_thai<>'MO' AND du_kien IS NOT NULL AND thuc_dem IS NOT NULL AND (du_kien=thuc_dem OR length(trim(coalesce(giai_trinh,'')))>0))),
  CHECK ((trang_thai='DONG')=(gio_dong IS NOT NULL) AND (trang_thai='DONG')=(nguoi_chot IS NOT NULL))
);

CREATE UNIQUE INDEX uq_ca_mo_nguoi ON ca_thu_ngan(nguoi_mo) WHERE trang_thai='MO';

CREATE TABLE phieu_ban (
  ma_ban TEXT PRIMARY KEY NOT NULL,
  ma_ca TEXT NOT NULL REFERENCES ca_thu_ngan(ma_ca) ON DELETE RESTRICT,
  thoi_diem TIMESTAMPTZ NOT NULL,
  pt_thu TEXT NOT NULL CHECK(pt_thu IN ('TM','CK')),
  tien_thu BIGINT NOT NULL CHECK(tien_thu>=0),
  trang_thai TEXT NOT NULL CHECK(trang_thai IN ('NHAP','XONG','HUY'))
);

CREATE TABLE dong_ban (
  ma_dong_ban TEXT PRIMARY KEY NOT NULL,
  ma_ban TEXT NOT NULL REFERENCES phieu_ban(ma_ban) ON DELETE RESTRICT,
  ma_hang TEXT NOT NULL REFERENCES hang_hoa(ma_hang) ON DELETE RESTRICT,
  sl BIGINT NOT NULL CHECK(sl>=1),
  don_gia BIGINT NOT NULL CHECK(don_gia>=0),
  giam BIGINT NOT NULL CHECK(giam>=0),
  CHECK(giam<=don_gia),
  thu_tu BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE
);

CREATE TABLE phieu_tra (
  ma_tra TEXT PRIMARY KEY NOT NULL,
  ma_ca TEXT NOT NULL REFERENCES ca_thu_ngan(ma_ca) ON DELETE RESTRICT,
  ma_ban TEXT NOT NULL REFERENCES phieu_ban(ma_ban) ON DELETE RESTRICT,
  thoi_diem TIMESTAMPTZ NOT NULL,
  pt_hoan TEXT NOT NULL CHECK(pt_hoan IN ('TM','CK')),
  tien_hoan BIGINT NOT NULL CHECK(tien_hoan>=0),
  trang_thai TEXT NOT NULL CHECK(trang_thai IN ('NHAP','XONG','HUY'))
);

CREATE TABLE dong_tra (
  ma_dong_tra TEXT PRIMARY KEY NOT NULL,
  ma_tra TEXT NOT NULL REFERENCES phieu_tra(ma_tra) ON DELETE RESTRICT,
  ma_dong_ban TEXT NOT NULL REFERENCES dong_ban(ma_dong_ban) ON DELETE RESTRICT,
  sl BIGINT NOT NULL CHECK(sl>=1),
  tinh_trang TEXT NOT NULL CHECK(tinh_trang IN ('TOT','HONG')),
  thu_tu BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE
);

CREATE TABLE thu_chi_khac (
  ma_tc TEXT PRIMARY KEY NOT NULL,
  ma_ca TEXT NOT NULL REFERENCES ca_thu_ngan(ma_ca) ON DELETE RESTRICT,
  thoi_diem TIMESTAMPTZ NOT NULL,
  loai TEXT NOT NULL CHECK(loai IN ('THU','CHI')),
  so_tien BIGINT NOT NULL CHECK(so_tien>=1),
  ly_do TEXT NOT NULL CHECK(length(trim(ly_do))>0),
  trang_thai TEXT NOT NULL CHECK(trang_thai IN ('NHAP','XONG','HUY'))
);

CREATE TABLE phieu_nhap (
  ma_nhap TEXT PRIMARY KEY NOT NULL,
  nguoi_lap TEXT NOT NULL REFERENCES nhan_vien(ma_nv) ON DELETE RESTRICT,
  thoi_diem TIMESTAMPTZ NOT NULL,
  nha_cung_cap TEXT NOT NULL CHECK(length(trim(nha_cung_cap))>0),
  trang_thai TEXT NOT NULL CHECK(trang_thai IN ('NHAP','XONG','HUY'))
);

CREATE TABLE dong_nhap (
  ma_dong_nhap TEXT PRIMARY KEY NOT NULL,
  ma_nhap TEXT NOT NULL REFERENCES phieu_nhap(ma_nhap) ON DELETE RESTRICT,
  ma_hang TEXT NOT NULL REFERENCES hang_hoa(ma_hang) ON DELETE RESTRICT,
  sl BIGINT NOT NULL CHECK(sl>=1),
  don_gia BIGINT NOT NULL CHECK(don_gia>=0),
  thu_tu BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE
);

CREATE TABLE phieu_kiem (
  ma_kiem TEXT PRIMARY KEY NOT NULL,
  nguoi_lap TEXT NOT NULL REFERENCES nhan_vien(ma_nv) ON DELETE RESTRICT,
  nguoi_xet TEXT REFERENCES nhan_vien(ma_nv) ON DELETE RESTRICT,
  luc_lap TIMESTAMPTZ NOT NULL,
  luc_gui TIMESTAMPTZ,
  luc_xet TIMESTAMPTZ,
  trang_thai TEXT NOT NULL CHECK(trang_thai IN ('NHAP','CHO','DUYET','TU_CHOI')),
  ly_do TEXT,
  CHECK ((trang_thai='NHAP')=(luc_gui IS NULL)),
  CHECK ((trang_thai IN ('DUYET','TU_CHOI'))=(nguoi_xet IS NOT NULL) AND (nguoi_xet IS NULL)=(luc_xet IS NULL)),
  CHECK (trang_thai<>'TU_CHOI' OR length(trim(coalesce(ly_do,'')))>0)
);

CREATE TABLE dong_kiem (
  ma_kiem TEXT NOT NULL REFERENCES phieu_kiem(ma_kiem) ON DELETE RESTRICT,
  ma_hang TEXT NOT NULL REFERENCES hang_hoa(ma_hang) ON DELETE RESTRICT,
  luc_dem TIMESTAMPTZ NOT NULL,
  ton_so BIGINT NOT NULL CHECK(ton_so>=0),
  moc_so BIGINT NOT NULL CHECK(moc_so>=0),
  thuc_dem BIGINT CHECK(thuc_dem>=0),
  giai_trinh TEXT,
  PRIMARY KEY(ma_kiem,ma_hang),
  thu_tu BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE
);
CREATE UNIQUE INDEX mot_ca_tai_quay ON ca_thu_ngan((1)) WHERE trang_thai IN ('MO','BAN_GIAO');
CREATE VIEW v_dong_tra AS
 SELECT t.*, t.sl*(b.don_gia-b.giam) AS tien_dong, b.ma_hang
 FROM dong_tra t JOIN dong_ban b USING(ma_dong_ban);
CREATE VIEW v_bien_dong AS
 SELECT d.ma_hang, 'BAN' AS loai,p.ma_ban AS chung_tu,p.thoi_diem AS luc,-d.sl AS bien_dong
 FROM dong_ban d JOIN phieu_ban p USING(ma_ban) WHERE p.trang_thai='XONG'
 UNION ALL SELECT d.ma_hang,'TRA',p.ma_tra,p.thoi_diem,d.sl FROM v_dong_tra d JOIN phieu_tra p USING(ma_tra) WHERE p.trang_thai='XONG' AND d.tinh_trang='TOT'
 UNION ALL SELECT d.ma_hang,'NHAP',p.ma_nhap,p.thoi_diem,d.sl FROM dong_nhap d JOIN phieu_nhap p USING(ma_nhap) WHERE p.trang_thai='XONG'
 UNION ALL SELECT d.ma_hang,'KIEM',p.ma_kiem,p.luc_xet,d.thuc_dem-d.ton_so FROM dong_kiem d JOIN phieu_kiem p USING(ma_kiem) WHERE p.trang_thai='DUYET' AND d.thuc_dem<>d.ton_so;
CREATE VIEW v_ton AS
 SELECT h.ma_hang,h.ton_dau+coalesce(sum(b.bien_dong),0)::bigint AS ton,count(b.chung_tu) AS moc
 FROM hang_hoa h LEFT JOIN v_bien_dong b USING(ma_hang) GROUP BY h.ma_hang;
CREATE INDEX ix_nhat_ky_ma_tk ON nhat_ky(ma_tk);
CREATE INDEX ix_ca_thu_ngan_nguoi_mo ON ca_thu_ngan(nguoi_mo);
CREATE INDEX ix_ca_thu_ngan_nguoi_chot ON ca_thu_ngan(nguoi_chot);
CREATE INDEX ix_phieu_ban_ma_ca ON phieu_ban(ma_ca);
CREATE INDEX ix_dong_ban_ma_ban ON dong_ban(ma_ban);
CREATE INDEX ix_dong_ban_ma_hang ON dong_ban(ma_hang);
CREATE INDEX ix_phieu_tra_ma_ca ON phieu_tra(ma_ca);
CREATE INDEX ix_phieu_tra_ma_ban ON phieu_tra(ma_ban);
CREATE INDEX ix_dong_tra_ma_tra ON dong_tra(ma_tra);
CREATE INDEX ix_dong_tra_ma_dong_ban ON dong_tra(ma_dong_ban);
CREATE INDEX ix_thu_chi_khac_ma_ca ON thu_chi_khac(ma_ca);
CREATE INDEX ix_phieu_nhap_nguoi_lap ON phieu_nhap(nguoi_lap);
CREATE INDEX ix_dong_nhap_ma_nhap ON dong_nhap(ma_nhap);
CREATE INDEX ix_dong_nhap_ma_hang ON dong_nhap(ma_hang);
CREATE INDEX ix_phieu_kiem_nguoi_lap ON phieu_kiem(nguoi_lap);
CREATE INDEX ix_phieu_kiem_nguoi_xet ON phieu_kiem(nguoi_xet);
CREATE INDEX ix_dong_kiem_ma_hang ON dong_kiem(ma_hang);

CREATE TABLE web_yeu_cau (
    ma_tk TEXT NOT NULL REFERENCES tai_khoan(ma_tk) ON DELETE RESTRICT,
    nghiep_vu TEXT NOT NULL CHECK(nghiep_vu IN ('02','03')),
    khoa TEXT NOT NULL CHECK(length(khoa) BETWEEN 1 AND 128),
    bam_noi_dung TEXT NOT NULL CHECK(length(bam_noi_dung)=64),
    ma_ban TEXT REFERENCES phieu_ban(ma_ban) ON DELETE RESTRICT,
    ma_tra TEXT REFERENCES phieu_tra(ma_tra) ON DELETE RESTRICT,
    thoi_diem TIMESTAMPTZ NOT NULL,
    PRIMARY KEY(ma_tk,nghiep_vu,khoa),
    UNIQUE(ma_ban),
    UNIQUE(ma_tra),
    CHECK((nghiep_vu='02' AND ma_ban IS NOT NULL AND ma_tra IS NULL)
       OR (nghiep_vu='03' AND ma_ban IS NULL AND ma_tra IS NOT NULL))
);
CREATE INDEX ix_web_ban_ngay ON phieu_ban(thoi_diem, ma_ban) WHERE trang_thai='XONG';
CREATE INDEX ix_web_tra_ngay ON phieu_tra(thoi_diem, ma_tra) WHERE trang_thai='XONG';
