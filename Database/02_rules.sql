-- Giao dịch ghi của cửa hàng một quầy được tuần tự hóa. Khóa tự nhả khi commit/rollback.
CREATE FUNCTION pos_khoa_ghi() RETURNS void LANGUAGE plpgsql VOLATILE AS $$
BEGIN
    IF current_setting('transaction_isolation') <> 'read committed' THEN
        RAISE EXCEPTION 'POS requires READ COMMITTED for writes' USING ERRCODE = '25000';
    END IF;
    PERFORM pg_advisory_xact_lock(41702, 4301);
END;
$$;

CREATE FUNCTION pos_truoc_khi_ghi() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    PERFORM pos_khoa_ghi();
    RETURN NULL;
END;
$$;

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON nhan_vien
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON tai_khoan
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON nhat_ky
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON hang_hoa
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON ca_thu_ngan
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON phieu_ban
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON dong_ban
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON phieu_tra
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON dong_tra
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON thu_chi_khac
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON phieu_nhap
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON dong_nhap
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON phieu_kiem
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON dong_kiem
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE TRIGGER pos_khoa_ghi BEFORE INSERT OR UPDATE OR DELETE ON web_yeu_cau
FOR EACH STATEMENT EXECUTE FUNCTION pos_truoc_khi_ghi();

CREATE FUNCTION phieu_ban_insert() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- start_phieu_ban
    IF NEW.trang_thai<>'NHAP' THEN
        RAISE EXCEPTION 'draft required' USING ERRCODE = '23514';
    END IF;
    -- open_phieu_ban_INSERT
    IF NEW.trang_thai='XONG' AND (SELECT trang_thai FROM ca_thu_ngan WHERE ma_ca=NEW.ma_ca)<>'MO' THEN
        RAISE EXCEPTION 'shift closed' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_ban_insert BEFORE INSERT ON phieu_ban
FOR EACH ROW EXECUTE FUNCTION phieu_ban_insert();

CREATE FUNCTION phieu_ban_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- transition_phieu_ban
    IF NOT (OLD.trang_thai='NHAP' AND NEW.trang_thai IN ('NHAP','HUY','XONG')) THEN
        RAISE EXCEPTION 'invalid transition or immutable document' USING ERRCODE = '23514';
    END IF;
    -- open_phieu_ban_UPDATE
    IF NEW.trang_thai='XONG' AND (SELECT trang_thai FROM ca_thu_ngan WHERE ma_ca=NEW.ma_ca)<>'MO' THEN
        RAISE EXCEPTION 'shift closed' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_ban_update BEFORE UPDATE ON phieu_ban
FOR EACH ROW EXECUTE FUNCTION phieu_ban_update();

CREATE FUNCTION phieu_ban_delete() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- keep_phieu_ban
    IF OLD.trang_thai<>'NHAP' THEN
        RAISE EXCEPTION 'preserve posted document' USING ERRCODE = '23514';
    END IF;
    RETURN OLD;
END;
$$;
CREATE TRIGGER phieu_ban_delete BEFORE DELETE ON phieu_ban
FOR EACH ROW EXECUTE FUNCTION phieu_ban_delete();

CREATE FUNCTION phieu_ban_update_of_trang_thai() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- lines_phieu_ban
    IF NEW.trang_thai='XONG' AND NOT EXISTS(SELECT 1 FROM dong_ban WHERE ma_ban=OLD.ma_ban) THEN
        RAISE EXCEPTION 'empty document' USING ERRCODE = '23514';
    END IF;
    -- sale_total
    IF NEW.trang_thai='XONG' AND
 (NEW.tien_thu<>(SELECT sum(sl*(don_gia-giam)) FROM dong_ban WHERE ma_ban=NEW.ma_ban)
 OR EXISTS(SELECT d.ma_hang FROM dong_ban d JOIN v_ton v USING(ma_hang) WHERE d.ma_ban=NEW.ma_ban GROUP BY d.ma_hang HAVING sum(d.sl)>max(v.ton))) THEN
        RAISE EXCEPTION 'invalid sale or insufficient stock' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_ban_update_of_trang_thai BEFORE UPDATE OF trang_thai ON phieu_ban
FOR EACH ROW EXECUTE FUNCTION phieu_ban_update_of_trang_thai();

CREATE FUNCTION dong_ban_insert() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_insert_dong_ban
    IF (SELECT trang_thai FROM phieu_ban WHERE ma_ban=NEW.ma_ban)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER dong_ban_insert BEFORE INSERT ON dong_ban
FOR EACH ROW EXECUTE FUNCTION dong_ban_insert();

CREATE FUNCTION dong_ban_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_update_dong_ban
    IF (SELECT trang_thai FROM phieu_ban WHERE ma_ban=OLD.ma_ban)<>'NHAP' OR (SELECT trang_thai FROM phieu_ban WHERE ma_ban=NEW.ma_ban)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER dong_ban_update BEFORE UPDATE ON dong_ban
FOR EACH ROW EXECUTE FUNCTION dong_ban_update();

CREATE FUNCTION dong_ban_delete() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_delete_dong_ban
    IF (SELECT trang_thai FROM phieu_ban WHERE ma_ban=OLD.ma_ban)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN OLD;
END;
$$;
CREATE TRIGGER dong_ban_delete BEFORE DELETE ON dong_ban
FOR EACH ROW EXECUTE FUNCTION dong_ban_delete();

CREATE FUNCTION phieu_tra_insert() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- start_phieu_tra
    IF NEW.trang_thai<>'NHAP' THEN
        RAISE EXCEPTION 'draft required' USING ERRCODE = '23514';
    END IF;
    -- open_phieu_tra_INSERT
    IF NEW.trang_thai='XONG' AND (SELECT trang_thai FROM ca_thu_ngan WHERE ma_ca=NEW.ma_ca)<>'MO' THEN
        RAISE EXCEPTION 'shift closed' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_tra_insert BEFORE INSERT ON phieu_tra
FOR EACH ROW EXECUTE FUNCTION phieu_tra_insert();

CREATE FUNCTION phieu_tra_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- transition_phieu_tra
    IF NOT (OLD.trang_thai='NHAP' AND NEW.trang_thai IN ('NHAP','HUY','XONG')) THEN
        RAISE EXCEPTION 'invalid transition or immutable document' USING ERRCODE = '23514';
    END IF;
    -- open_phieu_tra_UPDATE
    IF NEW.trang_thai='XONG' AND (SELECT trang_thai FROM ca_thu_ngan WHERE ma_ca=NEW.ma_ca)<>'MO' THEN
        RAISE EXCEPTION 'shift closed' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_tra_update BEFORE UPDATE ON phieu_tra
FOR EACH ROW EXECUTE FUNCTION phieu_tra_update();

CREATE FUNCTION phieu_tra_delete() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- keep_phieu_tra
    IF OLD.trang_thai<>'NHAP' THEN
        RAISE EXCEPTION 'preserve posted document' USING ERRCODE = '23514';
    END IF;
    RETURN OLD;
END;
$$;
CREATE TRIGGER phieu_tra_delete BEFORE DELETE ON phieu_tra
FOR EACH ROW EXECUTE FUNCTION phieu_tra_delete();

CREATE FUNCTION phieu_tra_update_of_trang_thai() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- lines_phieu_tra
    IF NEW.trang_thai='XONG' AND NOT EXISTS(SELECT 1 FROM dong_tra WHERE ma_tra=OLD.ma_tra) THEN
        RAISE EXCEPTION 'empty document' USING ERRCODE = '23514';
    END IF;
    -- return_checks
    IF NEW.trang_thai='XONG' AND (
 (SELECT trang_thai FROM phieu_ban WHERE ma_ban=NEW.ma_ban)<>'XONG'
 OR NEW.tien_hoan<>(SELECT sum(tien_dong) FROM v_dong_tra WHERE ma_tra=NEW.ma_tra)
 OR EXISTS(SELECT 1 FROM dong_tra t JOIN dong_ban b USING(ma_dong_ban) WHERE t.ma_tra=NEW.ma_tra AND b.ma_ban<>NEW.ma_ban)
 OR EXISTS(SELECT b.ma_dong_ban FROM dong_tra t JOIN dong_ban b USING(ma_dong_ban) JOIN phieu_tra p USING(ma_tra)
 WHERE p.trang_thai='XONG' OR p.ma_tra=NEW.ma_tra GROUP BY b.ma_dong_ban HAVING sum(t.sl)>max(b.sl))) THEN
        RAISE EXCEPTION 'invalid return' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_tra_update_of_trang_thai BEFORE UPDATE OF trang_thai ON phieu_tra
FOR EACH ROW EXECUTE FUNCTION phieu_tra_update_of_trang_thai();

CREATE FUNCTION dong_tra_insert() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_insert_dong_tra
    IF (SELECT trang_thai FROM phieu_tra WHERE ma_tra=NEW.ma_tra)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER dong_tra_insert BEFORE INSERT ON dong_tra
FOR EACH ROW EXECUTE FUNCTION dong_tra_insert();

CREATE FUNCTION dong_tra_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_update_dong_tra
    IF (SELECT trang_thai FROM phieu_tra WHERE ma_tra=OLD.ma_tra)<>'NHAP' OR (SELECT trang_thai FROM phieu_tra WHERE ma_tra=NEW.ma_tra)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER dong_tra_update BEFORE UPDATE ON dong_tra
FOR EACH ROW EXECUTE FUNCTION dong_tra_update();

CREATE FUNCTION dong_tra_delete() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_delete_dong_tra
    IF (SELECT trang_thai FROM phieu_tra WHERE ma_tra=OLD.ma_tra)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN OLD;
END;
$$;
CREATE TRIGGER dong_tra_delete BEFORE DELETE ON dong_tra
FOR EACH ROW EXECUTE FUNCTION dong_tra_delete();

CREATE FUNCTION phieu_nhap_insert() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- start_phieu_nhap
    IF NEW.trang_thai<>'NHAP' THEN
        RAISE EXCEPTION 'draft required' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_nhap_insert BEFORE INSERT ON phieu_nhap
FOR EACH ROW EXECUTE FUNCTION phieu_nhap_insert();

CREATE FUNCTION phieu_nhap_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- transition_phieu_nhap
    IF NOT (OLD.trang_thai='NHAP' AND NEW.trang_thai IN ('NHAP','HUY','XONG')) THEN
        RAISE EXCEPTION 'invalid transition or immutable document' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_nhap_update BEFORE UPDATE ON phieu_nhap
FOR EACH ROW EXECUTE FUNCTION phieu_nhap_update();

CREATE FUNCTION phieu_nhap_delete() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- keep_phieu_nhap
    IF OLD.trang_thai<>'NHAP' THEN
        RAISE EXCEPTION 'preserve posted document' USING ERRCODE = '23514';
    END IF;
    RETURN OLD;
END;
$$;
CREATE TRIGGER phieu_nhap_delete BEFORE DELETE ON phieu_nhap
FOR EACH ROW EXECUTE FUNCTION phieu_nhap_delete();

CREATE FUNCTION phieu_nhap_update_of_trang_thai() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- lines_phieu_nhap
    IF NEW.trang_thai='XONG' AND NOT EXISTS(SELECT 1 FROM dong_nhap WHERE ma_nhap=OLD.ma_nhap) THEN
        RAISE EXCEPTION 'empty document' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_nhap_update_of_trang_thai BEFORE UPDATE OF trang_thai ON phieu_nhap
FOR EACH ROW EXECUTE FUNCTION phieu_nhap_update_of_trang_thai();

CREATE FUNCTION dong_nhap_insert() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_insert_dong_nhap
    IF (SELECT trang_thai FROM phieu_nhap WHERE ma_nhap=NEW.ma_nhap)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER dong_nhap_insert BEFORE INSERT ON dong_nhap
FOR EACH ROW EXECUTE FUNCTION dong_nhap_insert();

CREATE FUNCTION dong_nhap_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_update_dong_nhap
    IF (SELECT trang_thai FROM phieu_nhap WHERE ma_nhap=OLD.ma_nhap)<>'NHAP' OR (SELECT trang_thai FROM phieu_nhap WHERE ma_nhap=NEW.ma_nhap)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER dong_nhap_update BEFORE UPDATE ON dong_nhap
FOR EACH ROW EXECUTE FUNCTION dong_nhap_update();

CREATE FUNCTION dong_nhap_delete() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_delete_dong_nhap
    IF (SELECT trang_thai FROM phieu_nhap WHERE ma_nhap=OLD.ma_nhap)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN OLD;
END;
$$;
CREATE TRIGGER dong_nhap_delete BEFORE DELETE ON dong_nhap
FOR EACH ROW EXECUTE FUNCTION dong_nhap_delete();

CREATE FUNCTION phieu_kiem_insert() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- start_phieu_kiem
    IF NEW.trang_thai<>'NHAP' THEN
        RAISE EXCEPTION 'draft required' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_kiem_insert BEFORE INSERT ON phieu_kiem
FOR EACH ROW EXECUTE FUNCTION phieu_kiem_insert();

CREATE FUNCTION phieu_kiem_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- transition_phieu_kiem
    IF NOT ((OLD.trang_thai='NHAP' AND NEW.trang_thai IN ('NHAP','CHO')) OR (OLD.trang_thai='CHO' AND NEW.trang_thai IN ('DUYET','TU_CHOI'))) THEN
        RAISE EXCEPTION 'invalid transition or immutable document' USING ERRCODE = '23514';
    END IF;
    -- count_ready
    IF NEW.trang_thai IN ('CHO','DUYET') AND EXISTS
 (SELECT 1 FROM dong_kiem d JOIN v_ton v USING(ma_hang) WHERE d.ma_kiem=NEW.ma_kiem AND
 (d.thuc_dem IS NULL OR d.moc_so<>v.moc OR d.ton_so<>v.ton)) THEN
        RAISE EXCEPTION 'stale or incomplete count' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_kiem_update BEFORE UPDATE ON phieu_kiem
FOR EACH ROW EXECUTE FUNCTION phieu_kiem_update();

CREATE FUNCTION phieu_kiem_delete() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- keep_phieu_kiem
    IF OLD.trang_thai<>'NHAP' THEN
        RAISE EXCEPTION 'preserve posted document' USING ERRCODE = '23514';
    END IF;
    RETURN OLD;
END;
$$;
CREATE TRIGGER phieu_kiem_delete BEFORE DELETE ON phieu_kiem
FOR EACH ROW EXECUTE FUNCTION phieu_kiem_delete();

CREATE FUNCTION phieu_kiem_update_of_trang_thai() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- lines_phieu_kiem
    IF NEW.trang_thai='CHO' AND NOT EXISTS(SELECT 1 FROM dong_kiem WHERE ma_kiem=OLD.ma_kiem) THEN
        RAISE EXCEPTION 'empty document' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER phieu_kiem_update_of_trang_thai BEFORE UPDATE OF trang_thai ON phieu_kiem
FOR EACH ROW EXECUTE FUNCTION phieu_kiem_update_of_trang_thai();

CREATE FUNCTION dong_kiem_insert() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_insert_dong_kiem
    IF (SELECT trang_thai FROM phieu_kiem WHERE ma_kiem=NEW.ma_kiem)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER dong_kiem_insert BEFORE INSERT ON dong_kiem
FOR EACH ROW EXECUTE FUNCTION dong_kiem_insert();

CREATE FUNCTION dong_kiem_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_update_dong_kiem
    IF (SELECT trang_thai FROM phieu_kiem WHERE ma_kiem=OLD.ma_kiem)<>'NHAP' OR (SELECT trang_thai FROM phieu_kiem WHERE ma_kiem=NEW.ma_kiem)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER dong_kiem_update BEFORE UPDATE ON dong_kiem
FOR EACH ROW EXECUTE FUNCTION dong_kiem_update();

CREATE FUNCTION dong_kiem_delete() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- guard_delete_dong_kiem
    IF (SELECT trang_thai FROM phieu_kiem WHERE ma_kiem=OLD.ma_kiem)<>'NHAP' THEN
        RAISE EXCEPTION 'locked document lines' USING ERRCODE = '23514';
    END IF;
    RETURN OLD;
END;
$$;
CREATE TRIGGER dong_kiem_delete BEFORE DELETE ON dong_kiem
FOR EACH ROW EXECUTE FUNCTION dong_kiem_delete();

CREATE FUNCTION hang_hoa_update_of_ton_dau() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- opening_balance_locked
    IF EXISTS(SELECT 1 FROM v_bien_dong WHERE ma_hang=OLD.ma_hang) OR EXISTS(SELECT 1 FROM dong_kiem WHERE ma_hang=OLD.ma_hang) THEN
        RAISE EXCEPTION 'opening balance already in use' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER hang_hoa_update_of_ton_dau BEFORE UPDATE OF ton_dau ON hang_hoa
FOR EACH ROW EXECUTE FUNCTION hang_hoa_update_of_ton_dau();

CREATE FUNCTION thu_chi_khac_insert() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- open_thu_chi_khac_INSERT
    IF NEW.trang_thai='XONG' AND (SELECT trang_thai FROM ca_thu_ngan WHERE ma_ca=NEW.ma_ca)<>'MO' THEN
        RAISE EXCEPTION 'shift closed' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER thu_chi_khac_insert BEFORE INSERT ON thu_chi_khac
FOR EACH ROW EXECUTE FUNCTION thu_chi_khac_insert();

CREATE FUNCTION thu_chi_khac_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- open_thu_chi_khac_UPDATE
    IF NEW.trang_thai='XONG' AND (SELECT trang_thai FROM ca_thu_ngan WHERE ma_ca=NEW.ma_ca)<>'MO' THEN
        RAISE EXCEPTION 'shift closed' USING ERRCODE = '23514';
    END IF;
    -- keep_cash
    IF OLD.trang_thai<>'NHAP' THEN
        RAISE EXCEPTION 'posted cash' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER thu_chi_khac_update BEFORE UPDATE ON thu_chi_khac
FOR EACH ROW EXECUTE FUNCTION thu_chi_khac_update();

CREATE FUNCTION thu_chi_khac_delete() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- keep_cash_delete
    IF OLD.trang_thai<>'NHAP' THEN
        RAISE EXCEPTION 'posted cash' USING ERRCODE = '23514';
    END IF;
    RETURN OLD;
END;
$$;
CREATE TRIGGER thu_chi_khac_delete BEFORE DELETE ON thu_chi_khac
FOR EACH ROW EXECUTE FUNCTION thu_chi_khac_delete();
