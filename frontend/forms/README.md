# Danh mục màn hình dự kiến
Dùng một khung điều hướng chung. Tên module form giao dịch bắt đầu bằng `frm_nv_`, form danh mục bắt đầu bằng `frm_dm_`. Bảng là thiết kế để triển khai. Các tên module bên dưới chưa phải form chạy được.

| Mã dự kiến | UC | Nội dung chính hoặc chi tiết | Chủ trì |
|---|---|---|---|
| frm_nv_mo_ca | 01 | Tiền đầu ca, người mở | TV1 |
| frm_nv_ban | 02 | Phiếu và các dòng hàng, tính lại tổng | TV1 |
| frm_nv_tra | 03 | Phiếu gốc, các dòng trả, tình trạng và tiền hoàn | TV1 |
| frm_nv_thu_chi | 04 | Loại, số tiền, lý do | TV1 |
| frm_nv_ban_giao | 05 | Quỹ dự kiến, thực đếm, chênh lệch | TV1 |
| frm_nv_doi_gia | 06 | Giá đang bán và giá mới | TV2 |
| frm_nv_nhap | 07 | Phiếu nhập và các dòng nhập | TV2 |
| frm_nv_kiem | 08 | Phiếu kiểm và các dòng kiểm | TV2 |
| frm_nv_duyet_kiem | 09 | Các dòng lệch, quyết định và lý do | TV2 |
| frm_dm_tai_khoan | 10 | Nhân viên, tài khoản, vai trò, trạng thái | TV2 |

Hai endpoint đã có là `POST /api/ban` và `POST /api/tra`. Ví dụ, để đi hết UC02 từ màn hình cần bổ sung API đọc ca đang mở và tra hàng theo mã vạch. Mỗi form cần ánh xạ cột về biểu mẫu/UC, dùng tiền định dạng `#,##0`, ngày `dd/MM/yyyy`, hiển thị rõ lỗi và kiểm tra lại ở Service.
