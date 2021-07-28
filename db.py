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


class Progress(DataBase):  # Track a user's education part
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
    last_quesion_num = Column(String(5))
    """ Quesion numbers:
    a1 - aim add
    a2 - aim update
    a3 - aim delete
    a4 - aim complete
    a5 - aim uncomplete
    
    p1 - plan add
    p2 - plan update
    p3 - plan delete
    p4 - plan complete
    p5 - plan uncomplete
    """


def update_tables():  # Function for updating all tables
    DataBase.metadata.drop_all(engine)
    DataBase.metadata.create_all(engine)


# TODO Add a check of database entry values

def set_support(user_id, values: dict):
    session.query(Support).filter(Support.user_id == user_id).update(values, synchronize_session='fetch')


# Plans functions

def add_plan(user_id, text):
    plan = Plans(plan_name=text, user_id=user_id)
    session.add(plan)
    session.commit()


def edit_plan(plan_q, text):
    plan_q.update({"plan_name": text}, synchronize_session='fetch')
    session.commit()


def delete_aim(plan_q):
    plan = plan_q.first()
    session.delete(plan)
    session.commit()


def complete_plan(plan_q):
    plan_q.update({"completed": True}, synchronize_session='fetch')
    session.commit()


def uncomplete_plan(plan_q):
    plan_q.update({"completed": False}, synchronize_session='fetch')
    session.commit()


# Plans points functions

def add_plan_point(plan_id, number):
    plan_points = session.query(PlansPoints).filter(PlansPoints.plan_id == plan_id)

    if plan_points.filter(PlansPoints.number == number + 1).first():
        for point in plan_points.all():  # Move next points number
            session.query(PlansPoints).filter(
                PlansPoints.number == point.number and PlansPoints.number >= number).update(
                {"number": point.number + 1}, synchronize_session='fetch')
    elif plan_points.filter(PlansPoints.number == number).first():
        plan_points.filter(PlansPoints.number == number).update({"number": number + 1}, synchronize_session='fetch')

    plan_point = PlansPoints(plan_id=plan_id, number=number)
    session.add(plan_point)
    session.commit()


def edit_plan_point():
    pass  # TODO


def delete_plan_point():
    pass  # TODO


# Aims functions

def add_aim(user_id, text):
    aim = Aims(user_id=user_id, aim_name=text)
    session.add(aim)
    session.commit()


def edit_aim(aim_q, text):
    aim_q.update({"aim_name": text}, synchronize_session='fetch')
    session.commit()


def delete_aim(aim_q):
    aim = aim_q.first()
    session.delete(aim)
    session.commit()


def complete_aim(aim_q):
    aim_q.update({"completed": True}, synchronize_session='fetch')
    session.commit()


def uncomplete_aim(aim_q):
    aim_q.update({"completed": False}, synchronize_session='fetch')
    session.commit()


def choise_aim(user_id, text=None):
    if text:
        return session.query(Aims).filter(Aims.user_id == user_id).filter(Aims.aim_name == text)
    else:
        return session.query(Aims).filter(Aims.user_id == user_id)


def choise_plan(user_id, text=None):
    if text:
        return session.query(Plans).filter(Plans.user_id == user_id).filter(Plans.plan_name == text)
    else:
        return session.query(Plans).filter(Plans.user_id == user_id)


# Find user function
def find_user(tele_id):
    return session.query(User).filter(User.tele_id == tele_id).first()
