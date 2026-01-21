# Student Attendance System (Python • Console • SQLite)

## 1) Giới thiệu
**Student Attendance System (SAS)** là hệ thống điểm danh sinh viên chạy **console (Text UI / menu)** với **3 vai trò**: **Student**, **Lecturer**, **Administrator**. Hệ thống hỗ trợ quy trình: **đăng nhập → tạo buổi điểm danh (session) → sinh viên check-in (PIN tuỳ chọn) → giảng viên ghi/điều chỉnh trạng thái → tổng hợp → xuất báo cáo Excel**, kèm **đơn xin vắng/trễ** và **cảnh báo điểm danh**.

## 2) Tech stack
- **Python 3.10+** (khuyến nghị 3.11)
- **SQLite** (lưu dữ liệu)
- **openpyxl** (xuất báo cáo Excel)
- **pytest** (unit test)
- **Docker** (đóng gói chạy)
- Công cụ: **GitHub** (quản lý source/nhóm), **VS Code** (IDE), **Excel** (test cases), **MantisBT** (bug tracking)

## 3) Vai trò & quyền hạn
| Vai trò | Quyền / chức năng chính |
|---|---|
| **Student** | Check-in điểm danh, xem lịch sử điểm danh, gửi yêu cầu vắng/trễ, xem cảnh báo |
| **Lecturer** | Tạo session (PIN tuỳ chọn), ghi/điều chỉnh điểm danh, duyệt/từ chối yêu cầu vắng/trễ, tổng hợp & xuất Excel |
| **Administrator** | Tìm kiếm & quản lý dữ liệu điểm danh (thêm/sửa/xoá bản ghi khi cần) |

---

## 4) Bảng Use Case (Chức năng & Công dụng)

| ID | Use Case | Actor chính | Chức năng | Công dụng |
|---:|---|---|---|---|
| UC01 | Login | Student/Lecturer/Admin | Đăng nhập, xác thực, điều hướng theo vai trò | Bảo đảm đúng người – đúng quyền |
| UC02 | Take Attendance (Check-in) | Student | Check-in vào session đang mở; nếu bật PIN phải nhập đúng | Ghi nhận nhanh, giảm gian lận |
| UC03 | View Attendance | Student/Lecturer | Xem lịch sử/chi tiết điểm danh theo lớp/session | Theo dõi minh bạch trạng thái |
| UC04 | Submit Absence/Late Request | Student | Gửi đơn vắng/trễ (lý do, minh chứng nếu có) | Xử lý ngoại lệ hợp lệ |
| UC05 | Search Attendance | Administrator | Tìm theo StudentID/SessionID/Class/Date range | Tra cứu nhanh khi kiểm tra |
| UC06 | Create Attendance Session | Lecturer | Tạo session (ngày/giờ/duration), trạng thái OPEN, PIN tuỳ chọn (4–6 chữ số) | Mở “cửa sổ” điểm danh |
| UC07 | Record Attendance | Lecturer/Admin | Ghi/điều chỉnh trạng thái (Present/Late/Absent/Excused), batch “Mark all Present”, đóng session | Chuẩn hoá dữ liệu điểm danh |
| UC08 | Approve Absence/Late Request | Lecturer | Duyệt đơn (cập nhật trạng thái theo quy định) | Hợp thức hoá ngoại lệ |
| UC09 | Reject Absence/Late Request | Lecturer | Từ chối đơn (cập nhật trạng thái theo quy định) | Giữ kỷ luật điểm danh |
| UC10 | Manage Attendance | Administrator | Thêm/sửa/xoá bản ghi sai/thiếu/trùng | Dữ liệu chính xác cho báo cáo |
| UC11 | View Attendance Warning | Student | Xem cảnh báo khi vượt ngưỡng vắng/trễ | Nhắc nhở để tránh vi phạm |
| UC12 | Summarize Attendance | Lecturer | Tổng hợp số buổi Present/Late/Absent theo SV/lớp | Theo dõi lớp, làm báo cáo |
| UC13 | Export Attendance Report to Excel | Lecturer | Xuất báo cáo Excel theo lớp/khoảng thời gian | Lưu trữ/chia sẻ/nộp báo cáo |

---

## 5) Giao diện Console (đúng menu & màn hình theo yêu cầu)

### 5.1 Main Menu
```text
==================================================
            STUDENT ATTENDANCE SYSTEM
==================================================
1. Login
2. Exit
--------------------------------------------------
Selection: _
```

### 5.2 Login (password masked)
```text
[LOGIN]
Username: _
Password: _  (masked input)
--------------------------------------------------
• If credentials are valid: redirect to the role dashboard.
• If invalid: show an error message and allow retry.
```

### 5.3 Student Dashboard
```text
[STUDENT DASHBOARD]
User: <StudentName> (ID: <StudentID>)
Warnings: <n> | Pending Requests: <n>
--------------------------------------------------
1. Take Attendance (Check-in)
2. View Attendance
3. Submit Absence/Late Request
4. View Attendance Warnings
0. Logout
--------------------------------------------------
Selection: _
```

### 5.4 Student — Take Attendance
```text
[TAKE ATTENDANCE]
Enter Session ID: _
Enter PIN (if required): _
--------------------------------------------------
• Validate: session exists, session is open, correct PIN (if enabled), and not checked-in yet.
• Success: record timestamp + “Check-in successful”.
• Failure: show reason (“Invalid PIN”, “Session closed/expired”, “Already checked-in”, ...).
```

### 5.5 Student — View Attendance
```text
[VIEW ATTENDANCE]
Enter Course/Class ID (or leave blank to list all): _
Optional Date Range: From (YYYY-MM-DD): _  To (YYYY-MM-DD): _
--------------------------------------------------
```

### 5.6 Student — Submit Absence/Late Request
```text
[SUBMIT REQUEST]
Enter Session ID: _
Request Type: 1. Absent   2. Late
Reason (text): _
Optional Evidence File Path (leave blank if none): _
Confirm submission (Y/N): _
--------------------------------------------------
• Save request with status=PENDING and notify lecturer.
```

### 5.7 Student — View Attendance Warnings
```text
[WARNINGS]
WarningID | Date       | Course/Class | Message
--------- | ---------- | ----------- | ------------------------------
<W003>    | 2026-01-14 | <CSE101>     | Absence threshold reached (3)
--------------------------------------------------
• Warnings are generated automatically when configured thresholds are exceeded.
```

### 5.8 Lecturer Dashboard
```text
[LECTURER DASHBOARD]
User: <LecturerName> (ID: <LecturerID>)
Pending Requests: <n>
--------------------------------------------------
1. Create Attendance Session
2. Record Attendance
3. Approve/Reject Absence/Late Requests
4. Summarize Attendance
5. Export Attendance Report (Excel)
0. Logout
--------------------------------------------------
Selection: _
```

### 5.9 Lecturer — Create Attendance Session
```text
[CREATE SESSION]
Enter Course/Class ID: _
Session Date (YYYY-MM-DD): _
Start Time (HH:MM): _
Duration (minutes): _
Require PIN? (Y/N): _
If Yes, enter PIN (4–6 digits) or leave blank to auto-generate: _
--------------------------------------------------
Output:
Session created successfully.
Session ID: <S123>
PIN (if enabled): <123456>
Status: OPEN
```

### 5.10 Lecturer — Record Attendance
```text
[RECORD ATTENDANCE]
Enter Session ID: _
--------------------------------------------------
StudentID | StudentName | Current Status
--------- | ----------- | --------------
<SV001>   | <A>         | Present
<SV002>   | <B>         | Absent
<SV003>   | <C>         | Late
--------------------------------------------------
Actions:
1. Update a student status
2. Mark all as Present (batch)
3. Close session
0. Back
Selection: _
```

### 5.11 Lecturer — Approve/Reject Requests
```text
[PROCESS REQUESTS]
Filter: 1. Pending only  2. All
Selection: _
--------------------------------------------------
RequestID | StudentID | SessionID | Type  | Reason (short) | Status
--------- | --------- | --------- | ----- | -------------- | ------
<R012>    | <SV003>   | <S002>    | Late  | Traffic jam... | PENDING
--------------------------------------------------
Enter RequestID to process (or 0 to back): _
Action: 1. Approve  2. Reject
Lecturer Comment (optional): _
Confirm (Y/N): _
--------------------------------------------------
• Update status and notify student.
```

### 5.12 Lecturer — Summarize Attendance
```text
[SUMMARIZE ATTENDANCE]
Enter Course/Class ID: _
Optional Date Range: From (YYYY-MM-DD): _  To (YYYY-MM-DD): _
--------------------------------------------------
```

### 5.13 Lecturer — Export Excel
```text
[EXPORT REPORT]
Enter Course/Class ID: _
Optional Date Range: From (YYYY-MM-DD): _  To (YYYY-MM-DD): _
Enter output file path (e.g., reports/CSE101_Attendance.xlsx): _
Confirm export (Y/N): _
--------------------------------------------------
Output: Export completed successfully.
```

### 5.14 Administrator Dashboard
```text
[ADMINISTRATOR DASHBOARD]
User: <AdminName> (ID: <AdminID>)
--------------------------------------------------
1. Search Attendance
2. Manage Attendance
0. Logout
--------------------------------------------------
Selection: _
```

### 5.15 Admin — Search Attendance
```text
[SEARCH ATTENDANCE]
Search by: 1. StudentID  2. SessionID  3. Course/Class  4. Date Range
Selection: _
Enter keyword/value: _
--------------------------------------------------
```

### 5.16 Admin — Manage Attendance
```text
[MANAGE ATTENDANCE]
Actions:
1. Add missing attendance record
2. Edit attendance status
3. Delete duplicated/incorrect record
0. Back
--------------------------------------------------
Selection: _
Example (Edit):
Enter Session ID: _
Enter Student ID: _
New Status: 1. Present  2. Late  3. Absent  4. Excused
Reason/Note: _
Confirm (Y/N): _
```

### 5.17 Thông báo lỗi/validation phổ biến
- Invalid menu selection. Please try again.
- Username or password is incorrect.
- Session ID not found.
- Session is closed or expired.
- Invalid or expired PIN.
- Attendance already recorded for this student in the session.
- Request submission failed: missing required information.
- Export failed: invalid output path or file is in use.

---

## 6) Mô hình lớp (Class Model) & kiến trúc code

### 6.1 Các class domain chính
- **User** (class chính)
  - **Student** (class phụ 1)
  - **Lecturer** (class phụ 2)
  - **Administrator** (class phụ 3)  
  ➜ **1 class chính + 3 class phụ**

- **AttendanceSession**
- **AttendanceRecord**
- **AbsenceLateRequest**
- **Warning**
- (tuỳ thiết kế Stage 2) **Class/Course**, **Enrollment**

### 6.2 Kiến trúc module/class theo tầng (khuyến nghị để dễ test Stage 4)
| Tầng | Class/module chính | Số “class phụ” gợi ý |
|---|---|---:|
| UI | `Menus`, `Prompts` | 2 |
| Services (business) | `AuthService`, `SessionService`, `AttendanceService`, `RequestService`, `ReportService`, `AdminService` | 6 |
| Repositories (DB) | `UserRepo`, `ClassRepo`, `SessionRepo`, `AttendanceRepo`, `RequestRepo`, `WarningRepo` | 6 |
| Utils | `security`, `validators`, `time_utils`, `file_utils` | 4 |

> Bạn có thể đổi tên class/module, nhưng nên giữ đủ trách nhiệm nghiệp vụ như bảng trên.

---

## 7) Yêu cầu phi chức năng (tóm tắt để triển khai đúng)
- **Bảo mật**: mật khẩu phải **hash/encode**, không lưu plain-text.
- **Khoá đăng nhập**: sau **5 lần đăng nhập sai liên tiếp**, tài khoản bị khoá tạm thời.
- **Hiệu năng**: phản hồi yêu cầu người dùng trong **≤ 2 giây** (bình thường); **Login ≤ 3 giây**; **check-in ≤ 2 giây/request**.
- **Đồng thời**: hỗ trợ **≥ 100** đăng nhập đồng thời vào giờ điểm danh; **≥ 200** người dùng đồng thời không suy giảm đáng kể.
- **Độ tin cậy dữ liệu**: không mất các dữ liệu quan trọng (attendance records, requests, warnings, reports).

---

## 8) Cấu trúc thư mục (đề xuất)
```text
.
├── src/
│   ├── main.py
│   ├── ui/                 # menu theo role, màn hình console
│   ├── services/           # nghiệp vụ (session, check-in, requests, report)
│   ├── repositories/       # thao tác SQLite
│   ├── models/             # entity/dto/enum
│   └── utils/              # validate, security (hash/lock), time, file
├── db/
│   ├── schema.sql
│   └── seed.sql
├── data/                   # sas.db (SQLite)
├── reports/                # file Excel xuất ra
├── tests/                  # pytest
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 9) Cài đặt & chạy (Local)

### 9.1 Tạo môi trường & cài phụ thuộc
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
```

### 9.2 Khởi tạo database
Ví dụ nếu bạn dùng file SQL:
```bash
sqlite3 data/sas.db < db/schema.sql
sqlite3 data/sas.db < db/seed.sql
```

### 9.3 Chạy ứng dụng
```bash
python -m src.main
```

---

## 10) Testing (Stage 4)

### 10.1 Unit test (pytest)
```bash
pytest -q
```

### 10.2 Manual test cases (Excel)
Tạo `testcases.xlsx` (hoặc Google Sheets rồi export) với các cột:
- `TC_ID`
- `Module/UseCase`
- `Preconditions`
- `Steps`
- `Input Data`
- `Expected Result`
- `Actual Result`
- `Pass/Fail`
- `Bug ID`
- `Notes`

---

## 11) Bug tracking (Stage 4) — MantisBT

### 11.1 Quy trình quản lý bug
1. Test case FAIL trong Excel → tạo bug trong Mantis (đặt tiêu đề có `TC_ID`)
2. Tạo branch: `fix/bug-<id>`
3. Commit/PR lên GitHub → review → merge
4. Retest TC → PASS → Close bug

### 11.2 Nội dung bug cần có
- Summary: `[TC09] Invalid PIN still records attendance`
- Steps to reproduce: copy từ Excel (Steps + Input)
- Expected vs Actual
- Severity/Priority
- Attachment: log/ảnh màn hình console (nếu có)

---

## 12) Docker (Packaging & Deployment)

### 12.1 Build & run
```bash
docker build -t sas:latest .
docker run --rm -it sas:latest
```

### 12.2 Gợi ý giữ dữ liệu SQLite
Mount thư mục `data/` (chứa `sas.db`) ra ngoài container để không mất dữ liệu khi restart:
```bash
docker run --rm -it -v "$PWD/data:/app/data" sas:latest
```

---

## 13) Quy ước GitHub (làm nhóm)
- Branch: `main`, `dev`, `feature/<name>`, `fix/bug-<id>`
- Commit message: `feat: ...`, `fix: ...`, `test: ...`, `docs: ...`
- Feature → Pull Request → review → merge

---

## 14) License
Dự án phục vụ mục đích học tập.
