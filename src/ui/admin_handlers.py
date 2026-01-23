from __future__ import annotations

from src.services.admin_service import AdminService
from src.ui.prompts import prompt_choice, prompt_text


class AdminHandlers:
    """UC05 Search Attendance; UC10 Manage Attendance handlers."""

    def __init__(self) -> None:
        self._admin_service = AdminService()

    def admin_menu(self) -> None:
        """Main admin menu - Navigate between Search and Manage."""
        while True:
            print("\n" + "=" * 60)
            print("ADMIN MENU")
            print("=" * 60)
            print("\n1. Search Attendance (UC05)")
            print("2. Manage Attendance (UC10)")
            print("3. Done")

            choice = prompt_choice("\nSelection: ")

            if choice == "1":
                self.search_attendance_menu()
            elif choice == "2":
                self.manage_attendance_menu()
            elif choice == "3":
                print("\n Goodbye!")
                break
            else:
                print("\n Invalid choice. Please try again.")

    def search_attendance_menu(self) -> None:
        """UC05: Search Attendance - Tìm kiếm nhanh chóng khi kiểm tra."""
        print("\n" + "=" * 60)
        print("SEARCH ATTENDANCE (UC05)")
        print("=" * 60)

        print("\nFilters (nhập để tìm, bỏ trống để bỏ qua):")
        student_id_input = prompt_text("Student ID (optional): ")
        session_id_input = prompt_text("Session ID (optional): ")
        class_id_input = prompt_text("Class ID (optional): ")
        date_from_input = prompt_text("Date From (YYYY-MM-DD, optional): ")
        date_to_input = prompt_text("Date To (YYYY-MM-DD, optional): ")

        # Convert to appropriate types or None
        student_id = int(student_id_input) if student_id_input else None
        session_id = int(session_id_input) if session_id_input else None
        class_id = int(class_id_input) if class_id_input else None
        date_from = date_from_input if date_from_input else None
        date_to = date_to_input if date_to_input else None

        try:
            results = self._admin_service.search_attendance(
                student_id=student_id,
                session_id=session_id,
                class_id=class_id,
                date_from=date_from,
                date_to=date_to,
            )

            if not results:
                print("\n  No records found.")
                return

            print(f"\n Found {len(results)} record(s):\n")
            print(f"{'RecordID':<10} {'SessionID':<10} {'StudentID':<10} {'Status':<12} {'Check-in':<20} {'Note':<30}")
            print("-" * 92)

            for record in results:
                record_id = record["record_id"]
                sid = record["session_id"]
                stud_id = record["student_id"]
                status = record["status"]
                checkin_time = record["checkin_time"] or "N/A"
                note = record["note"][:27] + "..." if record["note"] and len(record["note"]) > 30 else record["note"] or ""

                print(f"{record_id:<10} {sid:<10} {stud_id:<10} {status:<12} {checkin_time:<20} {note:<30}")

        except ValueError as e:
            print(f"\n Invalid input: {e}")
        except Exception as e:
            print(f"\n Error: {e}")

    def manage_attendance_menu(self) -> None:
        """UC10: Manage Attendance - Thêm/sửa/xoá bản ghi."""
        print("\n" + "=" * 60)
        print("MANAGE ATTENDANCE (UC10)")
        print("=" * 60)

        print("\n1. Add Record")
        print("2. Edit Record")
        print("3. Delete Record")
        print("4. Back")

        choice = prompt_choice("\nSelection: ")

        if choice == "1":
            self._add_record()
        elif choice == "2":
            self._edit_record()
        elif choice == "3":
            self._delete_record()

    def _add_record(self) -> None:
        """Add a new attendance record."""
        print("\n--- Add Attendance Record ---")
        try:
            session_id = int(prompt_text("Session ID: "))
            student_id = int(prompt_text("Student ID: "))
            status = prompt_text("Status (Present/Late/Absent/Excused): ")
            note = prompt_text("Note (optional): ")

            record_id = self._admin_service.add_record(
                session_id=session_id,
                student_id=student_id,
                status=status,
                note=note if note else None,
            )
            print(f"\n Record added successfully (ID: {record_id})")
        except ValueError as e:
            print(f"\n Invalid input: {e}")
        except Exception as e:
            print(f"\n Error: {e}")

    def _edit_record(self) -> None:
        """Edit an existing attendance record."""
        print("\n--- Edit Attendance Record ---")
        try:
            session_id = int(prompt_text("Session ID: "))
            student_id = int(prompt_text("Student ID: "))
            status = prompt_text("New Status (Present/Late/Absent/Excused): ")
            note = prompt_text("New Note (optional): ")

            self._admin_service.edit_record(
                session_id=session_id,
                student_id=student_id,
                status=status,
                note=note if note else None,
            )
            print("\n Record updated successfully")
        except ValueError as e:
            print(f"\n Invalid input: {e}")
        except Exception as e:
            print(f"\n Error: {e}")

    def _delete_record(self) -> None:
        """Delete an attendance record."""
        print("\n--- Delete Attendance Record ---")
        try:
            session_id = int(prompt_text("Session ID: "))
            student_id = int(prompt_text("Student ID: "))

            confirm = input(f"\n  Confirm delete record (Session {session_id}, Student {student_id})? (y/n): ").strip().lower()
            if confirm in ("y", "yes"):
                self._admin_service.delete_record(
                    session_id=session_id,
                    student_id=student_id,
                )
                print(" Record deleted successfully")
            else:
                print(" Deletion cancelled")
        except ValueError as e:
            print(f"\n Invalid input: {e}")
        except Exception as e:
            print(f"\n Error: {e}")
