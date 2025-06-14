from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from .models import Match, PlayerResult


@never_cache
def last_playerlist(request: WSGIRequest) -> JsonResponse:
    last_match_id = Match.objects.order_by("-id").values("id")[0]["id"]
    player_ids = PlayerResult.objects.filter(match=last_match_id).order_by("id").values_list("player__id", flat=True)
    return JsonResponse(list(player_ids), safe=False)


@never_cache
def clear_cache(request: WSGIRequest) -> JsonResponse:
    cache.clear()
    return JsonResponse({"response": "OK"})
