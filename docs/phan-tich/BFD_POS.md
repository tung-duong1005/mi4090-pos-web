# Sơ đồ phân cấp chức năng hệ thống POS bán lẻ

Phạm vi gồm một cửa hàng có quầy thu ngân và kho. Cây chức năng có **1 nút gốc, 6 nhánh cấp 2 và 21 chức năng cấp 3**. Sơ đồ đọc từ trái sang phải. Mỗi đường nối biểu thị chức năng con thuộc chức năng cha.

## Cây chức năng hoàn chỉnh

```mermaid
flowchart LR
  F1["F1 · Hệ thống POS bán lẻ"]
  F1 --> B1["F1.1 · Quản trị hệ thống · TV2"]
  B1 --> C11["F1.1.1 · Quản lý tài khoản và phân quyền"]
  B1 --> C12["F1.1.2 · Tra nhật ký thao tác"]
  B1 --> C13["F1.1.3 · Sao lưu và phục hồi dữ liệu"]
  F1 --> B2["F1.2 · Quản lý danh mục · TV2"]
  B2 --> C21["F1.2.1 · Quản lý hàng hóa"]
  B2 --> C22["F1.2.2 · Quản lý bảng giá bán"]
  B2 --> C23["F1.2.3 · Quản lý hồ sơ nhân viên"]
  F1 --> B3["F1.3 · Bán hàng và trả hàng · TV1"]
  B3 --> C31["F1.3.1 · Lập phiếu bán"]
  B3 --> C32["F1.3.2 · Ghi nhận thanh toán và in phiếu"]
  B3 --> C33["F1.3.3 · Xử lý trả hàng theo phiếu gốc và hoàn tiền"]
  F1 --> B4["F1.4 · Quản lý ca thu ngân · TV1"]
  B4 --> C41["F1.4.1 · Mở ca và ghi tiền đầu ca"]
  B4 --> C42["F1.4.2 · Ghi thu, chi tiền mặt khác"]
  B4 --> C43["F1.4.3 · Kết ca, đối chiếu tiền và bàn giao"]
  F1 --> B5["F1.5 · Quản lý kho · TV2"]
  B5 --> C51["F1.5.1 · Lập phiếu nhập hàng"]
  B5 --> C52["F1.5.2 · Cập nhật tồn từ giao dịch bán và trả hàng"]
  B5 --> C53["F1.5.3 · Lập phiếu kiểm kho"]
  B5 --> C54["F1.5.4 · Duyệt chênh lệch và điều chỉnh tồn"]
  F1 --> B6["F1.6 · Báo cáo thống kê · TV1"]
  B6 --> C61["F1.6.1 · Báo cáo doanh số cuối ngày"]
  B6 --> C62["F1.6.2 · Báo cáo thanh toán và kết ca"]
  B6 --> C63["F1.6.3 · Báo cáo nhập–xuất–tồn"]
  B6 --> C64["F1.6.4 · Báo cáo chênh lệch kiểm kho"]
  B6 --> C65["F1.6.5 · Theo dõi bán hàng và tồn kho trên dashboard"]
```

## Phân công và truy vết

TV1 chủ trì F1.3, F1.4 và F1.6. TV2 chủ trì F1.1, F1.2 và F1.5. Trong nhánh báo cáo, mỗi thành viên thực hiện hai báo cáo và cả hai cùng xây dựng dashboard.

| Mã cấp 3 | Chức năng | Use case | Thực hiện |
|---|---|---|---|
| F1.1.1 | Quản lý tài khoản và phân quyền | UC10 | TV2 |
| F1.1.2 | Tra nhật ký thao tác | UC16 | TV2 |
| F1.1.3 | Sao lưu và phục hồi dữ liệu | UC17 | TV2 |
| F1.2.1 | Quản lý hàng hóa | UC18, UC06 | TV2 |
| F1.2.2 | Quản lý bảng giá bán | UC06 | TV2 |
| F1.2.3 | Quản lý hồ sơ nhân viên | UC19, UC10 | TV2 |
| F1.3.1 | Lập phiếu bán | UC02 | TV1 |
| F1.3.2 | Ghi nhận thanh toán và in phiếu | UC02 | TV1 |
| F1.3.3 | Xử lý trả hàng theo phiếu gốc và hoàn tiền | UC03 | TV1 |
| F1.4.1 | Mở ca và ghi tiền đầu ca | UC01 | TV1 |
| F1.4.2 | Ghi thu, chi tiền mặt khác | UC04 | TV1 |
| F1.4.3 | Kết ca, đối chiếu tiền và bàn giao | UC05 | TV1 |
| F1.5.1 | Lập phiếu nhập hàng | UC07 | TV2 |
| F1.5.2 | Cập nhật tồn từ giao dịch bán và trả hàng | UC02, UC03 | TV2 |
| F1.5.3 | Lập phiếu kiểm kho | UC08 | TV2 |
| F1.5.4 | Duyệt chênh lệch và điều chỉnh tồn | UC09 | TV2 |
| F1.6.1 | Báo cáo doanh số cuối ngày | UC11 | TV1 |
| F1.6.2 | Báo cáo thanh toán và kết ca | UC12 | TV1 |
| F1.6.3 | Báo cáo nhập–xuất–tồn | UC13 | TV2 |
| F1.6.4 | Báo cáo chênh lệch kiểm kho | UC14 | TV2 |
| F1.6.5 | Theo dõi bán hàng và tồn kho trên dashboard | UC15 | TV1 và TV2 |

## Hai nghiệp vụ nối quầy và kho

- **UC02 – Bán hàng và thanh toán.** F1.3.1 lập phiếu, F1.3.2 ghi nhận thanh toán. Khi xác nhận bán, F1.5.2 giảm tồn theo các dòng hàng đã bán.
- **UC03 – Trả hàng và hoàn tiền.** F1.3.3 tra phiếu gốc, ghi lượng trả và tiền hoàn. F1.5.2 tăng tồn bán được theo lượng hàng trả đủ điều kiện.

Xem tiền điều kiện, ngoại lệ và ví dụ kiểm thử trong [đặc tả use case POS](https://chatgpt.com/library?file_id=libfile_33342f001d34819193560c46ddd23ba4&account_id=personal).
