from datetime import datetime, timezone

def luc():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')

def yeu_cau(ok, msg):
    if not ok:
        raise ValueError(msg)
