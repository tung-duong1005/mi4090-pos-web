-- Hai tháng, một quầy và một kho. Chạy bởi manage.py seed trong một giao dịch.
-- Tiền tính theo đồng. Các tài khoản mẫu dành cho demo nghiệp vụ.
DO $seed$
DECLARE
  ky integer;
  i integer;
  day0 timestamptz;
  ca text;
  id text;
  hh text;
BEGIN
  PERFORM pos_khoa_ghi();
  IF EXISTS (SELECT 1 FROM nhan_vien) OR EXISTS (SELECT 1 FROM hang_hoa) THEN
    RAISE EXCEPTION 'Chỉ nạp seed trên database demo trống. Dữ liệu hiện có được giữ nguyên.';
  END IF;
  INSERT INTO nhan_vien SELECT vai, 'Demo ' || vai, 'HOAT_DONG'
    FROM unnest(ARRAY['TN','KHO','QL','QT']) AS r(vai);
  INSERT INTO tai_khoan SELECT ma_nv, ma_nv, lower(ma_nv), 'demo-disabled', ma_nv, 'HOAT_DONG' FROM nhan_vien;
  INSERT INTO hang_hoa VALUES
    ('S','89001','Sữa','180 ml','hộp',25000,100,'HOAT_DONG'),
    ('B','89002','Bánh','100 g','gói',18000,100,'HOAT_DONG');
  FOR ky IN 1..2 LOOP
    day0 := make_timestamptz(2026, ky, 15, 8, 0, 0, 'Asia/Ho_Chi_Minh');
    ca := 'CA' || ky;
    INSERT INTO ca_thu_ngan(ma_ca,nguoi_mo,gio_mo,tien_dau,trang_thai)
      VALUES(ca,'TN',day0,100000,'MO');
    INSERT INTO phieu_nhap VALUES('N'||ky,'KHO',day0,'NCC demo','NHAP');
    INSERT INTO dong_nhap(ma_dong_nhap,ma_nhap,ma_hang,sl,don_gia)
      VALUES('DN'||ky,'N'||ky,'S',10,15000);
    UPDATE phieu_nhap SET trang_thai='XONG' WHERE ma_nhap='N'||ky;
    FOR i IN 1..12 LOOP
      id := 'PB'||ky||'-'||i;
      INSERT INTO phieu_ban VALUES (id,ca,day0+i*interval '10 minutes',
        CASE WHEN i%2=1 THEN 'TM' ELSE 'CK' END,0,'NHAP');
      FOREACH hh IN ARRAY ARRAY['S','B'] LOOP
        INSERT INTO dong_ban(ma_dong_ban,ma_ban,ma_hang,sl,don_gia,giam)
          SELECT id||hh,id,ma_hang,1,gia,0 FROM hang_hoa WHERE ma_hang=hh;
      END LOOP;
      IF i=12 THEN
        UPDATE phieu_ban SET trang_thai='HUY' WHERE ma_ban=id;
      ELSE
        UPDATE phieu_ban SET trang_thai='XONG',tien_thu=43000 WHERE ma_ban=id;
        INSERT INTO nhat_ky VALUES('LOG'||id,'TN',day0+i*interval '10 minutes','02','phieu_ban',id,'THANH_CONG');
      END IF;
    END LOOP;
    INSERT INTO phieu_tra VALUES('T'||ky,ca,'PB'||ky||'-1',day0+interval '3 hours','TM',0,'NHAP');
    INSERT INTO dong_tra(ma_dong_tra,ma_tra,ma_dong_ban,sl,tinh_trang)
      VALUES('DT'||ky,'T'||ky,'PB'||ky||'-1S',1,'TOT');
    UPDATE phieu_tra SET tien_hoan=25000,trang_thai='XONG' WHERE ma_tra='T'||ky;
    INSERT INTO thu_chi_khac VALUES('CHI'||ky,ca,day0+interval '4 hours','CHI',10000,'Mua giấy in','XONG');
    INSERT INTO phieu_kiem(ma_kiem,nguoi_lap,luc_lap,trang_thai) VALUES('K'||ky,'KHO',day0+interval '5 hours','NHAP');
    INSERT INTO dong_kiem(ma_kiem,ma_hang,luc_dem,ton_so,moc_so,thuc_dem)
      SELECT 'K'||ky,ma_hang,day0+interval '5 hours',ton,moc,ton FROM v_ton;
    UPDATE phieu_kiem SET trang_thai='CHO',luc_gui=day0+interval '6 hours' WHERE ma_kiem='K'||ky;
    UPDATE phieu_kiem SET trang_thai='DUYET',nguoi_xet='QL',luc_xet=day0+interval '7 hours' WHERE ma_kiem='K'||ky;
    UPDATE ca_thu_ngan SET du_kien=323000,thuc_dem=323000,trang_thai='BAN_GIAO' WHERE ma_ca=ca;
    UPDATE ca_thu_ngan SET trang_thai='DONG',nguoi_chot='QL',gio_dong=day0+interval '8 hours' WHERE ma_ca=ca;
  END LOOP;
END;
$seed$;
