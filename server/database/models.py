from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    LargeBinary,
    String,
    DateTime,
    ForeignKey
)

Base = declarative_base()


class Employees(Base):
    __tablename__ = "employees"

    id = Column('id', Integer, primary_key=True)
    first_name = Column('first_name', String(60))
    last_name = Column('last_name', String(60))
    patronymic = Column('patronymic', String(60))
    post = Column('post', Integer, ForeignKey("positions.id"))
    project = Column("project", Integer, ForeignKey("projects.id"))
    image = Column("image", LargeBinary, default=None)
    time_addition = Column("time_addition", DateTime(timezone=True), server_default=func.now())


class UserInformation(Base):
    __tablename__ = "user_information"

    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', Integer)
    last_message = Column('last_message', String(512), default='')
    offset = Column('offset', Integer, default=0)
    limit = Column('limit', Integer, default=5)
    image_buffer = Column("image_buffer", LargeBinary, default=None)
    cur_state = Column('cur_state',  Integer, default=5)
    ind = Column('ind', Integer, default=0)
    end_ind = Column('end_ind', Integer, default=0)
    role = Column('role', Integer, default=0)




class Projects(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    project_name = Column('project_name', String(128))

    relationship_projects2employees = relationship(
        "Employees",
        backref='projects',
        lazy=True
    )


class Positions(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    position_name = Column('position_name', String(60))
    relationship_positions2employees = relationship(
        "Employees",
        backref='positions',
        lazy=True
    )
