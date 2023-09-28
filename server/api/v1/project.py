from fastapi import APIRouter, Depends
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.api import schemas
from server.database import models as db_models
from server.database.session import get_db_session

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/add_project", status_code=status.HTTP_200_OK)
async def add_project(
        data: schemas.Project,
        session: AsyncSession = Depends(get_db_session),
):

    data = data.dict()
    prj = db_models.Projects(project_name=data['project_name'])
    session.add(prj)
    await session.commit()


@router.post("/search_project", status_code=status.HTTP_200_OK)
async def search_project(
        data: schemas.Project,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()
    project = await session.scalars(
        select(db_models.Projects).filter_by(project_name=data['project_name']))
    try:
        return [cur_project for cur_project in project]
    except:
        return []


# @router.post("/search_project_by_id", status_code=status.HTTP_200_OK)
# async def search_project_by_id(
#         data: schemas.Project,
#         session: AsyncSession = Depends(get_db_session),
# ):
#     data = data.dict()
#     project = await session.scalars(
#         select(db_models.Projects).filter_by(id=data['id']))
#     result = [cur_project for cur_project in project]
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content=jsonable_encoder({"content": result}),
#     )

@router.post("/delete_project", status_code=status.HTTP_200_OK)
async def delete_project(
        data: schemas.Project,
        session: AsyncSession = Depends(get_db_session),
):
    prj = await search_project(data, session=session)
    # data = data.dict()
    try:
        await session.delete(prj[0])
        await session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK
        )
    except IndexError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": "This entry was not found in the database!"}),
        )

