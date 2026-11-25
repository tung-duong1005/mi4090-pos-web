"""python -B kiem_tra_43.py: kiểm import, SQL và luồng HTTP không mở browser."""
import ast
import graphlib
import io
import json
import re
import unittest
from pathlib import Path

from bootstrap import tao_web
import kiem_thu_web as web_tests

ROOT = Path(__file__).resolve().parent
LAYERS = {'application','infrastructure','presentation','domain'}
ALLOW = {
    'application': {'domain','application'},
    'domain': {'domain'},
    'presentation': {'presentation','application','domain'},
    'infrastructure': {'infrastructure','application','domain'}
}


class KienTruc(unittest.TestCase):
    def test_import_va_sql(self):
        files = [f for base in LAYERS for f in (ROOT/base).glob('*.py')]
        modules = {}
        for f in files:
            key = '.'.join(f.relative_to(ROOT).with_suffix('').parts).removesuffix('.__init__')
            modules[key] = f
        graph = {}
        for name,path in modules.items():
            package = name.split('.')[0]
            graph[name] = set()
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):
                    self.assertEqual(node.level,0,name)
                    deps = [node.module]
                elif isinstance(node,ast.Import):
                    deps = [a.name for a in node.names]
                else:
                    deps = []
                for dep in deps:
                    part=dep.split('.')[0]
                    if part in LAYERS:
                        self.assertIn(part,ALLOW[package],name)
                        self.assertIn(dep,modules)
                        graph[name].add(dep)
                    self.assertNotIn(part,{'bootstrap','pos','web_db'},name)
                    if package!='infrastructure':
                        self.assertNotIn(part,{'sqlite3','psycopg'},name)
                if package!='infrastructure' and isinstance(node,ast.Constant) and isinstance(node.value,str):
                    self.assertIsNone(re.search(r'\b(SELECT\b.+\bFROM|INSERT INTO|UPDATE\s+\w+\s+SET|DELETE FROM|BEGIN IMMEDIATE|SAVEPOINT)\b',node.value,re.I|re.S),name)
            if name in ('application.quay','application.kho'):
                peer='application.kho' if name.endswith('.quay') else 'application.quay'
                self.assertNotIn(peer,graph[name])
        tuple(graphlib.TopologicalSorter(graph).static_order())


class HttpPOS(unittest.TestCase):
    def setUp(self):
        fixture=web_tests.POSWeb()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fx=fixture
        self.app=tao_web(fixture.path)

    def post(self,route,body,key='B',user='T'):
        raw=json.dumps(body).encode()
        env={'REQUEST_METHOD':'POST','PATH_INFO':route,'REMOTE_USER':user,'CONTENT_TYPE':'application/json',
             'CONTENT_LENGTH':str(len(raw)),'wsgi.input':io.BytesIO(raw),'HTTP_IDEMPOTENCY_KEY':key}
        statuses=[]
        result=b''.join(self.app(env,lambda status,headers:statuses.append(status)))
        return int(statuses[0][:3]),json.loads(result)

    def test_http_ban_tra_va_retry(self):
        payload={'ca':'C','pt':'CK','dong':[['S',2]]}
        code,ban=self.post('/api/ban',payload)
        self.assertEqual(code,201)
        self.assertEqual(self.post('/api/ban',payload),(200,ban))
        self.assertEqual(self.post('/api/ban',dict(payload,pt='TM'))[0],409)
        from infrastructure.postgres import ket_noi_request
        with ket_noi_request(self.fx.path) as dl:
            line=dl.mot('SELECT ma_dong_ban FROM dong_ban')['ma_dong_ban']
        ret={'ca':'C','goc':ban['ma_phieu'],'pt':'TM','dong':[[line,1,'TOT']]}
        code,tra=self.post('/api/tra',ret,'R')
        self.assertEqual(code,201)
        self.assertEqual(self.post('/api/tra',ret,'R'),(200,tra))
        self.assertEqual(self.fx.ket_qua(),(1,2,1))

    def test_http_bien_va_xung_dot(self):
        payload={'ca':'C','pt':'CK','dong':[['S',1],['S',2]]}
        self.assertEqual(self.post('/api/ban',payload,user=None)[0],401)
        self.assertEqual(self.post('/api/ban',dict(payload,ma_tk='T'))[0],422)
        self.assertEqual(self.post('/api/ban',payload)[0],409)
        self.assertEqual(self.fx.ket_qua(),(0,0,2))

if __name__=='__main__':
    unittest.main(verbosity=2)
