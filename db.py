from sqlalchemy.sql.expression import null
from config_reader import db_url
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Boolean, insert
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


# Connecting to database

engine = create_engine(db_url)

connection = engine.connect()
DataBase = declarative_base()
session = Session(bind=engine)


# Creating a database models

class User(DataBase):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    tele_id = Column(Integer(), unique=True, nullable=False)

class Progress(DataBase): # Track a user's education part
    __tablename__ = 'edu_progress'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey("users.id"), nullable=False)
    part_number = Column(Integer(), nullable=False, default=0)

class Aims(DataBase):
    __tablename__ = 'aims'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer(), ForeignKey("users.id"), nullable=False)
    aim_name = Column(String(100), nullable=False)
    plan_id = Column(Integer(), ForeignKey("plans.id"))
    completed = Column(Boolean(), default=False)

class Plans(DataBase):
    __tablename__ = 'plans'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey("users.id"), nullable=False)
    plan_name = Column(String(100), nullable=False)
    completed = Column(Boolean())

class PlansPoints(DataBase):
    __tablename__ = 'plans_points'
    id = Column(Integer(), primary_key=True)
    plan_id = Column(Integer(), ForeignKey("plans.id"), nullable=False)
    number = Column(Integer(), nullable=False)
    text = Column(String(255))
    completed = Column(Boolean(), default=False)

class Support(DataBase):
    __tablename__ = 'support_table'
    user_id = Column(Integer(), ForeignKey("users.id"), primary_key=True)
    last_quesion_id = Column(Integer())
    last_quesion_num = Column(String(4))
    """ Quesion numbers:
    a1 - aim add
    a2 - aim update
    a3 - aim delete
    """


def update_tables(): # Function for updating all tables
    DataBase.metadata.drop_all(engine)
    DataBase.metadata.create_all(engine)