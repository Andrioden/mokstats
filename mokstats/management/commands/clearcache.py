from typing import Any

from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args: Any, **kwargs: Any) -> None:  # noqa: F841
        cache.clear()
        self.stdout.write("Cleared cache\n")
