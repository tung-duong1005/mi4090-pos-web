# Checklist bài tập lớn Hệ thống thông tin quản lý · MI4090

Nhóm 2 sinh viên · 20 tiêu chí × 0,5 điểm · Tổng 10 điểm

| Nhóm tiêu chí | Điểm tối đa |
|---|---:|
| 1. Khối lượng và chức năng | 2,0 |
| 2. Chất lượng sản phẩm | 2,0 |
| 3. Phân tích nghiệp vụ gắn với code | 1,5 |
| 4. Thiết kế, UML, OOP, SOLID và mẫu thiết kế | 3,0 |
| 5. Kiểm thử và bảo vệ | 1,5 |

TV1 và TV2 là hai thành viên. Mỗi người phụ trách trọn luồng từ phân tích đến cài đặt và kiểm thử. Hai phân hệ phải trao đổi dữ liệu và cùng xử lý giao dịch.

## Trục I — Hoàn thiện sản phẩm (4 điểm)

### 1. Khối lượng và chức năng

- [ ] **1.1 — Đủ quy mô.** Có ít nhất 6 nhánh cấp 2 trong sơ đồ phân cấp chức năng (BFD), 3 nhánh/người. Có ít nhất 8 ca sử dụng (UC), 4 UC/người, gồm ít nhất 4 giao dịch phức hợp và 2 luồng đi qua hai phân hệ. Có ít nhất 9 form nghiệp vụ trên một cửa sổ chính, mỗi người phụ trách ít nhất 4 form. Form danh mục đơn chiếm tối đa 40%. Chạy thử với ít nhất 3 vai trò.
- [ ] **1.2 — Form chính–chi tiết và báo cáo.** Có ít nhất 4 form Master–Detail, 2 form/người, nạp được dòng chi tiết và tính lại tổng khi dữ liệu đổi. Cả hai phân hệ lọc được theo nhiều điều kiện. Có ít nhất 5 báo cáo (2/người và 1 báo cáo hoặc dashboard tổng hợp hai phân hệ). Báo cáo khớp 100% số liệu nguồn, xuất Excel/PDF đúng font. Thử tạo giao dịch ở phân hệ thứ nhất và xem ngay kết quả ở báo cáo phân hệ thứ hai.
- [ ] **1.3 — Dữ liệu mẫu.** Một lệnh tạo ít nhất 120 bản ghi liên thông qua ít nhất 11 bảng chuẩn 3NF. Dữ liệu trải qua 2–3 kỳ/tháng theo cách ghi của phiếu, phủ ít nhất 3 vai trò và các trạng thái hoàn thành, hủy, quá hạn, công nợ. Chuẩn bị bảng tính tay để đối chiếu báo cáo sau khi khởi tạo lại CSDL.
- [ ] **1.4 — Đóng gói và Git.** Build và chạy trên máy sạch trong tối đa 3 phút, đưa cấu hình riêng của máy ra ngoài code. Có README, gói thực thi, slide, video 3–5 phút và `.gitignore`. Có ít nhất 24 commit thực chất trải trên ít nhất 3 tuần và 2 PR đã merge. Mỗi người đóng góp 40–60% mã logic theo Git; tối đa 60% commit nằm trong 48 giờ cuối. Có bảng phân công theo chức năng đầu–cuối.

### 2. Chất lượng sản phẩm

- [ ] **2.1 — Giao diện và kiểm tra đầu vào.** Dùng chung cửa sổ chính, font, màu và bố cục. Định dạng tiền `#,##0`, ngày `dd/MM/yyyy`. Phân biệt form danh mục và form nghiệp vụ. Kiểm tra dữ liệu cả ở form lẫn Domain/Service. Thử nhập sai ở cả hai phân hệ và kiểm tra dữ liệu sai bị chặn trước khi chuyển tiếp.
- [ ] **2.2 — Độ ổn định, bảo mật và giao dịch.** Chạy luồng liên phân hệ không treo hoặc văng ứng dụng. Hai người dùng chung hệ ngoại lệ, xử lý lỗi rõ ràng, không để khối catch rỗng. Băm mật khẩu và tham số hóa toàn bộ truy vấn có đầu vào. Thử gây lỗi ở bước sau và kiểm tra transaction đã hoàn tác toàn bộ thay đổi ở các bảng của cả hai phân hệ.
- [ ] **2.3 — Hiệu năng và cấu hình.** JOIN, lọc và báo cáo tổng hợp chạy mượt trên ít nhất 120 bản ghi. Tránh N+1, tức truy vấn danh sách rồi phát thêm một truy vấn cho từng dòng. Dùng một tệp cấu hình ngoài chung và có tệp mẫu. Đổi chuỗi kết nối tại một chỗ và tái lập CSDL bằng một thao tác.
- [ ] **2.4 — Chất lượng mã nguồn.** Tuân thủ cấu trúc Solution và quy ước đặt tên trong HuongdanXDHTTTQL, gồm Database, Resource, frm_dm_, frm_nv_. Hai người thống nhất tên lớp, hàm và form, tái sử dụng xử lý chung, dọn mã chết hoặc mã sinh thừa và có lịch sử review PR chéo.

## Trục II — Hiểu và giải thích được từ mô hình đến code (6 điểm)

### 3. Phân tích nghiệp vụ (1,5 điểm)

- [ ] **3.1 — Khảo sát, BFD và UC.** Khảo sát theo 4W+1H, thu thập biểu mẫu thực tế. Ánh xạ toàn bộ nhánh chức năng và UC sang menu, form hoặc Service. Làm được chiều ngược lại, chẳng hạn chỉ ra một cột trên bảng giao diện xuất phát từ trường nào trên biểu mẫu và thuộc nút BFD nào. Cả hai người nắm trọn ít nhất 2 UC liên phân hệ và chỉ được vị trí cần sửa nếu đổi bước duyệt.
- [ ] **3.2 — ERD và mô hình miền.** Một ERD chung có ít nhất 3 quan hệ nhiều–nhiều có thuộc tính. Chuyển thành ít nhất 13 lớp Entity/Domain thực chất, gồm ít nhất 3 lớp liên kết. Hai phân hệ thống nhất tên, đơn vị và trạng thái. Giải thích thuộc tính lịch sử và ảnh hưởng khi đổi quan hệ 1–n thành n–n.
- [ ] **3.3 — Quy tắc và phân quyền.** Có ít nhất 8 quy tắc nghiệp vụ, 4/người và ít nhất 2 quy tắc liên phân hệ. Cài ở Domain/Service và kiểm quyền tại tầng nghiệp vụ cho ít nhất 3 vai trò. Nêu được điều kiện trước khi gọi, kết quả sau khi chạy và người có quyền gọi. Thử gọi trực tiếp Service bằng tài khoản thiếu quyền. Cột đối chiếu của phiếu có ghi DFD ở mục này.

**Ví dụ truy vết cho POS.** BFD thể hiện các nhánh bán hàng và kho. UC thanh toán hóa đơn mô tả khi nào việc bán hàng dẫn đến giảm tồn. Một cột “Đơn giá bán” trên form tra cứu phải truy ngược được về dòng hàng trên phiếu bán gốc. Trong ERD, Hóa đơn và Sản phẩm có quan hệ nhiều–nhiều; Chi tiết hóa đơn giữ số lượng và đơn giá của lần bán đó.

### 4. Thiết kế, UML, OOP, SOLID và mẫu thiết kế (3 điểm)

- [ ] **4.1 — UML và CSDL.** Một UML tổng có ít nhất 20 lớp thực chất, thể hiện 6 loại quan hệ UML. Một schema CSDL chung có ít nhất 11 bảng 3NF, ít nhất 3 bảng liên kết nhiều–nhiều hoặc giao dịch và ít nhất 2 khóa ngoại nối hai phân hệ. Bảng danh mục đơn chiếm tối đa 40%. Kiểm tra 3 lớp bất kỳ có đại diện hai người, UML phải khớp code 100%. Giải thích kết tập, hợp thành và ảnh hưởng khi xóa bản ghi cha qua biên phân hệ.
- [ ] **4.2 — Sơ đồ hành vi và debugger.** Có ít nhất 4 sơ đồ Sequence/State, 2/người và ít nhất 1 sơ đồ liên phân hệ. Chuỗi gọi hàm, nhánh xử lý và điều kiện chuyển trạng thái phải khớp code. Mỗi người tự đặt breakpoint, đọc call stack qua hai phân hệ và thử một chuyển trạng thái bị cấm.
- [ ] **4.3 — Kiến trúc phân tầng.** Package Diagram thể hiện ít nhất 3 tầng, hai module và Domain dùng chung. Tách SQL khỏi form, tách UI/SQL khỏi lõi nghiệp vụ và tránh phụ thuộc vòng. Kiểm tra qua project reference, using/import và chạy test không cần giao diện. Giải thích lý do chọn ranh giới giữa hai module.
- [ ] **4.4 — Đóng gói và đa hình.** Bảo vệ điều kiện luôn phải đúng của đối tượng tại constructor hoặc phương thức. Tránh công khai dữ liệu mà bên ngoài có thể tự sửa. Có ít nhất 2 nhánh kế thừa/đa hình thỏa nguyên lý thay thế Liskov (LSP). Chứng minh lớp con của TV2 chạy đúng trong hàm nhận kiểu cha của TV1, không dùng is/as/ép kiểu để chọn hành vi.
- [ ] **4.5 — SOLID và hợp đồng giữa hai phân hệ.** Áp dụng SRP, ISP, DIP/DI. Hai phân hệ giao tiếp qua interface/event, truyền phụ thuộc qua constructor và lắp ghép ở điểm khởi tạo chung. Không gọi cứng lớp cụ thể hay truy vấn thẳng bảng nội bộ của phân hệ kia. Thử thay cài đặt của TV2 và kiểm tra TV1 vẫn biên dịch.
- [ ] **4.6 — Mẫu GoF và mở rộng trực tiếp.** Ít nhất 3 mẫu GoF thuộc ít nhất 2 nhóm mẫu (khuyến khích đủ 3 nhóm), mỗi người ít nhất 1 mẫu, có ít nhất 1 mẫu nối hai phân hệ. Repository và MVC không được tính vào chỉ tiêu GoF. Cả hai giải thích được vai trò các lớp và đánh đổi của mẫu. Khi bảo vệ, mỗi người tự thêm một lớp cụ thể mà không sửa code cũ, tắt AI. Phiếu ghi 2–3 phút tại chỗ hoặc 5–7 phút cuốn chiếu.

### 5. Kiểm thử và bảo vệ (1,5 điểm)

- [ ] **5.1 — Ma trận ca kiểm thử và unit test.** Ghi mã ca, người phụ trách và quy tắc cần kiểm. Phủ phân lớp tương đương, giá trị biên, trạng thái và ngoại lệ. Có ít nhất 18 unit test theo AAA (chuẩn bị, thực hiện, kiểm tra), 9 test/người. Mỗi người có ít nhất 2 ca dùng Mock/Stub cho interface của phân hệ kia. Unit test chạy độc lập với CSDL và cài đặt thật của bạn cùng nhóm.
- [ ] **5.2 — Integration test.** Ít nhất 8 ca chạy với code thật của hai phân hệ và bộ seed ít nhất 120 dòng. Mỗi nhóm sau có ít nhất 2 ca: luồng liên phân hệ, hoàn tác giao dịch sau lỗi, báo cáo liên phân hệ khớp tính tay, và kiểm quyền tại Service trên ít nhất 3 vai trò. Kiểm cả ảnh hưởng của giao dịch đã hủy lên số liệu.
- [ ] **5.3 — Chạy test và sửa lỗi trực tiếp.** Chạy toàn bộ ít nhất 26 test, đạt 100%. Khi giảng viên tiêm lỗi, dùng test hiện có để phát hiện hoặc viết regression test trong 3–5 phút. Cả hai dùng debugger và call stack để tìm nguyên nhân, sửa rồi chạy lại toàn bộ test. Mỗi người giải thích được code và test của người kia.

## Điền phiếu và tính điểm

- **Đầu phiếu:** Ghi mã nhóm, đề tài, họ tên, MSSV, Git và số lượng thực tế của từng hạng mục. Ghi phần đóng góp riêng của TV1/TV2 ở các chỉ tiêu có chia theo người.
- **Từng mục:** Chọn X khi đã hoàn thiện. Minh chứng theo mẫu `[TV1]/[TV2] | Trang báo cáo | Tệp hoặc lớp | Chỉ số thực tế`. Ô điểm chữ để trống nghĩa là chưa chấm.
- **Đối chiếu:** A → B là từ tài liệu chỉ ra code hoặc hành vi thực chạy. B → A là từ code truy ngược về tài liệu. Δ là thử thay đổi hoặc tiêm lỗi. W là giải thích đánh đổi thiết kế. Live là thao tác trực tiếp khi bảo vệ.

| Điểm chữ | Điểm cho một tiêu chí |
|---|---:|
| A | 0,500 |
| B | 0,375 |
| C | 0,250 |
| D | 0,125 |
| F | 0,000 |

| Cổng chặn | Điều kiện | Trần điểm nhóm |
|---|---|---:|
| Sản phẩm | PASS, đạt ít nhất 80% khối lượng | 10 |
| Sản phẩm | WARN_SCOPE, thiếu hơn 20% khối lượng hoặc có lỗi nặng | 6 |
| Sản phẩm | FAIL_RUN, sản phẩm không chạy được | 3,5 |
| Hiểu sâu | Trục II dưới 1,80/6 | 3,5 |
| Hiểu sâu | Trục II từ 1,80 đến dưới 3,00/6 | 6,5 |
| Hiểu sâu | Trục II từ 3,00/6 trở lên | 10 |

Cổng hiểu sâu kích hoạt khi đã chấm đủ 12 mục Trục II. Điểm chốt nhóm làm tròn theo bước 0,5. Hệ số cá nhân từ 0 đến 1 căn cứ đóng góp Git và phần vấn đáp, mở rộng code, debug trực tiếp.

Nguồn đối chiếu: bản CSV của phiếu Checklist_BTL_HTTTQL_v2026. Phiếu dẫn sang Sheet 3 “Rubric A-F & Vấn đáp” cho mô tả chi tiết các mức và ngân hàng câu hỏi.
