from datetime import datetime
from sqlalchemy import Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DateTime, Integer, Numeric, String
from sqlalchemy.orm import sessionmaker
Base = declarative_base()

class SlimtimerUser(Base):
    __tablename__ = 'slimtimer_users'
    id = Column(Integer, primary_key=True)
    label = Column(String(255))
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class TimeEntry(Base):
    __tablename__ = 'time_entries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    task = Column(String(50))
    start_dt = Column(DateTime)
    duration = Column(Numeric)
    comment = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

def get_session(config):
    engine = create_engine(config.get('database', 'conn_string'),
        use_native_unicode=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    SlimtimerUser.metadata.bind = engine # Gotta do this to create tables
    TimeEntry.metadata.bind = engine # Gotta do this to create tables
    SlimtimerUser.metadata.create_all() # Create tables
    TimeEntry.metadata.create_all() # Create tables
    return session
