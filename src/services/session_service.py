import random
from datetime import datetime
# Giả định Dev A đã cung cấp repo này
import src.repositories.session_repo as session_repo 
from src.models.enums import SessionStatus

def create_session(class_id, lecturer_id, session_date, start_time, duration, pin_code=None):
    """
    Tạo phiên điểm danh mới.
    - PIN optional: Nếu user không nhập, có thể để None hoặc auto-gen.
    """
    # Validate PIN nếu có nhập
    if pin_code and len(pin_code) not in [4, 5, 6]:
        raise ValueError("PIN must be 4-6 digits.")

    # Auto-gen PIN nếu cần (tuỳ logic dự án)
    # if not pin_code: pin_code = str(random.randint(1000, 9999))

    # Gọi Repo lưu xuống DB
    new_id = session_repo.create(
        class_id=class_id,
        lecturer_id=lecturer_id,
        session_date=session_date,
        start_time=start_time,
        duration=duration,
        status=SessionStatus.OPEN.value,
        pin_code=pin_code
    )
    return new_id

def close_session(session_id):
    """Đóng session, sinh viên không thể check-in nữa"""
    # Kiểm tra session có tồn tại không
    session = session_repo.get_by_id(session_id)
    if not session:
        raise ValueError("Session ID not found")
        
    session_repo.update_status(session_id, SessionStatus.CLOSED.value)
    return True