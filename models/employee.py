### models/employee.py

### Map the existing PostgreSQL table
### This model maps to our existing public.employees table.

### NOTE: It does not create the table.

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Employee(Base):
    __tablename__ = "employees"

    __table_args__ = (
        UniqueConstraint(
            "employee_code",
            name="uq_employees_employee_code",
        ),
        UniqueConstraint(
            "email",
            name="uq_employees_email",
        ),
        CheckConstraint(
            "age BETWEEN 18 AND 70",
            name="ck_employees_age_range",
        ),
        CheckConstraint(
            "salary >= 0",
            name="ck_employees_salary_nonnegative",
        ),
        CheckConstraint(
            "rating >= 0 AND rating <= 5",
            name="ck_employees_rating_range",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'on_leave', 'terminated')",
            name="ck_employees_status_valid",
        ),
        CheckConstraint(
            "LENGTH(TRIM(first_name)) > 0",
            name="ck_employees_first_name_not_blank",
        ),
        CheckConstraint(
            "LENGTH(TRIM(last_name)) > 0",
            name="ck_employees_last_name_not_blank",
        ),
        Index(
            "ix_employees_department_status",
            "department",
            "status",
        ),
        Index("ix_employees_salary", "salary"),
        Index("ix_employees_joining_date", "joining_date"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    employee_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    age: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    salary: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    joining_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'active'"),
    )

    skills: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        nullable=False,
        server_default=text("'{}'::text[]"),
    )

    address: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    # The Python attribute is metadata_json because
    # Base.metadata is reserved by SQLAlchemy.
    # The actual PostgreSQL column is named "metadata".
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        server_default=text("0"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

'''
Important
----------
The constraints and indexes in __table_args__ describe the model's expected database structure. They do not modify an existing table.

This application deliberately does not call:

Base.metadata.create_all(bind=engine)

Also, the updated_at column will not automatically change on every update unless your existing database has a trigger or your application explicitly updates the field. We will handle that in the service layer.

Verify that your existing table matches the model before running the API.
'''
