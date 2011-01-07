from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DateTime, Integer, Numeric, String
Base = declarative_base()

class TimeEntry(Base):
    __tablename__ = 'time_entries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    task = Column(String(50))
    start = Column(DateTime)
    duration = Column(Numeric)
    comment = Column(String(1024))
