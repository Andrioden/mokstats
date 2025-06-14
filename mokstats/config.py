import json
import os
from decimal import Decimal
from typing import List

from google.cloud.secretmanager import SecretManagerServiceClient


class Config:
    ACTIVE_PLAYER_MATCH_THRESHOLD = 26
    RATING_START = Decimal(100)
    RATING_K = Decimal(2)

    def __init__(self) -> None:
        self._override_env_with_secrets()

    @staticmethod
    def _override_env_with_secrets() -> None:
        """This method overrides the environment variables with the secrets from the secret manager"""
        if secret_name := os.environ.get("SECRET_ENV"):
            secret_client = SecretManagerServiceClient()
            secret_payload: str = secret_client.access_secret_version(name=secret_name).payload.data.decode("UTF-8")
            for key, val in json.loads(secret_payload).items():
                os.environ[key] = val

    @property
    def debug(self) -> bool:
        return os.environ.get("DJANGO_DEBUG", "true").lower() == "true"

    @property
    def allowed_hosts(self) -> List[str]:
        if appengine_url := os.environ.get("APPENGINE_URL"):
            return [appengine_url]
        else:
            return ["*"]

    @property
    def secret_key(self) -> str:
        return os.environ.get("DJANGO_SECRET_KEY", "shitty_default_key")

    @property
    def database(self) -> dict:
        return {
            "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.postgresql"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
            "NAME": os.environ.get("DB_NAME", "mokstats"),
            "USER": os.environ.get("DB_USER", "mokstats"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "mokstats"),
        }


config = Config()
