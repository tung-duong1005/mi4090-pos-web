-- Chạy trong một giao dịch qua manage.py migrate-uc01.
LOCK TABLE ca_thu_ngan IN SHARE ROW EXCLUSIVE MODE;
DO $$
DECLARE
    trung text;
BEGIN
    SELECT string_agg(ma_ca, ', ' ORDER BY ma_ca) INTO trung
    FROM ca_thu_ngan WHERE trang_thai IN ('MO','BAN_GIAO')
    HAVING count(*) > 1;
    IF trung IS NOT NULL THEN
        RAISE EXCEPTION 'Cần đối chiếu các ca đang chiếm quầy: %', trung;
    END IF;
END $$;
CREATE UNIQUE INDEX IF NOT EXISTS mot_ca_tai_quay ON ca_thu_ngan((1))
    WHERE trang_thai IN ('MO','BAN_GIAO');
DROP INDEX IF EXISTS uq_ca_mo_nguoi;
