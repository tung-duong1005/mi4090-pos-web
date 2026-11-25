# Ca sử dụng của hệ thống POS bán lẻ

Phạm vi: một cửa hàng có quầy thu ngân và kho. Bốn vai trò sử dụng phần mềm gồm thu ngân, nhân viên kho, quản lý và quản trị viên. TV1 và TV2 là hai thành viên phụ trách cài đặt. Khách hàng giao dịch với thu ngân, còn thu ngân thao tác trên POS.

## 1. Danh mục cốt lõi và đối chiếu với BFD

| Mã | Mục tiêu của người dùng | Người thao tác | Chức năng BFD | Chủ trì |
|---|---|---|---|---|
| UC01 | Mở ca thu ngân | Thu ngân | F1.4.1 | TV1 |
| UC02 | Bán hàng và thanh toán | Thu ngân | F1.3.1, F1.3.2 ↔ F1.5.2 | TV1, phối hợp TV2 |
| UC03 | Trả hàng theo phiếu bán và hoàn tiền | Thu ngân | F1.3.3 ↔ F1.5.2 | TV1, phối hợp TV2 |
| UC04 | Ghi nhận khoản thu, chi tiền mặt trong ca | Thu ngân | F1.4.2 | TV1 |
| UC05 | Kết ca và bàn giao tiền | Thu ngân, quản lý đối chiếu | F1.4.3 | TV1 |
| UC06 | Cập nhật giá bán cho hàng hóa | Quản lý | F1.2.1, F1.2.2 | TV2 |
| UC07 | Nhập hàng vào kho | Nhân viên kho | F1.5.1 | TV2 |
| UC08 | Kiểm đếm hàng và gửi kết quả kiểm kho | Nhân viên kho | F1.5.3 | TV2 |
| UC09 | Duyệt chênh lệch và điều chỉnh tồn kho | Quản lý | F1.5.4 | TV2 |
| UC10 | Cấp tài khoản và phân quyền nhân viên | Quản trị viên | F1.1.1, F1.2.3 | TV2 |

### Đối chiếu mục 1.1 và 3.1 của checklist

| Chỉ tiêu | Thiết kế của nhóm |
|---|---|
| Ít nhất 8 UC cốt lõi, ít nhất 4 UC/người | 10 UC. TV1 chủ trì UC01–UC05, TV2 chủ trì UC06–UC10. |
| Ít nhất 4 giao dịch phức hợp | 5 giao dịch: UC02, UC03, UC05, UC07, UC09. |
| Ít nhất 2 luồng liên phân hệ | UC02 bán hàng và giảm tồn; UC03 trả hàng, hoàn tiền và cập nhật tồn theo tình trạng hàng. Mỗi UC tính một lần cho người chủ trì. |
| Truy vết hai chiều | Mã BFD nằm trong bảng danh mục. Khi cài đặt, nhóm bổ sung tên form, Service và ca kiểm thử thực tế cho từng UC. |

## 2. Đặc tả hai luồng liên phân hệ

### UC02 — Bán hàng và thanh toán

**Mục tiêu.** Hoàn tất một lần bán, giao phiếu cho khách, ghi nhận phương thức thanh toán và cập nhật số lượng hàng còn bán được.

**Tiền điều kiện.** Thu ngân đã đăng nhập, có quyền bán hàng và có ca đang mở.

| Bước | Thu ngân | Hệ thống |
|---|---|---|
| 1 | Quét mã hoặc chọn sản phẩm, nhập số lượng. | Tìm hàng theo mã và quy cách, lấy giá, hiển thị từng dòng và tổng tiền. |
| 2 | Chọn tiền mặt hoặc chuyển khoản. | Hiển thị số phải thu. Với tiền mặt, tính tiền trả lại. Với chuyển khoản, ghi nhận xác nhận đã nhận tiền của thu ngân. |
| 3 | Xác nhận hoàn tất. | Phân hệ bán hàng của TV1 yêu cầu phân hệ kho của TV2 kiểm tra và trừ tồn từng dòng. |
| 4 | Nhận kết quả và in phiếu. | Lưu phiếu bán, đơn giá thực bán, khoản thanh toán gắn với ca và biến động giảm tồn trong cùng giao dịch dữ liệu. Cho in sau khi lưu thành công. |

**Ngoại lệ.**

- Thiếu hàng khi xác nhận: hiển thị mặt hàng thiếu và lượng còn bán được, cho sửa giỏ hàng.
- Ghi kho thất bại: hoàn tác dữ liệu của lần bán, tránh để lại phiếu đã hoàn tất hoặc dòng tồn cập nhật dở.
- Máy in lỗi sau khi dữ liệu đã lưu: cho in lại phiếu cũ, giữ nguyên doanh số và số lượng tồn.

**Ca kiểm chứng.** Bán 2 hộp sữa giá 25.000 đồng/hộp, khách chuyển khoản. Kết quả mong đợi gồm một phiếu 50.000 đồng, tồn giảm 2 hộp, thu chuyển khoản tăng 50.000 đồng và tiền mặt dự kiến trong ngăn kéo tăng 0 đồng.

### UC03 — Trả hàng theo phiếu bán và hoàn tiền

**Mục tiêu.** Nhận đúng số hàng khách còn được trả, hoàn tiền theo giao dịch gốc và cập nhật tồn theo tình trạng hàng.

**Tiền điều kiện.** Thu ngân có quyền trả hàng, ca đang mở và tra được phiếu bán đã hoàn tất.

| Bước | Thu ngân | Hệ thống |
|---|---|---|
| 1 | Nhập hoặc quét mã phiếu gốc. | Hiển thị các dòng hàng, giá thực bán, số đã mua và số đã trả theo các phiếu trả còn hiệu lực. |
| 2 | Chọn dòng hàng, nhập số muốn trả. | Tính số còn được trả bằng số đã bán trừ tổng số đã trả của chính dòng đó. Chặn lượng vượt giới hạn. |
| 3 | Ghi tình trạng hàng, chọn phương thức hoàn. | Tính tiền hoàn theo giá thực bán lưu trên dòng phiếu gốc. Xác định lượng đủ điều kiện nhập lại tồn bán được. |
| 4 | Xác nhận trả hàng. | TV1 ghi phiếu trả liên kết với phiếu gốc và ghi khoản hoàn. TV2 cập nhật tồn đủ điều kiện. Hai phần cùng hoàn tất trong một giao dịch dữ liệu. |

**Ngoại lệ.**

- Khách trả nhiều lần: kiểm tra tổng số đã trả của mọi lần trước khi xác nhận lần mới.
- Hàng không còn bán được: ghi tình trạng trên phiếu, giữ nguyên tồn bán được của phần hàng này.
- Cập nhật kho thất bại: hoàn tác phiếu trả và bản ghi hoàn tiền trong CSDL. Khoản chuyển tiền thực tế đã thực hiện bên ngoài phần mềm cần được đối chiếu riêng.

**Ca kiểm chứng.** Phiếu bán gốc ghi 2 hộp, khách đã trả 1 hộp. Yêu cầu trả tiếp 2 hộp bị chặn. Trả tiếp 1 hộp đủ điều kiện thì được chấp nhận, tồn bán được tăng 1 và số còn được trả về 0.

## 3. Đặc tả tám ca cốt lõi còn lại

| Mã | Tiền điều kiện | Luồng chính và hậu điều kiện | Trường hợp cần kiểm tra |
|---|---|---|---|
| UC01 | Thu ngân đã đăng nhập và có quyền mở ca. | Nhập tiền đầu ca và xác nhận. Hệ thống lưu mã ca, người mở, thời điểm và số tiền. Các giao dịch sau gắn với mã ca này. | Tiền đầu ca âm hoặc thu ngân đã có ca đang mở. |
| UC04 | Có ca đang mở. | Chọn thu hoặc chi, nhập số tiền, lý do và xác nhận. Hệ thống lập phiếu và cập nhật quỹ tiền mặt dự kiến. | Chặn số tiền không dương, ca đã đóng hoặc ghi trùng khoản đã hạch toán qua bán hay trả hàng. |
| UC05 | Ca đang mở, thu ngân có quyền kết ca. | Hệ thống tổng hợp quỹ dự kiến. Thu ngân nhập tiền thực đếm, ghi giải trình chênh lệch. Quản lý đối chiếu, hệ thống lưu bàn giao và đóng ca. | Khi lệch tiền, giữ số dự kiến, thực đếm và giải trình. Chặn giao dịch mới ghi vào ca đã đóng. |
| UC06 | Quản lý có quyền sửa giá, mặt hàng đã tồn tại. | Chọn đúng hàng và quy cách, nhập giá mới và xác nhận. Lần bán tiếp theo dùng giá mới. Phiếu cũ giữ giá tại thời điểm bán. | Thử mã sai, giá âm và tra lại phiếu cũ sau khi đổi giá. |
| UC07 | Nhân viên kho có quyền nhập hàng. | Chọn nhà cung cấp, ghi các dòng hàng, lượng thực nhận và đơn giá nhập. Kiểm tra tổng rồi xác nhận. Hệ thống lưu phiếu và tăng tồn. | Phiếu rỗng, số lượng không dương hoặc lỗi ghi kho. Khi lỗi, hoàn tác phiếu và các dòng đã ghi. |
| UC08 | Nhân viên kho có quyền kiểm kê. | Ghi tồn làm căn cứ, nhập lượng đếm thực tế, tính lệch từng dòng và gửi phiếu sang trạng thái Chờ duyệt. | Phân biệt dòng chưa đếm với thực đếm bằng 0. Gửi phiếu chưa làm đổi tồn. |
| UC09 | Quản lý có quyền duyệt, phiếu đang Chờ duyệt. | Xem chênh lệch và giải trình. Nếu duyệt, ghi điều chỉnh kho, người duyệt và thời điểm. Nếu từ chối, lưu lý do. | Chặn sai quyền khi gọi thẳng Service, chặn duyệt lại. Nếu có giao dịch kho phát sinh sau lúc đếm, yêu cầu đối chiếu trước khi điều chỉnh. |
| UC10 | Quản trị viên đã đăng nhập, hồ sơ nhân viên tồn tại. | Chọn nhân viên, tạo tài khoản, gán vai trò và lưu. Khi đăng nhập, quyền của người dùng được áp dụng vào từng nghiệp vụ. | Chặn tên đăng nhập trùng. Kiểm quyền ở Service khi người thiếu quyền gọi trực tiếp. |

## 4. Ca sử dụng bổ sung và trách nhiệm thực hiện

| Mã | Ca sử dụng | BFD | Thành viên |
|---|---|---|---|
| UC11 | Xem báo cáo doanh số cuối ngày | F1.6.1 | TV1 |
| UC12 | Đối chiếu thanh toán và xem báo cáo kết ca | F1.6.2 | TV1 |
| UC13 | Xem báo cáo nhập–xuất–tồn | F1.6.3 | TV2 |
| UC14 | Xem báo cáo chênh lệch kiểm kho | F1.6.4 | TV2 |
| UC15 | Theo dõi bán hàng và tồn kho trên dashboard tổng hợp | F1.6.5 | TV1 và TV2 |
| UC16 | Tra nhật ký thao tác | F1.1.2 | TV2 |
| UC17 | Sao lưu, phục hồi dữ liệu | F1.1.3 | TV2 |
| UC18 | Quản lý danh mục hàng hóa | F1.2.1 | TV2 |
| UC19 | Quản lý hồ sơ nhân viên | F1.2.3 | TV2 |

## 5. Quyết định nghiệp vụ của nhóm

- UC03 giao cho thu ngân ghi nhận tình trạng hàng trả. Tình trạng đó quyết định số lượng được nhập lại tồn bán được.
- UC08 và UC09 tách trách nhiệm lập và duyệt phiếu. Nhân viên kho ghi nhận số thực đếm. Quản lý quyết định có điều chỉnh tồn hay không.
- Báo cáo chia thành hai báo cáo của TV1, hai báo cáo của TV2 và một dashboard tổng hợp dùng dữ liệu cả hai phân hệ.
