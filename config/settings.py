### It loads the database configuration without hardcoding the 
# 
# # credentials in the application.

### URL.create() also handles passwords containing special characters.

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


'''
NOTE:
If your PostgreSQL password contains special characters such as @, SQLAlchemy constructs the connection URL correctly without requiring you to manually URL-encode the password.
'''

# ===============================

'''
funtools and lru_cache
-------------------------
functools is a Python standard library module.
lru_cache is a decorator that caches the return value of a function.
When the function is called again with the same arguments, Python returns the cached result instead of executing the function again.

@lru_cache

    This decorator caches the result returned by get_settings().

In short: @lru_cache ensures that get_settings() creates the settings object once and reuses it for subsequent calls with the same arguments.  
'''
#===================================================

'''
How it works in your application
----------------------------------
settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
)

Execution flow:
------------------
The application calls get_settings().
Python creates the Settings object and reads the configuration.
@lru_cache stores the returned object.
Subsequent calls reuse the cached object.
The application avoids repeatedly creating and validating the settings object.

'''