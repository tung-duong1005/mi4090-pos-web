"""Mỗi bài kiểm thử tạo một schema riêng trong database kiểm thử."""
from contextlib import contextmanager
import os
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo


@contextmanager
def test_schema():
    base = os.environ.get("POS_TEST_DSN")
    if not base:
        raise RuntimeError("Đặt POS_TEST_DSN tới database thử nghiệm để chạy kiểm thử.")
    name = "pos_test_" + uuid4().hex
    with psycopg.connect(base, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(name)))
        try:
            yield make_conninfo(base, options=f"-c search_path={name} -c timezone=UTC")
        finally:
            admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(name)))
