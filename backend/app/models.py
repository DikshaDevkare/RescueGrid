from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime
from datetime import datetime, timezone
from .db import Base

def now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = 'users'
    id=Column(String,primary_key=True); full_name=Column(String); email=Column(String,unique=True,index=True)
    password_hash=Column(String); role=Column(String); mobile=Column(String,default=''); area=Column(String,default='')
    latitude=Column(Float,nullable=True); longitude=Column(Float,nullable=True)
    team_name=Column(String,default=''); team_id=Column(String,default=''); designation=Column(String,default='')
    team_type=Column(String,default=''); verification_id=Column(String,default=''); created_at=Column(DateTime,default=now)

class RescueTeam(Base):
    __tablename__='rescue_teams'
    id=Column(String,primary_key=True); team_name=Column(String); team_id=Column(String,unique=True,index=True)
    leader_name=Column(String); designation=Column(String); mobile=Column(String); email=Column(String)
    operational_area=Column(String); team_type=Column(String); verification_id=Column(String); status=Column(String,default='Active')
    latitude=Column(Float,nullable=True); longitude=Column(Float,nullable=True); created_at=Column(DateTime,default=now)

class Victim(Base):
    __tablename__='victims'
    id=Column(String,primary_key=True); name=Column(String); age=Column(Integer); severity=Column(String); medical_condition=Column(String)
    latitude=Column(Float); longitude=Column(Float); status=Column(String); version=Column(Integer,default=1); updated_by=Column(String)
    device_id=Column(String,default=''); updated_at=Column(DateTime,default=now)

class Incident(Base):
    __tablename__='incidents'
    id=Column(String,primary_key=True); title=Column(String); type=Column(String); severity=Column(String); description=Column(Text)
    latitude=Column(Float); longitude=Column(Float); people_affected=Column(Integer); status=Column(String); version=Column(Integer,default=1)
    updated_by=Column(String); image_data=Column(Text,default=''); location=Column(String,default=''); device_id=Column(String,default=''); updated_at=Column(DateTime,default=now)

class Resource(Base):
    __tablename__='resources'
    id=Column(String,primary_key=True); name=Column(String); category=Column(String); available=Column(Integer); allocated=Column(Integer)
    unit=Column(String); location=Column(String); latitude=Column(Float,nullable=True); longitude=Column(Float,nullable=True)
    status=Column(String); version=Column(Integer,default=1); updated_by=Column(String); device_id=Column(String,default=''); updated_at=Column(DateTime,default=now)

class Conflict(Base):
    __tablename__='conflicts'
    id=Column(String,primary_key=True); entity=Column(String); entity_id=Column(String); operation=Column(String); local_payload=Column(Text)
    server_payload=Column(Text); base_version=Column(Integer); server_version=Column(Integer); device_id=Column(String); resolved=Column(Boolean,default=False); created_at=Column(DateTime,default=now)

class Activity(Base):
    __tablename__='activities'
    id=Column(Integer,primary_key=True); text=Column(String); type=Column(String); created_at=Column(DateTime,default=now)
