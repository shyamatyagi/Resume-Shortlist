from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Resume(Base):
    __tablename__ = 'resumes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    file_path = Column(String)
    match = Column(Float)
    color = Column(String)
    is_new = Column(Integer, default=1)  # 1 for True, 0 for False


class JobRole(Base):
    __tablename__ = 'job_roles'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    qualification = Column(String)
    experience = Column(String)
    techstack = Column(String)

class Requirement(Base):
    __tablename__ = 'requirements'
    id = Column(Integer, primary_key=True)
    text = Column(String)
