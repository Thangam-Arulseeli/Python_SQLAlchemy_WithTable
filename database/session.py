### The application uses SessionLocal whenever it needs to interact with PostgreSQL.
### This code manages the database session lifecycle. It creates a session, provides it for database operations, and closes it afterward.
'''
For Example
with SessionLocal() as session:
    # Perform database operations here.
    pass

The context manager closes the session after the block completes.

The service layer will explicitly commit or roll back write transactions.
'''

from collections.abc import Generator

from sqlalchemy.orm import Session

from database.connection import SessionLocal


def get_db() -> Generator[Session, None, None]: # Creates a new database session.   
    db = SessionLocal()

    try:
        yield db # Provides the session to the calling function without immediately ending the generator.
    finally:     # Ensures cleanup runs when the generator is closed.
        db.close()   # Closes the session and releases its database connection back to the connection pool

'''
This function provides a database session to an API request and closes it when the request finishes.

We will connect it to FastAPI through dependency injection.
'''
#----------------------------------------

''''
yield db provides the session to the endpoint. The endpoint executes database queries.

Why is it important?
--------------------- 
Resource management: Prevents database sessions from being left open.
Connection reuse: Returns connections to the connection pool.
Error handling: The finally block ensures cleanup even if an exception occurs.


In short: get_db() provides a database session for each request and ensures that the session is closed afterward.

'''



# ==========================

# from sqlalchemy.orm import Session, sessionmaker

# from database.connection import engine


# SessionLocal = sessionmaker(
#     bind=engine,
#     class_=Session,
#     autoflush=False,
#     expire_on_commit=False,
# )