import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import FastAPI, Body, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, text, or_, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from server.api import schemas
from server.database import models as db_models
from server.database.session import get_db_session

from server.api.v1.position import search_post
from server.api.v1.project import search_project

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/add_employee", status_code=status.HTTP_200_OK)
async def add_employee(
        data: schemas.Employee,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()

    if data.get('image', None) is not None:
        result_img = data['image'].encode('utf-8')
    else:
        result_img = None

    employee = db_models.Employees(first_name=data['first_name'],
                                   last_name=data['last_name'],
                                   patronymic=data['patronymic'],
                                   image=result_img)
    prj = db_models.Projects(project_name=data['project_name'], relationship_projects2employees=[employee])
    pos = db_models.Positions(position_name=data['post_name'], relationship_positions2employees=[employee])
    session.add_all([prj, pos, employee])
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"detail": "The employee has been added successfully!"}),
    )


@router.post("/update_employee", status_code=status.HTTP_200_OK)
async def update_employee(
        data: schemas.Employee,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()
    if data.get('image', None) is not None:
        result_img = data['image'].encode('utf-8')
    else:
        result_img = None

    await session.execute(
        update(db_models.Employees).values(first_name=data['first_name'], last_name=data['last_name'],
                                           patronymic=data['patronymic'], image=result_img).filter_by(
            id=data['id']))

    info_employee = await session.scalars(select(db_models.Employees).filter_by(id=data['id']))
    info_employee = [item for item in info_employee]

    if len(info_employee) == 0:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"detail": "It looks like the employee has been deleted!"}),
        )

    info_employee = info_employee[0]

    await session.execute(
        update(db_models.Positions).values(position_name=data['post_name']).filter_by(id=info_employee.post))

    await session.execute(
        update(db_models.Projects).values(project_name=data['project_name']).filter_by(id=info_employee.project))

    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"detail": "The employee has been added successfully!"}),
    )


@router.post("/search_employee", status_code=status.HTTP_200_OK)
async def search_employee(
        data: schemas.EmployeeSearch,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()

    term = data['first_name'] + " " + data['last_name'] + ' ' + data['patronymic']
    term = term.lower()
    offset = data['offset']
    limit = data['limit']

    columns = func.coalesce(db_models.Employees.first_name, '').concat(
        func.coalesce(db_models.Employees.last_name, '')).concat(
        func.coalesce(db_models.Employees.patronymic, ''))

    columns = columns.self_group()
    search_result = await session.scalars(select(
        db_models.Employees,
        func.similarity(func.lower(columns), term),

    ).where(
        or_(columns.bool_op('%')(term),
            db_models.Employees.first_name.bool_op('%')(term),
            db_models.Employees.last_name.bool_op('%')(term),
            db_models.Employees.patronymic.bool_op('%')(term))
    ).limit(limit).offset(offset).order_by(
        func.similarity(columns, term).desc(),
        func.similarity(db_models.Employees.first_name, term).desc(),
        func.similarity(db_models.Employees.last_name, term).desc(),
        func.similarity(db_models.Employees.patronymic, term).desc(),
    ))
    search_result = [item for item in search_result]

    list_projects, list_positions = [], []
    for item in search_result:
        list_projects.append(item.project)
        list_positions.append(item.post)

    result_project = await session.scalars(
        select(db_models.Projects).filter(db_models.Projects.id.in_(list(list_projects))))
    result_project = [item for item in result_project]

    result_positions = await session.scalars(
        select(db_models.Positions).filter(db_models.Positions.id.in_(list(list_positions))))
    result_positions = [item for item in result_positions]

    result = []
    for ind, item in enumerate(search_result):
        result.append({
            'id': item.id,
            "first_name": item.first_name,
            "last_name": item.last_name,
            "patronymic": item.patronymic,
            'image': item.image,
            "post_name": result_positions[ind].position_name,
            "project_name": result_project[ind].project_name
        })

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"content": result}),
    )


@router.post("/search_employee_by_id", status_code=status.HTTP_200_OK)
async def search_employee_by_id(
        data: schemas.EmployeeSearchById,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()
    search_results = await session.scalars(
        select(db_models.Employees).filter_by(id=data['id']))
    search_results = [item for item in search_results]

    if len(search_results) == 0:
        # Пользователь не найден
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=None,
        )

    search_result = search_results[0]

    result_project = await session.scalars(
        select(db_models.Projects).filter_by(id=search_result.project))

    result_project = [item for item in result_project]
    result_project = result_project[0]

    result_position = await session.scalars(
        select(db_models.Positions).filter_by(id=search_result.post))
    result_position = [item for item in result_position]
    result_position = result_position[0]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "id": search_result.id,
            "first_name": search_result.first_name,
            "last_name": search_result.last_name,
            'image': search_result.image,
            "patronymic": search_result.patronymic,
            "post_name": result_position.position_name,
            "project_name": result_project.project_name,
        }),
    )


@router.post("/delete_employee_by_id", status_code=status.HTTP_200_OK)
async def delete_employee_by_id(
        data: schemas.EmployeeSearchById,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()
    await session.execute(delete(db_models.Employees).filter_by(id=data['id']))

    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=None,
    )
