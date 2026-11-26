# POS web · Python và PostgreSQL

Bản này thay tầng SQLite của mục 4.3 bằng PostgreSQL. Backend Python tiếp tục dùng WSGI và các service Quầy, Kho. Trình duyệt gửi JSON qua cùng hai endpoint bán và trả hàng. Phạm vi bài tập là một cửa hàng, một quầy thu ngân và một kho.

## Chạy khung dự án bằng Docker Compose

1. Sao chép tệp .env.example thành .env và đặt POSTGRES_PASSWORD bằng một chuỗi chữ và số riêng.
2. Chạy **docker compose up --build -d**. PostgreSQL tự tạo schema và trigger ở lần khởi động volume mới.
3. Chạy **docker compose exec web python manage.py seed** trên database demo trống. Chạy **docker compose exec web python manage.py check** để kiểm tra.
4. Địa chỉ API mặc định là http://localhost:8000/api/ban và http://localhost:8000/api/tra. Các yêu cầu ghi dùng POST và cần danh tính do middleware cung cấp. Hai API này là phạm vi web đang có.

## Theo dõi bài tập lớn

- [Checklist gốc](docs/Checklist_BTL_HTTTQL_2026.md) và [bảng minh chứng theo từng tiêu chí](docs/minh-chung.md).
- [Phân công và thiết kế form](frontend/forms/README.md), [ma trận ca kiểm thử](docs/kiem-thu/ma-tran.csv) và [kết quả tính tay theo tháng](docs/kiem-thu/doi-chieu-seed.csv).
- Hồ sơ khảo sát trong **docs/khao-sat/**, các tài liệu phân tích trong **docs/phan-tich/**. Slide khảo sát–thiết kế đã có và kịch bản quay video nằm trong **docs/bao-ve/**.
- Chạy unit test bằng **python -m unittest discover -s tests/unit -v**. Workflow GitHub chạy thêm các bài tích hợp trên PostgreSQL riêng khi push hoặc mở PR.
- Database/ chứa lược đồ, trigger và seed; Resource/ dành cho tài nguyên giao diện, mẫu in. Frontend dùng JavaScript; application/, domain/, presentation/ và infrastructure/ là các package của backend Python.

## Khởi động trên Windows

Cần Python 3.10 trở lên, PostgreSQL 16 trở lên và một database trống. Ví dụ dưới dùng database `pos_web` đã được tạo với encoding UTF8 và role `pos_app` có quyền tạo bảng trong schema đích. Từ thư mục chứa tệp này, chạy PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
$env:DATABASE_URL = "postgresql://pos_app@localhost:5432/pos_web"
```

Đặt mật khẩu kết nối bằng tệp mật khẩu PostgreSQL của máy hoặc biến môi trường `PGPASSWORD` trong phiên làm việc. Nếu role và database chưa có, có thể chạy `createuser -U postgres -P pos_app` và `createdb -U postgres -O pos_app -E UTF8 pos_web` bằng bộ công cụ PostgreSQL.

**Chọn một trong hai cách tạo dữ liệu**:

| Trường hợp | Lệnh PowerShell |
|---|---|
| Bắt đầu với cửa hàng trống | `.\.venv\Scripts\python manage.py init` |
| Đã có tệp SQLite từ mục 4.1 hoặc bản web 4.3 | `.\.venv\Scripts\python manage.py import-sqlite "D:\POS\pos_web.sqlite"` |

Sau đó chạy `.\.venv\Scripts\python manage.py check` để xem tên database, số phiếu bán, số phiếu trả, số khóa yêu cầu và số mã hàng. Có thể xem trực tiếp các bảng và view bằng pgAdmin. Cả hai lệnh khởi tạo đều dành cho schema mới. Nếu schema đã có bảng trùng tên, thao tác dừng và hoàn tác.

**Điểm vào web** là `wsgi:application`. Ví dụ với Waitress trên Windows:

```powershell
.\.venv\Scripts\python -m pip install waitress
.\.venv\Scripts\waitress-serve --listen=127.0.0.1:8000 wsgi:application
```

Host hoặc middleware đăng nhập cần xác thực người dùng và gán `REMOTE_USER` trong WSGI environ bằng `tai_khoan.ma_tk`. Chạy lệnh trên riêng lẻ sẽ nhận HTTP 401 khi gửi phiếu. Đây là điểm tích hợp đăng nhập đã có trong thiết kế. Frontend trong gói là module gọi API bán/trả.

## Kiến trúc và dữ liệu

| Thành phần | Vai trò |
|---|---|
| `frontend/api_client.mjs` | Gửi yêu cầu HTTP, chuyển cùng khóa khi thử lại. |
| `presentation/` | Đọc JSON, kiểm hợp đồng HTTP và trả mã lỗi. |
| `application/` và `domain/` | Mở/bàn giao/chốt ca, bán, trả, thu chi, đổi giá, nhập, kiểm kê và phê duyệt. Báo cáo ca chỉ cộng phần tác động đến tiền mặt. |
| `infrastructure/postgres.py` | Dùng Psycopg 3, mở kết nối theo request, ánh xạ dòng dữ liệu, kiểm soát giao dịch. |
| `Database/01_schema.sql` | 14 bảng nghiệp vụ, bảng `web_yeu_cau`, 22 khóa ngoại, chỉ mục và ba view `v_dong_tra`, `v_bien_dong`, `v_ton`. |
| `Database/02_rules.sql` | Trigger PostgreSQL bảo vệ trạng thái, tính bất biến của chứng từ, ca mở, tồn, lượng hoàn và mốc kiểm kê. |
| `Package_Diagram_POS_Web.svg` và `UML.md` | Sơ đồ package và lớp để đối chiếu với mục 4.3. |

Số tiền lưu bằng số nguyên đồng (`BIGINT`). Thời điểm lưu bằng `TIMESTAMPTZ`. Các mã phiếu, mã hàng và mã dòng tiếp tục dùng `TEXT`. Bốn bảng dòng có thêm `thu_tu` kiểu identity để giữ thứ tự nhập khi đọc lại phiếu.

**Giao dịch đồng thời.** Lần ghi đầu tiên trong một giao dịch nghiệp vụ lấy khóa `pg_advisory_xact_lock(41702, 4301)`. Trong phạm vi một quầy, các lần ghi lần lượt kiểm tra trạng thái đã commit gần nhất theo `READ COMMITTED`. Việc kiểm tồn, tạo phiếu, ghi nhật ký và lưu khóa yêu cầu nằm trong cùng giao dịch. Khóa được nhả khi commit hoặc rollback. Nhân viên vẫn có thể đọc dữ liệu khi quầy đang ghi. Với ứng dụng mở rộng nhiều quầy, chiến lược khóa ghi chung này sẽ giới hạn thông lượng.

## Hợp đồng HTTP

| Nghiệp vụ | Đường dẫn | JSON minh họa |
|---|---|---|
| UC02 bán hàng | `POST /api/ban` | `{"ca":"C","pt":"CK","dong":[["S",2]]}` |
| UC03 trả hàng | `POST /api/tra` | `{"ca":"C","pt":"TM","goc":"B","dong":[["D1",1,"TOT"]]}` |

Cả hai yêu cầu gửi `Content-Type: application/json` và `Idempotency-Key`. Trong ví dụ trả hàng, `B` là mã phiếu bán đã hoàn tất và `D1` là mã dòng bán thuộc chính phiếu đó. Bán mới trả 201 và `{"ma_phieu":"…"}`. Thử lại cùng nội dung và khóa trả 200 với mã phiếu cũ. Dùng lại khóa với nội dung khác trả 409. Nếu hết thời gian chờ khóa, API trả 503 và `Retry-After: 1`. Frontend dùng lại cùng khóa khi thử lại.

## Chuyển dữ liệu từ SQLite

Dừng ghi ở ứng dụng cũ trước khi lấy bản chụp cuối cùng. Tệp SQLite gốc do người dùng cung cấp mở ở chế độ chỉ đọc. Công cụ kiểm tính toàn vẹn và khóa ngoại nguồn, tạo bảng đích, sao chép theo thứ tự phụ thuộc rồi kiểm từng trường và từng số dư `v_ton` trước khi cài trigger và commit. Khóa ngoại, `CHECK` và `UNIQUE` có hiệu lực khi nạp. Trigger yêu cầu bắt đầu bằng phiếu nháp được cài sau khi nạp để giữ lịch sử các phiếu đã chốt. Mọi thao tác trên đích nằm trong một giao dịch.

Các trường thời gian nguồn có múi giờ được giữ đúng thời điểm. Với dữ liệu cũ chỉ có ngày hoặc thiếu múi giờ, công cụ hiểu là UTC theo quy ước của backend 4.3. Nếu nguồn thực tế đã ghi giờ địa phương thiếu offset, cần xác định lại múi giờ trước khi nhập. Bản 4.1 có 14 bảng sẽ nhận bảng khóa yêu cầu trống. Bản 4.3 giữ cả mã phiếu và hàm băm đã lưu. Nếu tồn, giá trị từng trường hoặc số dòng lệch, giao dịch hoàn tác.

## Kiểm tra và bảo vệ bài

**Đã chạy trên PostgreSQL 18.7**: tạo schema, hàm và trigger, chạy `Database/test_rules.sql` bằng backend PostgreSQL ở chế độ single-user. Kịch bản bán bằng chuyển khoản, trả một hàng tốt và một hàng hỏng sau khi giá đổi, rồi nhập thêm hàng đã cho tồn lần lượt 0, 1 và 2. Kịch bản cũng kiểm tra chặn sửa dòng đã chốt, bán âm kho, trùng khóa, trả quá số đã bán, duyệt kiểm kê theo mốc cũ và hoàn tác khi lỗi. Hai kiểm thử đối chiếu UML–code và chiều phụ thuộc giữa các tầng đã chạy thành công.

**Kiểm thử tích hợp để chạy với PostgreSQL đang phục vụ kết nối**:

```powershell
$env:POS_TEST_DSN = "postgresql://pos_app@localhost:5432/pos_web_test"
.\.venv\Scripts\python -m unittest -v kiem_chung kiem_thu_web kiem_tra_43 kiem_thu_chuyen_doi
.\.venv\Scripts\python ghi_debug.py
```

Tạo trước database kiểm thử và cấp cho role quyền tạo schema. Mỗi ca dùng schema ngẫu nhiên, rồi dọn schema do chính ca đó tạo. Bộ kiểm thử gồm hai giao dịch cùng khóa, hai yêu cầu tranh lượng tồn cuối, rollback khi lưu khóa lỗi, thử lại sau khi khóa tài khoản, kiểm thử qua WSGI và nhập SQLite có lịch sử. `ghi_debug.py` tạo log PDB cho hai thành viên. Môi trường tạo gói chặn kết nối TCP nội bộ nên các ca cần Psycopg kết nối máy chủ và hai log debugger chưa được xác nhận. Tệp `fixtures/legacy_empty.sqlite` chỉ dùng làm đầu vào cho kiểm thử nhập dữ liệu.

Tài liệu đối chiếu: [Quản lý giao dịch trong Psycopg 3](https://www.psycopg.org/psycopg3/docs/basic/transactions.html) · [Khóa trong PostgreSQL](https://www.postgresql.org/docs/18/explicit-locking.html).

### FastAPI

Chạy `docker compose up --build`, mở Swagger UI tại `http://localhost:8000/docs`.
Ứng dụng cung cấp `POST /api/ban` và `POST /api/tra`. Để ghi phiếu, middleware
xác thực của host phải gán mã tài khoản vào `request.state.ma_tk`. Nếu chưa
tích hợp middleware, hai endpoint trả 401. Mỗi lần lập phiếu cần một
`Idempotency-Key`; dùng lại khóa khi gửi lại cùng yêu cầu.
