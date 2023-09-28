from typing import Optional
from pydantic import BaseModel


class Employee(BaseModel):
    id: Optional[int] = 0
    user_id: Optional[int]
    first_name: str
    last_name: str
    patronymic: Optional[str] = ''
    post_name: str
    project_name: str
    image: Optional[str] = None


class EmployeeSearch(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    patronymic: Optional[str]
    offset: Optional[int] = 0
    limit: Optional[int] = 5
    project: Optional[str] = None
    position: Optional[str] = None


class EmployeeSearchBetweenTime(BaseModel):
    from_time: Optional[str]
    to_time: Optional[str]


class EmployeeSearchById(BaseModel):
    id: int


class Project(BaseModel):
    project_name: str


class PostSearchById(BaseModel):
    id: int


class ProjectUpdate(BaseModel):
    project_name: str
    new_project_name: str


class Post(BaseModel):
    position_name: str


class PostUpdate(BaseModel):
    position_name: str


class UserInformation(BaseModel):
    user_id: int
    last_message: Optional[str] = None
    offset: Optional[int] = 0
    limit: Optional[int] = 5
    image_buffer: Optional[str] = None
    cur_state: Optional[int] = None
    ind: Optional[int] = None
    end_ind: Optional[int] = None
    role: Optional[int] = 0
