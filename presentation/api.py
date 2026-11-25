"""Controller độc lập với framework. Host xác thực và inject service theo từng request."""
from application.yeu_cau import ghi_yeu_cau, XungDotYeuCau

def post_phieu(quay, uc, khoa, payload):
    try:
        ma, moi = ghi_yeu_cau(quay, uc, khoa, **payload)
    except PermissionError:
        return 403, {"loi": "Không đủ quyền"}
    except XungDotYeuCau as exc:
        return 409, {"loi": str(exc)}
    except ValueError as exc:
        return 422, {"loi": str(exc)}
    return (201 if moi else 200), {"ma_phieu": ma}
