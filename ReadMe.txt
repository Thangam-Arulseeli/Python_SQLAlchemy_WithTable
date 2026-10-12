Assume the employees table already exists in PostgreSQL. We will connect to that existing table and perform CRUD operations using SQLAlchemy ORM and Pydantic.

We will use Mapped and mapped_column() to map the existing PostgreSQL table to a Python class.

--- Table Creation in PostgreSQL, where public is the schema and employes is the table name

-- Table Structure
--------------------
CREATE TABLE public.employees
(
    -- UUID
    id UUID PRIMARY KEY,

    -- Employee identification
    employee_code VARCHAR(20) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,

    -- Contact information
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),

    -- Employment information
    department VARCHAR(100) NOT NULL,
    age SMALLINT NOT NULL,
    salary NUMERIC(12, 2) NOT NULL,
    joining_date DATE NOT NULL,

    -- Login information
    last_login_at TIMESTAMPTZ,

    -- Employee status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    -- PostgreSQL array
    skills TEXT[] NOT NULL DEFAULT '{}',

    -- PostgreSQL JSONB
    address JSONB NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',

    -- Employee rating
    rating DOUBLE PRECISION NOT NULL DEFAULT 0,

    -- Audit timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraints
    CONSTRAINT uq_employees_employee_code
        UNIQUE (employee_code),

    CONSTRAINT uq_employees_email
        UNIQUE (email),

    -- Check constraints
    CONSTRAINT ck_employees_age_range
        CHECK (age BETWEEN 18 AND 70),

    CONSTRAINT ck_employees_salary_nonnegative
        CHECK (salary >= 0),

    CONSTRAINT ck_employees_rating_range
        CHECK (rating >= 0 AND rating <= 5),

    CONSTRAINT ck_employees_status_valid
        CHECK (
            status IN (
                'active',
                'inactive',
                'on_leave',
                'terminated'
            )
        ),

    CONSTRAINT ck_employees_first_name_not_blank
        CHECK (LENGTH(TRIM(first_name)) > 0),

    CONSTRAINT ck_employees_last_name_not_blank
        CHECK (LENGTH(TRIM(last_name)) > 0)
);
-----------------------------

---Indexes
-----------

CREATE INDEX ix_employees_department_status
ON public.employees (department, status);

CREATE INDEX ix_employees_salary
ON public.employees (salary);

CREATE INDEX ix_employees_joining_date
ON public.employees (joining_date);
------------------------------------

-- Insert Records
------------------
INSERT INTO public.employees
(
    id,
    employee_code,
    first_name,
    last_name,
    email,
    phone,
    department,
    age,
    salary,
    joining_date,
    is_active,
    status,
    skills,
    address,
    metadata,
    rating
)
VALUES
(
    gen_random_uuid(),
    'CG1001',
    'Arun',
    'Kumar',
    'arun.kumar@example.com',
    '+919876543210',
    'Software Development',
    28,
    65000.00,
    '2025-06-10',
    TRUE,
    'active',
    ARRAY['Python', 'SQLAlchemy', 'PostgreSQL'],
    '{"city":"Coimbatore","state":"Tamil Nadu"}'::JSONB,
    '{"work_mode":"hybrid"}'::JSONB,
    4.5
);
-----------------------------------------

-- gen_random_uuid() generates a UUID on PostgreSQL versions that support this function.
-- You can also provide a UUID explicitly if needed.
--------------------------------------

SELECT * FROM public.employees;

-- Inspect the table columns
SELECT
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid = 'public.employees'::regclass
ORDER BY conname;
-----------------------------------
-- Inspect the constraints
SELECT
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid = 'public.employees'::regclass
ORDER BY conname;
------------------------------------

1. What Are We Going to Build?

Our application will have the following features:

Connect to the existing PostgreSQL database.
Map the existing employees table to a SQLAlchemy ORM model.
Validate input using Pydantic v2.
Create employees.
Retrieve employees by ID.
Retrieve all employees.
Update employee information.
Delete employees.
Filter employees by department, salary, age, status, and joining date.
Implement pagination and sorting.
Search employees.
Manage employee status transitions.
Handle database transactions and exceptions.
Use a repository and service architecture.

Technology restrictions: no Alembic, no relationships, and no table creation through Python code (ORM)
---------------------------------------------

2. Understand the Difference Between the Two Approaches
------------------------------------------------------------
Previously, we used:

Base.metadata.create_all(bind=engine)

That command creates missing tables based on the registered ORM models.

In this version, we will not execute it.

Instead, we will map the existing table:

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

SQLAlchemy uses this mapping when querying and updating the existing table.
--------------------------------------------------------------------------
The process becomes:
Existing PostgreSQL Database
            |
            v
Existing employees Table
            |
            v
SQLAlchemy ORM Model
            |
            v
Pydantic Validation
            |
            v
Service Layer
            |
            v
Repository Layer
            |
            v
SQLAlchemy Session
            |
            v
Existing PostgreSQL Table

The ORM model must match the actual table structure. Defining mapped_column() does not create or modify the database table.

=================================================


3. Project Folder Structure
-------------------------------
employee_management/
Python_SQLAlchemy_WithTable/
│
├── .env
├── .gitignore
├── requirements.txt
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── database/
│   ├── __init__.py
│   ├── base.py
│   ├── connection.py
│   └── session.py
│
├── models/
│   ├── __init__.py
│   └── employee.py
│
├── schemas/
│   ├── __init__.py
│   └── employee.py
│
├── repositories/
│   ├── __init__.py
│   └── employee_repository.py
│
├── services/
│   ├── __init__.py
│   └── employee_service.py
│
├── routers/
│   ├── __init__.py
│   ├── employee_router.py
│   └── health_router.py
│
├── dependencies/
│   ├── __init__.py
│   └── database.py
│
└── main.py



The main additions are:

routers/employee_router.py: defines employee API endpoints.
dependencies/database.py: provides a database session to API requests.
main.py: creates the FastAPI application and registers the routers.



4. Install the Required Packages
-----------------------------------
Create a virtual environment:

    > python -m venv venv

Activate it:

    > .\venv\Scripts\Activate.ps1

Install the dependencies:
    > pip install "SQLAlchemy>=2.0,<3.0" "psycopg[binary]>=3.2,<4.0" "pydantic>=2.0,<3.0" "pydantic-settings>=2.0,<3.0" "email-validator>=2.0"


These packages provide:

    SQLAlchemy ORM.
    PostgreSQL connectivity through Psycopg.
    Pydantic validation.
    Environment configuration.
    Email validation.


Operation	             HTTP method	  Endpoint	                          Purpose
Create employee	         POST             /api/v1/employees/	                Create an employee
Get all employees	    GET               /api/v1/employees/	                Retrieve employees with filtering and pagination
Get employee by ID  	GET               /api/v1/employees/{employee_id}	    Retrieve one employee
Update employee	        PUT               /api/v1/employees/{employee_id}	    Update employee details
Update employee status	PATCH             /api/v1/employees/{employee_id}/status Change employee status
Delete employee	        DELETE             /api/v1/employees/{employee_id}	        Delete an employee
Health check	        GET                /health                                  Check whether the application is running




FastAPI automatically generates interactive API documentation for these endpoints.



You can access it at:

http://127.0.0.1:8000/docs


##############################

Test the API in Swagger UI
------------------------------

POST /api/v1/employees/
-----------------------
{
  "employee_code": "EMP1001",
  "first_name": "Arun",
  "last_name": "Kumar",
  "email": "arun.kumar@example.com",
  "phone": "9876543210",
  "department": "Development",
  "age": 28,
  "salary": 55000.00,
  "joining_date": "2026-01-15",
  "last_login_at": null,
  "is_active": true,
  "status": "active",
  "skills": [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "SQLAlchemy"
  ],
  "address": {
    "door_no": "12A",
    "street": "Gandhi Street",
    "city": "Coimbatore",
    "state": "Tamil Nadu",
    "country": "India",
    "pincode": "641001"
  },
  "metadata": {
    "employment_type": "Full-Time",
    "work_mode": "Office"
  },
  "rating": 4.5
}
==========================================

Retrieve all employees
-----------------------
GET /api/v1/employees/
Set:

page = 1
page_size = 10
==========================================

Test filtering
----------------
The list endpoint supports several query parameters.
------------------------------------------------------
Filter by department
--------------------
GET /api/v1/employees/?department=Development

Filter by status
------------------
GET /api/v1/employees/?status=active

Filter by active flag
----------------------
GET /api/v1/employees/?is_active=true

Filter by salary range
----------------------
GET /api/v1/employees/?min_salary=30000&max_salary=70000

Search employee details
-----------------------
GET /api/v1/employees/?search=Arun


The search checks employee first name, last name, email, and employee code.

Filter by joining date
------------------------
GET /api/v1/employees/?joining_date_from=2026-01-01&joining_date_to=2026-12-31

Combine multiple filters
-------------------------
GET /api/v1/employees/?department=Development&status=active&min_salary=30000&max_salary=80000&page=1&page_size=10


Retrieve an employee by ID
----------------------------

GET /api/v1/employees/{employee_id}

Exampe

GET /api/v1/employees/6fa459ea-ee8a-3ca4-894e-db77e160355e

Replace the example UUID with the actual ID returned by the create endpoint.

If the employee exists, the API returns HTTP 200 OK.
##########################################################

Update employee details

PUT /api/v1/employees/{employee_id}

The current implementation uses PUT as a partial-update operation for compatibility with the earlier application. In a stricter REST design, use PATCH for partial updates and reserve PUT for replacing the complete resource.

For example, you can submit:

{
  "department": "AI Development",
  "salary": 65000.00,
  "rating": 4.8
}

The service updates only the supplied fields. Fields that are not included remain unchanged.

If you supply a required field with an explicit null, the service rejects it.
------------------------------------------

Update employee status
------------------------

PATCH /api/v1/employees/{employee_id}/status

Example request:

{
  "status": "on_leave"
}

Other supported status values are:

active
inactive
on_leave
terminated

The API also synchronizes the is_active flag according to the business rule implemented in the service.

A terminated employee cannot have their status changed through this endpoint under the example business rules.
############################################

21. Delete an employee
------------------------
Open:

DELETE /api/v1/employees/{employee_id}

Supply the employee UUID and click Execute.

On successful deletion, the API returns:

204 No Content

A successful 204 response has no response body.

Production consideration: Permanent deletion may not be appropriate for employee records. Many organizations prefer soft deletion or a controlled termination process to preserve audit history.

###################################





