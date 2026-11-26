"""Điểm vào quản trị POS. Các lệnh thao tác trên DATABASE_URL."""
import argparse
import os
import psycopg

from infrastructure.setup_db import SQL, install


def main():
    parser = argparse.ArgumentParser(description="Thiết lập cơ sở dữ liệu POS PostgreSQL")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Tạo mới 15 bảng, view, index và trigger")
    migrate = commands.add_parser("import-sqlite", help="Tạo schema và nhập dữ liệu SQLite 4.1 hoặc web")
    migrate.add_argument("source", help="Tệp SQLite nguồn")
    commands.add_parser("check", help="Kiểm tra kết nối, schema, số phiếu và tồn kho")
    commands.add_parser("seed", help="Nạp hai tháng dữ liệu vào database demo trống")
    commands.add_parser("migrate-uc01", help="Áp dụng ràng buộc một ca mở cho mỗi thu ngân")
    args = parser.parse_args()
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        parser.error("Cần đặt DATABASE_URL tới cơ sở dữ liệu đích.")
    with psycopg.connect(dsn, autocommit=True) as db:
        db.execute("SET TIME ZONE 'UTC'")
        if args.command == "init":
            install(db)
            print("Đã tạo schema POS.")
        elif args.command == "migrate-uc01":
            with db.transaction():
                db.execute((SQL / "04_uc01_ca_mo.sql").read_text(encoding="utf-8"))
            print("Đã áp dụng ràng buộc ca mở.")
        elif args.command == "seed":
            with db.transaction():
                db.execute((SQL / "03_seed_demo.sql").read_text(encoding="utf-8"))
            print("Đã nạp dữ liệu demo hai tháng.")
        elif args.command == "import-sqlite":
            from infrastructure.import_sqlite import import_from
            result = import_from(args.source, db)
            for name, total in result.items():
                print(f"{name}: {total}")
            print("Đã đối chiếu dữ liệu và tồn kho, giao dịch đã commit.")
        else:
            print("PostgreSQL", db.info.server_version, "| database", db.info.dbname)
            print("Phiếu bán / trả / khóa yêu cầu / mã hàng:",
                  db.execute("""SELECT (SELECT count(*) FROM phieu_ban),
                  (SELECT count(*) FROM phieu_tra), (SELECT count(*) FROM web_yeu_cau),
                  (SELECT count(*) FROM v_ton)""").fetchone())


if __name__ == "__main__":
    main()
