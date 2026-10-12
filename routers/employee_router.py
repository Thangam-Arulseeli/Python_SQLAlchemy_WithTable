import math
import uuid
from datetime import date
from decimal import Decimal
from typing import Annotated  # Combines the type and its additional dependency information.

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from dependencies.database import get_database

from schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeStatusUpdate,
    EmployeeResponse,
    EmployeeListResponse,
    EmployeeStatus,
)
from services.employee_service import (
    EmployeeService,
    EmployeeNotFoundError,
    EmployeeAlreadyExistsError,
    InvalidEmployeeOperationError,
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


# This code uses FastAPI Dependency Injection to create an EmployeeService object and provide it to API endpoints.
def get_employee_service(    
    db: Annotated[Session, Depends(get_database)],
) -> EmployeeService:
    return EmployeeService(db)

'''
Depends(get_database) — FastAPI calls get_database() to obtain a database session.
db: Annotated[Session, ...] — Specifies that db is a SQLAlchemy session provided through dependency injection.
EmployeeService(db) — Creates an EmployeeService object and passes the database session to it.
-> EmployeeService — Indicates that the function returns an EmployeeService object.

'''

# EmployeeServiceDependency
EmployeeServiceDependency = Annotated[  # Attaches additional information to a type.
    EmployeeService,
    Depends(get_employee_service), # 
]
### Creates a reusable dependency that tells FastAPI to call get_employee_service() whenever an endpoint requests an EmployeeServiceDependency.
### Annotated connects the EmployeeService type with FastAPI's dependency instructions, allowing you to reuse the same dependency declaration across multiple endpoints.



@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an employee",
)

def create_employee(
    data: EmployeeCreate,
    service: EmployeeServiceDependency,
):
    try:
        return service.create_employee(data)

    except EmployeeAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,  # "Employee code already exists
            detail=str(exc),
        ) from exc

    except InvalidEmployeeOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc



@router.get(
    "/",
    response_model=EmployeeListResponse,
    summary="List employees with filtering and pagination",
)
def list_employees(
    service: EmployeeServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    department: str | None = None,
    employee_status: Annotated[
        EmployeeStatus | None,
        Query(alias="status"),
    ] = None,
    is_active: bool | None = None,
    min_salary: Annotated[
        Decimal | None,
        Query(ge=0),
    ] = None,
    max_salary: Annotated[
        Decimal | None,
        Query(ge=0),
    ] = None,
    joining_date_from: date | None = None,
    joining_date_to: date | None = None,
    search: Annotated[
        str | None,
        Query(min_length=1, max_length=100),
    ] = None,
    sort_by: str = "created_at",
    sort_order: Annotated[
        str,
        Query(pattern="^(asc|desc)$"),
    ] = "desc",
):
    if (
        min_salary is not None
        and max_salary is not None
        and min_salary > max_salary
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_salary cannot exceed max_salary.",
        )

    if (
        joining_date_from is not None
        and joining_date_to is not None
        and joining_date_from > joining_date_to
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="joining_date_from cannot exceed joining_date_to.",
        )

    try:
        employees, total = service.list_employees(
            page=page,
            page_size=page_size,
            department=department,
            status=employee_status,
            is_active=is_active,
            min_salary=min_salary,
            max_salary=max_salary,
            joining_date_from=joining_date_from,
            joining_date_to=joining_date_to,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    total_pages = math.ceil(total / page_size) if total else 0

    return EmployeeListResponse(
        items=employees,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1 and total > 0,
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get an employee by ID",
)
def get_employee(
    employee_id: uuid.UUID,
    service: EmployeeServiceDependency,
):
    try:
        return service.get_employee(employee_id)

    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc



@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Update employee details",
)
def update_employee(
    employee_id: uuid.UUID,
    data: EmployeeUpdate,
    service: EmployeeServiceDependency,
):
    try:
        return service.update_employee(employee_id, data)

    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except EmployeeAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except InvalidEmployeeOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc



@router.patch(
    "/{employee_id}/status",
    response_model=EmployeeResponse,
    summary="Update employee status",
)
def update_employee_status(
    employee_id: uuid.UUID,
    data: EmployeeStatusUpdate,
    service: EmployeeServiceDependency,
):
    try:
        return service.update_status(
            employee_id,
            data.status,
        )

    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except InvalidEmployeeOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc



@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an employee",
)
def delete_employee(
    employee_id: uuid.UUID,
    service: EmployeeServiceDependency,
):
    try:
        service.delete_employee(employee_id)

        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )

    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    