from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from server.api import schemas
from server.database import models as db_models
from server.database.session import get_db_session

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/add_user_information", status_code=status.HTTP_200_OK)
async def add_user_information(
        data: schemas.UserInformation,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()
    search_results = await search_user_information(schemas.UserInformation(**data), session)
    if search_results is not None:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"detail": "This user has already been added before!"}),
        )

    user_information = db_models.UserInformation(user_id=data['user_id'])
    session.add(user_information)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"detail": "User successfully added!"}),
    )


@router.post("/search_user_information", status_code=status.HTTP_200_OK)
async def search_user_information(
        data: schemas.UserInformation,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()
    search_results = await session.scalars(
        select(db_models.UserInformation).filter_by(user_id=data['user_id']))

    result = [item for item in search_results]
    if len(result) != 0:
        if result[0].image_buffer is not None:
            result_img = result[0].image_buffer.decode('utf-8')
        else:
            result_img = None

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({
                "id": result[0].id,
                "user_id": result[0].user_id,
                "limit": result[0].limit,
                "offset": result[0].offset,
                "image_buffer": result_img,
                "last_message": result[0].last_message,
                "cur_state": result[0].cur_state,
                "ind": result[0].ind,
                "end_ind": result[0].end_ind,
                'role': result[0].role
            }),
        )
    else:
        return None


@router.post("/update_user_information", status_code=status.HTTP_200_OK)
async def update_user_information(
        data: schemas.UserInformation,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()
    if 'image_buffer' in data and data['image_buffer'] is not None:
        data['image_buffer'] = data['image_buffer'].encode('utf-8')
    print(data)

    await session.execute(
        update(db_models.UserInformation).values(**{k: v for k, v in data.items() if v is not None}).filter_by(
            user_id=data['user_id']))
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"detail": "Information has been successfully updated!"}),
    )


@router.post("/update_user_role", status_code=status.HTTP_200_OK)
async def update_user_information(
        data: schemas.UserInformation,
        session: AsyncSession = Depends(get_db_session),
):
    data = data.dict()

    await session.execute(
        update(db_models.UserInformation).values({'role': data['role']}).filter_by(user_id=data['user_id']))

    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"detail": "Information has been successfully updated!"}),
    )