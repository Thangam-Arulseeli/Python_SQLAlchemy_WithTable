'''
File: schemas/employee.py
----------------------------
Create the Pydantic schemas
------------------------------
Pydantic validates incoming JSON before the service layer processes it.

For example, an employee's age must be between 18 and 70, the email must be valid, and the salary must be nonnegative.
'''

'''
What does this layer do?

For example:

EmployeeCreate(
    employee_code="cg1001",
    first_name="Arun",
    last_name="Kumar",
    email="arun@example.com",
    department="Development",
    age=28,
    salary=Decimal("65000.00"),
    joining_date=date(2025, 6, 10),
)

Pydantic validates the input and normalizes the employee code to CG1001.

Invalid email addresses, negative salaries, and ages outside the allowed range are rejected before database operations occur.
'''


import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class EmployeeBase(BaseModel):
    employee_code: str = Field(
        min_length=1,
        max_length=20,
    )

    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str = Field(
        min_length=1,
        max_length=100,
    )

    email: EmailStr

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    department: str = Field(
        min_length=1,
        max_length=100,
    )

    age: int = Field(
        ge=18,
        le=70,
    )

    salary: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    joining_date: date

    last_login_at: datetime | None = None

    is_active: bool = True

    status: EmployeeStatus = EmployeeStatus.ACTIVE

    skills: list[str] = Field(default_factory=list)

    address: dict[str, Any] = Field(default_factory=dict)

    metadata_json: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices(
            "metadata_json",
            "metadata",
        ),
        serialization_alias="metadata",
    )

    rating: float = Field(
        default=0,
        ge=0,
        le=5,
    )

    @field_validator(
        "employee_code",
        "first_name",
        "last_name",
        "department",
        mode="before",
    )
    @classmethod
    def validate_required_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError("This field cannot be blank.")

        return value

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, value: list[str]) -> list[str]:
        cleaned = []

        for skill in value:
            skill = skill.strip()

            if not skill:
                raise ValueError("Skills cannot contain blank values.")

            cleaned.append(skill)

        return cleaned


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    employee_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    department: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    age: int | None = Field(
        default=None,
        ge=18,
        le=70,
    )

    salary: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    joining_date: date | None = None

    last_login_at: datetime | None = None

    is_active: bool | None = None

    skills: list[str] | None = None

    address: dict[str, Any] | None = None

    metadata_json: dict[str, Any] | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "metadata_json",
            "metadata",
        ),
        serialization_alias="metadata",
    )

    rating: float | None = Field(
        default=None,
        ge=0,
        le=5,
    )

    @field_validator(
        "employee_code",
        "first_name",
        "last_name",
        "department",
        mode="before",
    )
    @classmethod
    def validate_update_text(cls, value: Any) -> Any:
        if value is None:
            return value

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError("This field cannot be blank.")

        return value

    @field_validator("skills")
    @classmethod
    def validate_update_skills(
        cls,
        value: list[str] | None,
    ) -> list[str] | None:
        if value is None:
            return value

        cleaned = []

        for skill in value:
            skill = skill.strip()

            if not skill:
                raise ValueError("Skills cannot contain blank values.")

            cleaned.append(skill)

        return cleaned


class EmployeeStatusUpdate(BaseModel):
    status: EmployeeStatus


class EmployeeResponse(EmployeeBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class EmployeeListResponse(BaseModel):
    items: list[EmployeeResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool

'''
Why do we have different schemas?
Schema	                Purpose
EmployeeCreate	         Validates new employee data
EmployeeUpdate	         Validates fields provided during an update
EmployeeStatusUpdate	Validates a status-change request
EmployeeResponse	    Defines the employee data returned by the API
EmployeeListResponse	Defines the paginated employee list response

The metadata_json Python attribute maps to the database column named metadata. The schema accepts either metadata or metadata_json in input and uses metadata in serialized output.

Note: EmployeeUpdate uses None to represent omitted or null fields. The service below rejects explicit null values for fields that must not be null. It also rejects an empty update request.
'''