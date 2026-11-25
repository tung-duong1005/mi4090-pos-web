# Bảng minh chứng MI4090

Điền phiên bản commit, trang báo cáo và họ tên thật khi nghiệm thu. TV1 phụ trách Quầy từ UC01–UC05. TV2 phụ trách Kho và quản trị từ UC06–UC10. Cả hai cùng kiểm tra luồng UC02 và UC03. Các phân công nêu trong repo là đề xuất.

| Mục | Minh chứng trong repo | Việc cần xác nhận khi nộp |
|---|---|---|
| 1.1 | [BFD](phan-tich/BFD_POS.md), [UC](phan-tich/Use_Case_POS.md), [danh mục form](../frontend/forms/README.md) | Chạy ít nhất 9 form trên khung chính với ít nhất 3 vai trò. |
| 1.2 | Bốn form chính–chi tiết trong danh mục, bảng đối chiếu seed tại `kiem-thu/` | Cài tính tổng, lọc, 5 báo cáo và xuất Excel/PDF. |
| 1.3 | `Database/03_seed_demo.sql`, [đối chiếu theo tháng](kiem-thu/doi-chieu-seed.csv) | Seed có chứng từ hoàn thành và hủy. Hai yêu cầu quá hạn/công nợ cần đối chiếu lại phạm vi POS đã duyệt. |
| 1.4 | README, Dockerfile, compose.yaml, .gitignore, [slide khảo sát–thiết kế](bao-ve/POS-Khao-sat-Phan-tich-Thiet-ke.pptx), [kịch bản](bao-ve/kich-ban-video.md), mẫu PR | Bổ sung video thật, đóng gói bản cuối và đo thời gian chạy trên máy sạch. Hai người tích lũy ít nhất 24 commit trong ít nhất 3 tuần và 2 PR đã merge. |
| 2.1 | `frontend/forms/`, `frontend/api_client.mjs`, `presentation/http.py` | Hoàn thiện khung màn hình chung, định dạng và kiểm dữ liệu nhập. |
| 2.2 | `bootstrap.py`, `application/phien.py`, `infrastructure/postgres.py`, `kiem_thu_web.py` | Tích hợp đăng nhập, băm mật khẩu, thử lỗi và đối chiếu rollback. |
| 2.3 | `.env.example`, `Database/01_schema.sql`, `manage.py` | Đo trên seed, kiểm truy vấn N+1 và thời gian báo cáo. |
| 2.4 | `Database/`, `Resource/`, quy ước `frm_nv_` và `frm_dm_` ở frontend | Review chéo từng PR và đối chiếu quy ước của môn. |
| 3.1 | `khao-sat/`, BFD và UC ở `phan-tich/` | Truy vết menu, cột trên form thực tế về biểu mẫu và BFD. |
| 3.2 | [ERD và mô hình miền](phan-tich/ERD_Mo_hinh_mien_POS.md), `domain/` | Đối chiếu tên, đơn vị và thuộc tính lịch sử giữa hai phân hệ. |
| 3.3 | [Quy tắc và phân quyền](phan-tich/Quy_tac_va_phan_quyen_POS.md), `application/` | Chạy lại ca kiểm quyền bằng cách gọi trực tiếp service. |
| 4.1 | [UML](../UML.md), `Database/01_schema.sql`, `kiem_chung.py` | Mỗi thành viên giải thích các quan hệ và thử xóa qua biên phân hệ. |
| 4.2 | [Bốn sơ đồ hành vi](thiet-ke/So_do_hanh_vi.md), `demo42.py`, `ghi_debug.py` | Tạo log PDB trên bản PostgreSQL đang chạy và trình bày call stack. |
| 4.3 | [Package Diagram](../Package_Diagram_POS_Web.svg), `kiem_tra_43.py` | Đối chiếu import và ranh giới module khi tích hợp màn hình. |
| 4.4 | `domain/__init__.py`, các ca tác động quỹ ở `tests/unit/` | Bổ sung bằng chứng bảo vệ invariant và hai nhánh đa hình theo LSP. |
| 4.5 | `application/ports.py`, `bootstrap.py` | Thử thay cài đặt qua interface và ghi kết quả. |
| 4.6 | Thiết kế hiện tại có repository và các service | Bổ sung minh chứng ba mẫu GoF theo hai nhóm và bài mở rộng tại chỗ. |
| 5.1 | [Ma trận ca kiểm](kiem-thu/ma-tran.csv), `tests/unit/` | Sáu unit test ban đầu. Hoàn thiện 18 ca, 9/người và các ca dùng mock/stub theo checklist. |
| 5.2 | `kiem_chung.py`, `kiem_thu_web.py`, `kiem_thu_chuyen_doi.py`, bộ seed | Đối chiếu đủ bốn nhóm integration test, mỗi nhóm ít nhất hai ca trên dữ liệu đúng quy mô. |
| 5.3 | `.github/workflows/tests.yml`, lệnh chạy test trong README | Ghi số test đạt trên commit nộp và minh chứng sửa lỗi trực tiếp. |

Các tài liệu phân tích và slide được giữ theo giai đoạn lập. Với vị trí lớp, tên adapter và schema vật lý, dùng UML, Package Diagram và Database của repo. Với báo cáo từ bộ seed, mỗi tháng có 6 phiếu tiền mặt và 5 phiếu chuyển khoản đã chốt, mỗi phiếu 43.000 đồng. Quỹ cuối ca bằng 100.000 + 258.000 − 25.000 − 10.000 = 323.000 đồng.
