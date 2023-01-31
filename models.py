from database import Base
from sqlalchemy import String, INTEGER, Column, DateTime, Boolean, Enum
from datetime import datetime
import enum

# Enum class which has different genders
class GenderEnum(enum.Enum):

    Male = "Male"
    Female = "Female"
    Other = "Other"

# Enum class for buiness
class Business(enum.Enum):
    Student = "Student"
    Professional = "Professional"


class SystemUserModel(Base):

    __tablename__ = "system_user"

    id = Column(String(36), primary_key=True)
    first_name = Column(String(150), default=None)
    last_name = Column(String(150), default=None)
    email = Column(String(50), default=None)
    password = Column(String(150), default=None)
    phone_num = Column(String(15), default = None)
    gender = Column(Enum(GenderEnum))
    image = Column(String(255), default = None)
    notification = Column(DateTime, default = datetime.now)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)