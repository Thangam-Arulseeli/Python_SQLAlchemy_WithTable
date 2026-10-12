'''
File: services/employee_service.py
---------------------------------------
The service handles business rules and transaction management.

For example, an employee's email must not already exist, and a terminated employee should not be reactivated through the status endpoint.


'''
import uuid
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.employee import Employee
from repositories.employee_repository import EmployeeRepository
from schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeStatus,
)


class EmployeeNotFoundError(Exception):
    pass


class EmployeeAlreadyExistsError(Exception):
    pass


class InvalidEmployeeOperationError(Exception):
    pass


class EmployeeService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = EmployeeRepository(db)


    def create_employee(
        self,
        data: EmployeeCreate,
    ) -> Employee:

        values = data.model_dump(
            by_alias=False,
            mode="python",
        )

        values["id"] = uuid.uuid4()
        values["status"] = data.status.value

        existing_code = self.repository.get_by_code(
            data.employee_code
        )

        if existing_code:
            raise EmployeeAlreadyExistsError(
                "Employee code already exists."
            )

        existing_email = self.repository.get_by_email(
            str(data.email)
        )

        if existing_email:
            raise EmployeeAlreadyExistsError(
                "Email already exists."
            )

        employee = Employee(**values)

        try:
            self.repository.create(employee)
            self.db.commit()
            self.db.refresh(employee)

            return employee

        except IntegrityError as exc:
            self.db.rollback()

            raise EmployeeAlreadyExistsError(
                "Employee code, email, or another database "
                "constraint was violated."
            ) from exc

        except Exception:
            self.db.rollback()
            raise



    def get_employee(
        self,
        employee_id: uuid.UUID,
    ) -> Employee:

        employee = self.repository.get_by_id(employee_id)

        if employee is None:
            raise EmployeeNotFoundError(
                "Employee not found."
            )

        return employee


    def list_employees(self, **filters):
        return self.repository.list_employees(**filters)

    def update_employee(
        self,
        employee_id: uuid.UUID,
        data: EmployeeUpdate,
    ) -> Employee:

        employee = self.get_employee(employee_id)

        changes = data.model_dump(
            exclude_unset=True,
            by_alias=False,
            mode="python",
        )

        if not changes:
            raise InvalidEmployeeOperationError(
                "Provide at least one field to update."
            )

        required_fields = {
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "department",
            "age",
            "salary",
            "joining_date",
            "is_active",
            "status",
            "skills",
            "address",
            "metadata_json",
            "rating",
        }

        for field, value in changes.items():
            if value is None and field in required_fields:
                raise InvalidEmployeeOperationError(
                    f"{field} cannot be null."
                )

        if "employee_code" in changes:
            existing = self.repository.get_by_code(
                changes["employee_code"]
            )

            if existing and existing.id != employee.id:
                raise EmployeeAlreadyExistsError(
                    "Employee code already exists."
                )

        if "email" in changes:
            email = str(changes["email"])

            existing = self.repository.get_by_email(email)

            if existing and existing.id != employee.id:
                raise EmployeeAlreadyExistsError(
                    "Email already exists."
                )

        if "status" in changes:
            changes["status"] = changes["status"].value

        for field, value in changes.items():
            setattr(employee, field, value)

        employee.updated_at = datetime.now(timezone.utc)

        try:
            self.repository.update(employee)
            self.db.commit()
            self.db.refresh(employee)

            return employee

        except IntegrityError as exc:
            self.db.rollback()

            raise InvalidEmployeeOperationError(
                "The update violated a database constraint."
            ) from exc

        except Exception:
            self.db.rollback()
            raise



    def update_status(
        self,
        employee_id: uuid.UUID,
        new_status: EmployeeStatus,
    ) -> Employee:

        employee = self.get_employee(employee_id)

        if employee.status == EmployeeStatus.TERMINATED.value:
            raise InvalidEmployeeOperationError(
                "A terminated employee's status cannot be changed."
            )

        employee.status = new_status.value

        # Keep the Boolean active flag consistent with status.
        employee.is_active = (
            new_status == EmployeeStatus.ACTIVE
        )

        employee.updated_at = datetime.now(timezone.utc)

        try:
            self.repository.update(employee)
            self.db.commit()
            self.db.refresh(employee)

            return employee

        except IntegrityError as exc:
            self.db.rollback()

            raise InvalidEmployeeOperationError(
                "The status update violated a database constraint."
            ) from exc

        except Exception:
            self.db.rollback()
            raise



    def delete_employee(
        self,
        employee_id: uuid.UUID,
    ) -> None:

        employee = self.get_employee(employee_id)

        try:
            self.repository.delete(employee)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise


'''
Important business-rule note
-------------------------------
The status logic above treats terminated as a final status. This is an example business rule, not a restriction imposed by PostgreSQL itself.

If your organization permits reactivating terminated employees, modify that rule.

The code also synchronizes is_active with the status endpoint:

active → is_active = True
inactive → is_active = False
on_leave → is_active = False
terminated → is_active = False

That mapping is a business decision. Ensure it matches your organization's definition of an active employee.

'''