"""Chạy thật pdb, ghi cả lệnh, frame và biến cục bộ cho từng kịch bản."""
import contextlib
import io
import os
import pdb
from pathlib import Path

from demo42 import chay

HERE = Path(__file__).resolve().parent
COMMANDS = {
    'TV1': [
        'tbreak infrastructure/postgres.py:179',
        'tbreak application/quay.py:73, r == 0',
        'continue','where',"p (ma_hang, r['ton'], r['moc'])",
        'up','p (ma, ca, pt, hang, sl)','down','continue',
        'where','p (ma, r)',
        "p self.dl.lay(CaThuNgan, ma).trang_thai",'continue'],
    'TV2': [
        'tbreak infrastructure/postgres.py:182',
        "tbreak domain/__init__.py:193, self.trang_thai == 'DUYET'",
        'continue','where','p ma_hang','up','p (ma, ca, sl)','down','continue',
        'where','p (self.ma_kiem, self.trang_thai, self.nguoi_xet)',
        'up','p (ma, duyet, ly_do)','continue']
}

class Lenh(io.StringIO):
    def __init__(self, commands, log):
        super().__init__('\n'.join(commands)+'\n')
        self.log = log

    def readline(self, *args):
        line = super().readline(*args)
        self.log.write(line)
        return line

def ghi(vai):
    log = io.StringIO()
    debug = pdb.Pdb(stdin=Lenh(COMMANDS[vai],log), stdout=log, readrc=False)
    with contextlib.redirect_stdout(log):
        debug.runcall(chay,vai)
    s = log.getvalue()
    if '***' in s or 'PASS '+vai not in s or s.count('(Pdb) where') != 2:
        raise RuntimeError(s)
    for marker in (('-> return r[', "('PB015', 'C1', 'CK', 'S', 2)", "('C1', 0)") if vai=='TV1'
                   else ("('PB1', 'C1', 1)", "('PK2', 'DUYET', 'Q')")):
        if marker not in s:
            raise RuntimeError(s)
    return s

if __name__ == '__main__':
    os.chdir(HERE)
    for vai in COMMANDS:
        s = ghi(vai)
        (HERE/('PDB_'+vai+'.txt')).write_text(s,encoding='utf-8')
        print(vai, 'PASS | 2 breakpoints, 2 call stacks')
