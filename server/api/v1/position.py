from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import FastAPI, Body, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.api import schemas
from server.database import models as db_models
from server.database.session import get_db_session

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/add_post", status_code=status.HTTP_200_OK)
async def add_post(
        data: schemas.Post,
        session: AsyncSession = Depends(get_db_session),
):
    # prj = await search_project(data, session=session)
    data = data.dict()
    post = db_models.Positions(position_name=data['position_name'])
    session.add(post)
    await session.commit()


@router.post("/search_post", status_code=status.HTTP_200_OK)
async def search_post(
        data: schemas.Post,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()
    positions = await session.scalars(
        select(db_models.Positions).filter_by(position_name=data['position_name']))
    try:
        return [cur_post for cur_post in positions]
    except:
        return []


@router.post("/search_post_by_id", status_code=status.HTTP_200_OK)
async def search_post_by_id(
        data: schemas.PostSearchById,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()
    positions = await session.scalars(
        select(db_models.Positions).filter_by(id=data['id']))
    results = [cur_post for cur_post in positions]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"content": results}),
    )

@router.post("/delete_post", status_code=status.HTTP_200_OK)
async def delete_post(
        data: schemas.Post,
        session: AsyncSession = Depends(get_db_session),
):
    positions = await search_post(data, session=session)
    # data = data.dict()
    try:
        await session.delete(positions[0])
        await session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK
        )
    except IndexError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,  # TODO: Изменить ошибку
            content=jsonable_encoder({"detail": "This entry was not found in the database!"}),
        )


@router.post("/get_all_positions", status_code=status.HTTP_200_OK)
async def get_all_positions(
        data: schemas.Post,
        session: AsyncSession = Depends(get_db_session),
):
    # data = data.dict()
    positions = await session.scalars(select(db_models.Positions))
    results = [cur_post for cur_post in positions]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"content": results}),
    )


# @router.post("/update_post", status_code=status.HTTP_200_OK)
# async def update_post(
#         data: schemas.ProjectUpdate,
#         session: AsyncSession = Depends(get_db_session),
# ):
#     data = data.dict()
#     return data['first_name']
