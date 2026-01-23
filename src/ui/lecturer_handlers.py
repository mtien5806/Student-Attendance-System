from src.services.session_service import SessionService
from src.services.attendance_service import AttendanceService
from src.services.request_service import RequestService
from src.services.report_service import ReportService


session_service = SessionService()
attendance_service = AttendanceService()
request_service = RequestService()
report_service = ReportService()


def lecturer_dashboard(lecturer):
    """
    lecturer: object hoặc dict có thuộc tính
        - id
        - name
    """

    while True:
        pending_requests = get_pending_request_count()

        print("""
[LECTURER DASHBOARD]
User: {} (ID: {})
Pending Requests: {}
--------------------------------------------------
1. Create Attendance Session
2. Record Attendance
3. Approve/Reject Absence/Late Requests
4. Summarize Attendance
5. Export Attendance Report (Excel)
0. Logout
--------------------------------------------------
""".format(lecturer.name, lecturer.id, pending_requests), end="")

        choice = input("Selection: ").strip()

        if choice == "1":
            create_session_ui()

        elif choice == "2":
            record_attendance_ui()

        elif choice == "3":
            process_requests_ui()

        elif choice == "4":
            summarize_attendance_ui()

        elif choice == "5":
            export_attendance_ui()

        elif choice == "0":
            print("Logout successfully.")
            break

        else:
            print("Invalid selection. Please try again.")
