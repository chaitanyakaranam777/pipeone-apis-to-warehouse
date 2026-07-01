"""
Central configuration module for PipeOne.
Loads environment variables and exposes typed settings.
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    db: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "pipeone"))
    user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "pipeone_user"))
    password: str = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "pipeone_pass"))

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


@dataclass
class APIConfig:
    github_token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    github_base_url: str = "https://api.github.com"
    hn_base_url: str = "https://hacker-news.firebaseio.com/v0"
    batch_size: int = field(default_factory=lambda: int(os.getenv("BATCH_SIZE", "100")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    retry_delay: float = field(default_factory=lambda: float(os.getenv("RETRY_DELAY", "2")))


@dataclass
class AppConfig:
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)


# Singleton
settings = AppConfig()
