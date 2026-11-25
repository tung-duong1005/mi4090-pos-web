from application.quay import QuayService
from application.kho import KhoService
from application.phien import PhienPOS
from application.yeu_cau import ghi_yeu_cau
from infrastructure.postgres import SoKhoPostgreSQL
from infrastructure.postgres import ket_noi_request
from contextlib import contextmanager
from presentation.http import tao_api
import psycopg
from psycopg import errors

def lap_service(dl, ma_tk):
    phien = PhienPOS(dl, ma_tk)
    kho = SoKhoPostgreSQL(dl)
    return QuayService(phien, kho), KhoService(phien, kho)

def ghi_phieu(dl, ma_tk, uc, khoa, *, ca, pt, dong, goc=None):
    quay, _ = lap_service(dl, ma_tk)
    return ghi_yeu_cau(quay, uc, khoa, ca=ca, pt=pt, dong=dong, goc=goc)


def tao_web(dsn):
    @contextmanager
    def mo_quay(ma_tk):
        with ket_noi_request(dsn) as dl:
            quay, _ = lap_service(dl, ma_tk)
            yield quay

    app = tao_api(mo_quay)

    def wsgi(env, start_response):
        try:
            return app(env, start_response)
        except (errors.NumericValueOutOfRange, errors.CharacterNotInRepertoire):
            start_response('422 Unprocessable Entity', [('Content-Type', 'application/json')])
            return [b'{"error":"invalid_value"}']
        except psycopg.IntegrityError:
            start_response('409 Conflict', [('Content-Type', 'application/json')])
            return [b'{"error":"constraint_conflict"}']
        except (errors.LockNotAvailable, errors.DeadlockDetected, errors.SerializationFailure,
                psycopg.errors.ConnectionException, psycopg.OperationalError):
            start_response('503 Service Unavailable', [('Content-Type','application/json'),('Retry-After','1')])
            return [b'{"error":"database_busy"}']
    return wsgi
