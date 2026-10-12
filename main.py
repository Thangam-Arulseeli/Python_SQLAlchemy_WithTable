from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.connection import engine
from routers.employee_router import router as employee_router
#from routers.health_router import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify that the database is reachable when the application starts.
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    yield

    # Dispose of the engine's connection pool on shutdown.
    engine.dispose()


app = FastAPI(
    title="Employee Management API",
    description=(
        "REST API for managing employee records using "
        "FastAPI, SQLAlchemy ORM, Pydantic, and PostgreSQL."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(
    employee_router,
    prefix="/api/v1",  ### The router prefix and endpoint path are combined.
)

# app.include_router(health_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the Employee Management API",
        "documentation": "/docs",
      #  "health": "/health",
    }


'''
@router.get("/{employee_id}")   #### With the root router the end points are combines so.......

it becomes:

GET /api/v1/employees/{employee_id}

FastAPI automatically includes registered endpoints in the OpenAPI specification used by Swagger UI.

Notice that main.py does not call Base.metadata.create_all(). The application connects to your existing database and maps the existing table.
'''