"""Đọc snapshot SQLite, ghi vào PostgreSQL và đối chiếu trước khi commit."""
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from psycopg import sql
from psycopg.rows import tuple_row

from infrastructure.setup_db import install

TABLES = (
    "nhan_vien", "tai_khoan", "hang_hoa", "ca_thu_ngan", "phieu_ban", "dong_ban",
    "phieu_tra", "dong_tra", "thu_chi_khac", "phieu_nhap", "dong_nhap", "phieu_kiem",
    "dong_kiem", "nhat_ky", "web_yeu_cau",
)
TIMES = {"thoi_diem", "gio_mo", "gio_dong", "luc_lap", "luc_gui", "luc_xet", "luc_dem"}


def source_tables(source):
    names = {r[0] for r in source.execute("SELECT name FROM sqlite_schema WHERE type='table'")}
    missing = set(TABLES[:-1]) - names
    if missing:
        raise ValueError("Thiếu bảng nguồn: " + ", ".join(sorted(missing)))
    if source.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise ValueError("Tệp nguồn không đạt kiểm tra toàn vẹn.")
    if source.execute("PRAGMA foreign_key_check").fetchone():
        raise ValueError("Nguồn có khóa ngoại không hợp lệ.")
    return [name for name in TABLES if name in names]


def normalize(col, val):
    if col in TIMES and val is not None:
        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return val


def copy_snapshot(source, db):
    report = {}
    for table in source_tables(source):
        # table chỉ lấy từ TABLES. COPY chỉ lấy cột nghiệp vụ, PostgreSQL sinh thu_tu.
        cursor = source.execute(f'SELECT * FROM "{table}" ORDER BY rowid')
        cols = [d[0] for d in cursor.description]
        fields = sql.SQL(", ").join(map(sql.Identifier, cols))
        name = sql.Identifier(table)
        with db.cursor(row_factory=tuple_row) as dest:
            dest.execute(sql.SQL("SELECT * FROM {} LIMIT 0").format(name))
            expected = [f.name for f in dest.description if f.name != "thu_tu"]
            if set(cols) != set(expected):
                raise ValueError(f"Các cột của {table} không khớp schema đích.")
            with dest.copy(sql.SQL("COPY {} ({}) FROM STDIN").format(name, fields)) as cp:
                for row in cursor:
                    cp.write_row(tuple(normalize(c, x) for c, x in zip(cols, row)))
            # Đối chiếu từng trường theo khóa chính hoặc thứ tự dòng trên phiếu.
            info = source.execute(f'PRAGMA table_info("{table}")').fetchall()
            pk = [r[1] for r in sorted(info, key=lambda r: r[5]) if r[5]]
            line = table in ("dong_ban", "dong_tra", "dong_nhap", "dong_kiem")
            src_order = "rowid" if line else ", ".join('"' + c + '" COLLATE BINARY' for c in pk)
            pg_order = sql.SQL("thu_tu") if line else sql.SQL(", ").join(
                sql.SQL('{} COLLATE "C"').format(sql.Identifier(c)) for c in pk)
            src = source.execute(f'SELECT * FROM "{table}" ORDER BY {src_order}')
            query = sql.SQL("SELECT {} FROM {} ORDER BY {}").format(fields, name, pg_order)
            with db.cursor(name="verify_rows", row_factory=tuple_row) as check:
                check.execute(query)
                count = 0
                for row in src:
                    if check.fetchone() != tuple(normalize(c, x) for c, x in zip(cols, row)):
                        raise ValueError(f"Sai dữ liệu khi đối chiếu {table}, dòng {count + 1}.")
                    count += 1
                if check.fetchone() is not None:
                    raise ValueError(f"Số bản ghi đích vượt nguồn ở {table}.")
                report[table] = count
    with db.cursor(row_factory=tuple_row) as cur:
        cur.execute('SELECT ma_hang,ton,moc FROM v_ton ORDER BY ma_hang COLLATE "C"')
        old = source.execute("SELECT ma_hang,ton,moc FROM v_ton ORDER BY ma_hang COLLATE BINARY")
        if list(cur) != list(old):
            raise ValueError("Số dư hoặc mốc biến động kho không khớp.")
    return report


def import_from(path, db):
    uri = Path(path).resolve(strict=True).as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as source:
        source.execute("BEGIN")
        report = {}
        install(db, lambda dest: report.update(copy_snapshot(source, dest)))
    return report
