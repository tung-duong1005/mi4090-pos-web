"""Điểm vào của WSGI server; middleware xác thực gán REMOTE_USER bằng ma_tk."""
import os
from bootstrap import tao_web

application = tao_web(os.environ["DATABASE_URL"])
