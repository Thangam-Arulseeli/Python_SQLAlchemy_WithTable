### This code configures the SQLAlchemy database connection and session management for your PostgreSQL database.
from sqlalchemy import create_engine  # Creates the SQLAlchemy engine to communicate with PostgreSQL.
from sqlalchemy.orm import sessionmaker # Creates a factory for generating database sessions.   
from config.settings import get_settings # Retrieves database configuration from your .env file.


settings = get_settings() # Loads the database settings, including the host, port, database name and others

#### The engine manages database connections efficiently.
engine = create_engine(
    settings.database_url, # Specifies the PostgreSQL connection details.
    pool_pre_ping=True,   # Checks whether a pooled connection is alive before using it.
    pool_size=5,            # Maintains up to 5 connections in the pool.    
    max_overflow=10,        # Allows up to 10 additional temporary connections.
    pool_timeout=30,        # Waits up to 30 seconds for a connection to become available.
    pool_recycle=1800,  #Recycles connections older than 1800 seconds (30 minutes) when they are checked out.
)

#### SessionLocal creates database sessions for CRUD operations.
SessionLocal = sessionmaker(
    bind=engine,        # Connects each session to the configured database engine.
    autoflush=False,    # Prevents SQLAlchemy from automatically flushing pending changes before queries. Changes are still flushed explicitly or during commit.
    expire_on_commit=False,     # Keeps loaded ORM object attributes accessible after committing, without automatically expiring them
)


'''
The engine manages connections to PostgreSQL.

pool_pre_ping=True helps detect stale connections before they are used.

No table is created by this file.
'''