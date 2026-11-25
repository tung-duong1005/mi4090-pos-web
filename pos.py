"""Facade tương thích cho chương trình và test mục 4.1–4.2."""
from infrastructure.postgres import BANG, CHI_TIET, KhoDuLieu, SoKhoPostgreSQL
from application.phien import QUYEN, PhienPOS
from application.quay import QuayService
from application.kho import KhoService
from application.ports import ITonKho
from domain.common import luc, yeu_cau
from domain import *
