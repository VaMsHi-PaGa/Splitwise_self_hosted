from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://splitsmart:splitsmart_dev_password@db:5432/splitsmart"
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_expire_minutes: int = 1440
    seed_demo: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def async_database_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")


settings = Settings()
