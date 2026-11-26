import json
import unittest
from contextlib import nullcontext
from io import BytesIO

from application.phien import PhienPOS
from application.quay import QuayService
from domain import NhanVien, TaiKhoan
from presentation.http import tao_api


class KhoCaThu:
    def __init__(self):
        self.ca = None

    def giao_dich(self, chi_doc=False):
        return nullcontext()

    def lay(self, lop, ma):
        if lop is TaiKhoan:
            return TaiKhoan(ma, ma, ma, '', 'QL' if ma == 'ql' else 'TN', 'HOAT_DONG')
        return NhanVien(ma, ma, 'HOAT_DONG')

    def ca_tai_quay(self):
        return self.ca

    def tao_ca(self, ma, nv, dau):
        self.ca = dict(ma_ca=ma, nguoi_mo=nv, tien_dau=str(dau), trang_thai='MO')


class MoCaHTTP(unittest.TestCase):
    def setUp(self):
        self.dl = KhoCaThu()
        self.app = tao_api(lambda tk: nullcontext(QuayService(PhienPOS(self.dl, tk), None)))

    def call(self, method, data=None, tk='tn'):
        body = json.dumps(data).encode()
        env = {'PATH_INFO': '/api/ca', 'REQUEST_METHOD': method, 'REMOTE_USER': tk,
               'CONTENT_TYPE': 'application/json', 'CONTENT_LENGTH': str(len(body)),
               'wsgi.input': BytesIO(body)}
        status = []
        result = self.app(env, lambda s, headers: status.append(int(s[:3])))
        return status[0], json.loads(result[0])

    def test_mo_doc_lai_va_trung(self):
        self.assertEqual(self.call('GET'), (200, {'ca': None}))
        status, result = self.call('POST', {'tien_dau': 200000})
        self.assertEqual(status, 201)
        self.assertEqual(result['ca']['tien_dau'], '200000')
        self.assertEqual(self.call('GET'), (200, result))
        status, trung = self.call('POST', {'tien_dau': 0})
        self.assertEqual((status, trung['ca']), (409, result['ca']))

    def test_quay_ban_va_ban_giao(self):
        status, mo = self.call('POST', {'tien_dau': 0})
        self.assertEqual((status, mo['ca']['tien_dau']), (201, '0'))
        for method in ['GET', 'POST']:
            status, data = self.call(method, {'tien_dau': 0}, 'tn2')
            self.assertEqual((status, data['ca']), (409, None))
        self.dl.ca['trang_thai'] = 'BAN_GIAO'
        self.assertEqual(self.call('POST', {'tien_dau': 0})[0], 409)

    def test_so_tien_sai(self):
        for value in ['', None, -1, 2.5, True, 2**63]:
            with self.subTest(value=value):
                self.assertEqual(self.call('POST', {'tien_dau': value})[0], 422)
        self.assertEqual(self.call('POST', {'tien_dau': 0, 'nguoi_mo': 'tn2'})[0], 422)
        self.assertIsNone(self.call('GET')[1]['ca'])

    def test_quyen(self):
        for method in ['POST', 'GET']:
            for tk, status in [(None, 401), ('ql', 403)]:
                self.assertEqual(self.call(method, {'tien_dau': 0}, tk)[0], status)

