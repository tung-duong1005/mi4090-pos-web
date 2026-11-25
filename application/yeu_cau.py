import json
from hashlib import sha256
from uuid import uuid4
from application.quay import QuayService

class XungDotYeuCau(ValueError):
    """Một khóa được gửi lại với nội dung khác (HTTP 409)."""


def ghi_yeu_cau(quay: QuayService, uc, khoa, *, ca, pt, dong, goc=None):
    """ma_tk do backend lấy từ phiên đã xác thực; ca, pt, dong là dữ liệu đã giải mã."""
    if uc not in ('02','03') or not isinstance(khoa,str) or not khoa.strip() or len(khoa)>128:
        raise ValueError("Sai nghiệp vụ hoặc khóa yêu cầu")
    if not isinstance(ca,str) or not ca or pt not in ('TM','CK') or not isinstance(dong,(list,tuple)) or not dong:
        raise ValueError("Sai ca, phương thức hoặc danh sách dòng")
    if (uc=='03' and (not isinstance(goc,str) or not goc)) or (uc=='02' and goc is not None):
        raise ValueError("Sai phiếu gốc")
    for d in dong:
        if not isinstance(d,(tuple,list)) or len(d)!=3 or not isinstance(d[0],str) or not d[0]:
            raise ValueError("Sai cấu trúc dòng")
        if type(d[1]) is not int or d[1] <= 0:
            raise ValueError("Lượng phải là số nguyên dương")
        if uc=='02' and (type(d[2]) is not int or d[2]<0):
            raise ValueError("Sai số tiền giảm")
        if uc=='03' and d[2] not in ('TOT','HONG'):
            raise ValueError("Sai tình trạng hàng")
    payload = json.dumps([ca,pt,goc,dong],ensure_ascii=False,separators=(',',':'))
    digest = sha256(payload.encode('utf-8')).hexdigest()
    phien = quay.phien
    dl = phien.du_lieu
    ma_tk = phien.ma_tk
    with dl.giao_dich():
        phien.kiem_quyen(uc)
        old = dl.tim_yeu_cau(ma_tk,uc,khoa)
        if old:
            if old['bam_noi_dung'] != digest:
                raise XungDotYeuCau("Khóa đã dùng cho nội dung khác")
            return old['ma'], False
        ma = uuid4().hex
        if uc=='02':
            quay.ban(ma,ca,pt,dong)
        else:
            quay.tra(ma,ca,goc,pt,dong)
        dl.luu_yeu_cau(ma_tk,uc,khoa,digest,ma)
        return ma, True
