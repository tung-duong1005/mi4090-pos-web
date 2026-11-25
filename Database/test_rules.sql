-- Chạy trong schema POS mới. Toàn bộ dữ liệu kiểm thử được rollback.
BEGIN;
INSERT INTO nhan_vien VALUES ('n','Thu ngân','HOAT_DONG'),('k','Kho','HOAT_DONG'),('q','Quản lý','HOAT_DONG');
INSERT INTO tai_khoan VALUES ('t','n','thu_ngan','fixture','TN','HOAT_DONG');
INSERT INTO hang_hoa VALUES ('s','89','Sữa','180ml','hộp',25000,2,'HOAT_DONG');
INSERT INTO ca_thu_ngan(ma_ca,nguoi_mo,gio_mo,tien_dau,trang_thai) VALUES ('c','n',now(),100000,'MO');
INSERT INTO phieu_ban VALUES ('b','c',now(),'CK',0,'NHAP');
INSERT INTO dong_ban(ma_dong_ban,ma_ban,ma_hang,sl,don_gia,giam) VALUES ('l','b','s',2,25000,0);
UPDATE phieu_ban SET trang_thai='XONG',tien_thu=50000 WHERE ma_ban='b';
INSERT INTO web_yeu_cau VALUES ('t','02','khoa',repeat('a',64),'b',NULL,now());
DO $$
BEGIN
    IF (SELECT ton FROM v_ton WHERE ma_hang='s') <> 0 THEN RAISE EXCEPTION 'Sai tồn sau bán'; END IF;
    BEGIN
        INSERT INTO web_yeu_cau VALUES ('t','02','khoa',repeat('a',64),'b',NULL,now());
        RAISE EXCEPTION 'Khóa trùng được chấp nhận';
    EXCEPTION WHEN unique_violation THEN NULL; END;
    BEGIN
        UPDATE dong_ban SET sl=1 WHERE ma_dong_ban='l';
        RAISE EXCEPTION 'Đã sửa được dòng bán sau khi chốt';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
        INSERT INTO phieu_ban VALUES ('over','c',now(),'TM',0,'NHAP');
        INSERT INTO dong_ban(ma_dong_ban,ma_ban,ma_hang,sl,don_gia,giam) VALUES ('x','over','s',1,25000,0);
        UPDATE phieu_ban SET trang_thai='XONG',tien_thu=25000 WHERE ma_ban='over';
        RAISE EXCEPTION 'Đã chốt vượt tồn';
    EXCEPTION WHEN check_violation THEN NULL; END;
    IF EXISTS (SELECT 1 FROM phieu_ban WHERE ma_ban='over') THEN RAISE EXCEPTION 'Hoàn tác thiếu'; END IF;
END;
$$;
UPDATE hang_hoa SET gia=30000 WHERE ma_hang='s';
INSERT INTO phieu_tra VALUES ('r','c','b',now(),'TM',0,'NHAP');
INSERT INTO dong_tra(ma_dong_tra,ma_tra,ma_dong_ban,sl,tinh_trang)
VALUES ('r1','r','l',1,'TOT'),('r2','r','l',1,'HONG');
UPDATE phieu_tra SET trang_thai='XONG',tien_hoan=50000 WHERE ma_tra='r';
DO $$
BEGIN
    IF (SELECT ton FROM v_ton WHERE ma_hang='s') <> 1 THEN RAISE EXCEPTION 'Sai tồn hàng trả'; END IF;
    BEGIN
        INSERT INTO phieu_tra VALUES ('rr','c','b',now(),'CK',0,'NHAP');
        INSERT INTO dong_tra(ma_dong_tra,ma_tra,ma_dong_ban,sl,tinh_trang) VALUES ('rr1','rr','l',1,'TOT');
        UPDATE phieu_tra SET trang_thai='XONG',tien_hoan=25000 WHERE ma_tra='rr';
        RAISE EXCEPTION 'Trả vượt số lượng';
    EXCEPTION WHEN check_violation THEN NULL; END;
END;
$$;
INSERT INTO phieu_kiem(ma_kiem,nguoi_lap,luc_lap,trang_thai) VALUES ('p','k',now(),'NHAP');
INSERT INTO dong_kiem(ma_kiem,ma_hang,luc_dem,ton_so,moc_so,thuc_dem)
SELECT 'p',ma_hang,now(),ton,moc,0 FROM v_ton WHERE ma_hang='s';
UPDATE phieu_kiem SET trang_thai='CHO',luc_gui=now() WHERE ma_kiem='p';
INSERT INTO phieu_nhap VALUES ('i','k',now(),'NCC','NHAP');
INSERT INTO dong_nhap(ma_dong_nhap,ma_nhap,ma_hang,sl,don_gia) VALUES ('i1','i','s',1,15000);
UPDATE phieu_nhap SET trang_thai='XONG' WHERE ma_nhap='i';
DO $$
BEGIN
    BEGIN
        UPDATE phieu_kiem SET trang_thai='DUYET',luc_xet=now(),nguoi_xet='q' WHERE ma_kiem='p';
        RAISE EXCEPTION 'Duyệt kiểm theo mốc cũ';
    EXCEPTION WHEN check_violation THEN NULL; END;
    IF (SELECT ton FROM v_ton WHERE ma_hang='s') <> 2 THEN RAISE EXCEPTION 'Sai tồn khi nhập'; END IF;
END;
$$;
UPDATE phieu_kiem SET trang_thai='TU_CHOI',luc_xet=now(),nguoi_xet='q',ly_do='Đếm lại' WHERE ma_kiem='p';
ROLLBACK;
