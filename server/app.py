from fastapi import FastAPI
import uvicorn
from server.api.v1.employee import router as v1_router_employee
from server.api.v1.project import router as v1_router_project
from server.api.v1.position import router as v1_router_positions
from server.api.v1.user_information import router as v1_router_user_information
# from aerial_photography.api.v2.routes import router as v2_router
from server.config import settings
from fastapi import Depends
from server.database.session import get_db_session, create_db_and_tables
from fastapi import FastAPI, Body, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.include_router(v1_router_employee, prefix="/api")
app.include_router(v1_router_project, prefix="/api")
app.include_router(v1_router_positions, prefix="/api")
app.include_router(v1_router_user_information, prefix="/api")


@app.on_event("startup")
async def initial_db():
    await create_db_and_tables()
    print('Initialization completed successfully!')


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(),
                                  "body": exc.body,
                                  "custom msg": {"Your error message"}}),
    )

#
if __name__ == "__main__":
    uvicorn.run("server.app:app", port=8001, log_level="info", reload=True)
