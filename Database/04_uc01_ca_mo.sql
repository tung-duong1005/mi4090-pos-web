-- Chạy trong một giao dịch qua manage.py migrate-uc01.
LOCK TABLE ca_thu_ngan IN SHARE ROW EXCLUSIVE MODE;
DO $$
DECLARE
    trung text;
BEGIN
    SELECT string_agg(nguoi_mo || ' (' || danh_sach || ')', '; ') INTO trung
    FROM (SELECT nguoi_mo, string_agg(ma_ca, ', ' ORDER BY ma_ca) AS danh_sach
          FROM ca_thu_ngan WHERE trang_thai='MO'
          GROUP BY nguoi_mo HAVING count(*) > 1) AS ca_trung;
    IF trung IS NOT NULL THEN
        RAISE EXCEPTION 'Cần đối chiếu các ca đang mở trùng trước khi nâng cấp: %', trung;
    END IF;
END $$;
CREATE UNIQUE INDEX IF NOT EXISTS uq_ca_mo_nguoi ON ca_thu_ngan(nguoi_mo) WHERE trang_thai='MO';
