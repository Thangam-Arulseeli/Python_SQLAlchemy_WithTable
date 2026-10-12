'''
Repository responsibilities
------------------------------
The repository performs the database operations:

Insert an employee.
Retrieve an employee.
Search by employee code or email.
Filter and paginate employee records.
Update an employee.
Delete an employee.

Notice the allowlist for sort_by. A client cannot supply an arbitrary SQL expression as a sorting column.
'''

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select # In SQLAlchemy, func is used to call SQL functions such as COUNT(), SUM(), AVG(), MIN(), MAX() and scalar() from Python code.
from sqlalchemy.orm import Session

from models.employee import Employee
from schemas.employee import EmployeeStatus


class EmployeeRepository:

    def __init__(self, db: Session):
        self.db = db


    def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.flush()
        self.db.refresh(employee)

        return employee
    


    def get_by_id(
        self,
        employee_id: uuid.UUID,
    ) -> Employee | None:
        return self.db.get(Employee, employee_id)
    ### NOTE Session.get() is optimized for primary-key lookups. SQLAlchemy may return the object directly from its session's identity map if it is already loaded, avoiding another database query.



    def get_by_code(self, code: str) -> Employee | None:
        statement = select(Employee).where(
            Employee.employee_code == code
        )
        return self.db.scalar(statement)
    

    def get_by_email(self, email: str) -> Employee | None:
        statement = select(Employee).where(
            func.lower(Employee.email) == email.lower()
        )

        return self.db.scalar(statement)



    def list_employees(
        self,      # Accesses the repository object and its database session.
        *,        # Requires the following parameters to be passed as keyword arguments.
        page: int,
        page_size: int,
        department: str | None = None,
        status: EmployeeStatus | None = None,
        is_active: bool | None = None,
        min_salary: Decimal | None = None,
        max_salary: Decimal | None = None,
        joining_date_from: date | None = None,
        joining_date_to: date | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Employee], int]:  # Returns a list of employees and the total matching record count

        statement = select(Employee)

        if department:
            statement = statement.where(
                Employee.department.ilike(department) # Case -insensitive
            )

        if status:
            statement = statement.where(
                Employee.status == status.value
            )

        if is_active is not None:
            statement = statement.where(
                Employee.is_active == is_active
            )

        if min_salary is not None:
            statement = statement.where(
                Employee.salary >= min_salary
            )

        if max_salary is not None:
            statement = statement.where(
                Employee.salary <= max_salary
            )

        if joining_date_from:
            statement = statement.where(
                Employee.joining_date >= joining_date_from
            )

        if joining_date_to:
            statement = statement.where(
                Employee.joining_date <= joining_date_to
            )

        if search:
            search_pattern = f"%{search}%"

            statement = statement.where(
                Employee.first_name.ilike(search_pattern)
                | Employee.last_name.ilike(search_pattern)
                | Employee.email.ilike(search_pattern)
                | Employee.employee_code.ilike(search_pattern) # Case -insensitive
            )

        count_statement = select(
            func.count()
        ).select_from(
            statement.order_by(None).subquery()   # Converts the filtered employee query into a subquery so the outer query can count its results.
        )

        total = self.db.scalar(count_statement) or 0

        allowed_sort_columns = {
            "created_at": Employee.created_at,
            "employee_code": Employee.employee_code,
            "first_name": Employee.first_name,
            "salary": Employee.salary,
            "joining_date": Employee.joining_date,
            "department": Employee.department,
        }

        sort_column = allowed_sort_columns.get(sort_by)

        if sort_column is None:
            raise ValueError("Unsupported sort column.")

        if sort_order == "desc":
            statement = statement.order_by(sort_column.desc())
        else:
            statement = statement.order_by(sort_column.asc())

        offset = (page - 1) * page_size

        statement = statement.offset(offset).limit(page_size)

        employees = list(self.db.scalars(statement).all())

        return employees, total

   
   
    def update(self, employee: Employee) -> Employee:
        self.db.flush()
        self.db.refresh(employee)

        return employee



    def delete(self, employee: Employee) -> None:
        self.db.delete(employee)
        self.db.flush()

