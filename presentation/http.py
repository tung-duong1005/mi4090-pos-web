"""Biên HTTP WSGI. Middleware phía host cung cấp REMOTE_USER đã xác thực."""
import json
from http import HTTPStatus
from presentation.api import post_phieu


def tao_api(mo_quay):
    def handle(env):
        uc = {'/api/ban': '02', '/api/tra': '03'}.get(env.get('PATH_INFO'))
        if not uc:
            return 404, {'loi': 'Sai đường dẫn'}
        if env.get('REQUEST_METHOD') != 'POST':
            return 405, {'loi': 'Cần POST'}
        tk = env.get('REMOTE_USER')
        if not tk:
            return 401, {'loi': 'Cần đăng nhập'}
        if env.get('CONTENT_TYPE','').split(';')[0].strip() != 'application/json':
            return 415, {'loi': 'Cần application/json'}
        try:
            size = int(env.get('CONTENT_LENGTH') or 0)
            if size < 1 or size > 1024*1024:
                return 413, {'loi': 'Kích thước yêu cầu không hợp lệ'}
            data = json.loads(env['wsgi.input'].read(size))
            expected = {'ca','pt','dong'} | ({'goc'} if uc=='03' else set())
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
            return post_phieu(quay,uc,env.get('HTTP_IDEMPOTENCY_KEY'),data)

    def app(env,start_response):
        status,data = handle(env)
        body = json.dumps(data,ensure_ascii=False).encode('utf-8')
        start_response(f'{status} {HTTPStatus(status).phrase}',
                       [('Content-Type','application/json; charset=utf-8'),('Content-Length',str(len(body)))])
        return [body]
    return app
