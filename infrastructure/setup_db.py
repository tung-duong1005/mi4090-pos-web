"""Cài mới hoặc nhập bản chụp vào schema PostgreSQL mới trong một giao dịch."""
from pathlib import Path

SQL = Path(__file__).resolve().parents[1] / "Database"


def install(db, load=None):
    with db.transaction():
        db.execute("SELECT pg_advisory_xact_lock(41702, 4301)")
        db.execute((SQL / "01_schema.sql").read_text(encoding="utf-8"))
        if load is not None:
            load(db)
        db.execute((SQL / "02_rules.sql").read_text(encoding="utf-8"))
