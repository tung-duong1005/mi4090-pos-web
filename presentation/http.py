"""Biên HTTP WSGI. Middleware phía host cung cấp REMOTE_USER đã xác thực."""
import json
from http import HTTPStatus
from pathlib import Path
from uuid import uuid4
from application.quay import CaDaMo
from presentation.api import post_phieu

FORMS = Path(__file__).resolve().parents[1] / "frontend" / "forms"
ASSETS = {"frm_nv_mo_ca.html": "text/html", "frm_nv_mo_ca.js": "text/javascript",
          "frm_nv_ban.css": "text/css"}


def api_ca(quay, data=None):
    try:
        if data is None:
            return 200, {'ca': quay.ca_dang_mo()}
        return 201, {'ca': quay.mo_ca(uuid4().hex, data['tien_dau'])}
    except CaDaMo as exc:
        return 409, {'loi': str(exc), 'ca': exc.ca}
    except PermissionError:
        return 403, {'loi': 'Không đủ quyền mở ca'}
    except ValueError as exc:
        return 422, {'loi': str(exc)}


def tao_api(mo_quay):
    def handle(env):
        uc = {'/api/ca': '01', '/api/ban': '02', '/api/tra': '03'}.get(env.get('PATH_INFO'))
        if not uc:
            return 404, {'loi': 'Sai đường dẫn'}
        doc_ca = uc == '01' and env.get('REQUEST_METHOD') == 'GET'
        if not doc_ca and env.get('REQUEST_METHOD') != 'POST':
            return 405, {'loi': 'Cần POST'}
        tk = env.get('REMOTE_USER')
        if not tk:
            return 401, {'loi': 'Cần đăng nhập'}
        if doc_ca:
            with mo_quay(tk) as quay:
                return api_ca(quay)
        if env.get('CONTENT_TYPE','').split(';')[0].strip() != 'application/json':
            return 415, {'loi': 'Cần application/json'}
        try:
            size = int(env.get('CONTENT_LENGTH') or 0)
            if size < 1 or size > 1024*1024:
                return 413, {'loi': 'Kích thước yêu cầu không hợp lệ'}
            data = json.loads(env['wsgi.input'].read(size))
            expected = {'ca','pt','dong'} | ({'goc'} if uc=='03' else set())
            if uc == '01':
                expected = {'tien_dau'}
            if not isinstance(data,dict) or set(data) != expected:
                return 422, {'loi': 'Sai trường dữ liệu'}
            if uc == '02':
                # API bán chuẩn lấy giá trên máy chủ. Giảm giá theo chính sách cần endpoint riêng.
                if not isinstance(data['dong'],list) or any(not isinstance(d,list) or len(d)!=2 for d in data['dong']):
                    return 422, {'loi': 'Dòng bán cần mã hàng và số lượng'}
                data['dong'] = [(ma,sl,0) for ma,sl in data['dong']]
        except (ValueError,UnicodeError):
            return 400, {'loi': 'JSON hoặc độ dài không hợp lệ'}
        with mo_quay(tk) as quay:
            if uc == '01':
                return api_ca(quay, data)
            return post_phieu(quay,uc,env.get('HTTP_IDEMPOTENCY_KEY'),data)

    def app(env,start_response):
        path = env.get('PATH_INFO', '')
        name = path.removeprefix('/frontend/forms/')
        if path.startswith('/frontend/forms/') and name in ASSETS and env.get('REQUEST_METHOD') == 'GET':
            body = (FORMS / name).read_bytes()
            start_response('200 OK', [('Content-Type', ASSETS[name] + '; charset=utf-8'),
                                      ('Content-Length', str(len(body)))])
            return [body]
        status,data = handle(env)
        body = json.dumps(data,ensure_ascii=False).encode('utf-8')
        start_response(f'{status} {HTTPStatus(status).phrase}',
                       [('Content-Type','application/json; charset=utf-8'),('Content-Length',str(len(body))),
                        ('Cache-Control','no-store')])
        return [body]
    return app
