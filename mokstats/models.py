import datetime
import logging
from decimal import Decimal
from typing import Any, Literal

from django.db import models
from django.db.models import CASCADE, PROTECT, Q, QuerySet
from django.db.models.signals import post_delete, post_save

from .config import config

logger = logging.getLogger(__name__)


class Player(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def get_ratings(self) -> list[list]:
        results = PlayerResult.objects.filter(player=self).select_related("match")
        ratings = []
        prev_rating = config.RATING_START
        for res in results.order_by("match__date", "match__id"):
            dif = res.rating - prev_rating  # type: ignore[operator]
            if dif > 0:
                css_class = "positive"
            elif dif < 0:
                css_class = "negative"
            else:
                css_class = ""
            dif_str = f"+{dif}" if dif > 0 else str(dif)
            ratings.append([res.match.date.isoformat(), int(res.rating), css_class, dif_str, res.match.id])  # type: ignore  # noqa: E501
            prev_rating = res.rating  # type: ignore[assignment]
        return ratings

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Place(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


def _get_last_match_date() -> datetime.date:
    match_count = Match.objects.count()
    if match_count == 0:
        return datetime.datetime.now()
    else:
        return Match.objects.all()[match_count - 1].date


def _get_last_match_place() -> int | None:
    match_count = Match.objects.count()
    if match_count == 0:
        return None
    else:
        return Match.objects.all()[match_count - 1].place_id


class Match(models.Model):
    date = models.DateField(default=_get_last_match_date)
    place = models.ForeignKey(Place, default=_get_last_match_place, on_delete=PROTECT)

    def get_winners(self) -> list[Player]:
        min_sum = 1000
        winners: list[Player] = []
        for result in PlayerResult.objects.filter(match=self):
            total = result.total()
            if total < min_sum:
                min_sum = total
                winners = []
                winners.append(result.player)
            elif total == min_sum:
                winners.append(result.player)
        return winners

    def get_positions(self) -> list[dict]:
        players = [{"id": res.player_id, "total": res.total()} for res in PlayerResult.objects.filter(match=self)]
        splayers = sorted(players, key=lambda player: player["total"])
        for i in range(len(players)):
            players[i]["position"] = self.get_position(players[i]["id"], splayers)
        return players

    def get_position(self, pid: int, splayers: list[dict] | None = None) -> int:
        if not splayers:
            players = [{"id": res.player_id, "total": res.total()} for res in PlayerResult.objects.filter(match=self)]
            splayers = sorted(players, key=lambda player: player["total"])
        for i in range(len(splayers)):
            if splayers[i]["id"] == pid:
                # Check if winner
                if splayers[i]["total"] == splayers[0]["total"]:
                    return 1
                # Check if player got same total as someone ahead in the sorted list
                for pos in range(i):
                    if splayers[i]["total"] == splayers[pos]["total"]:
                        return pos + 1
                # Check if player got same total as someone behind in the sorted list
                for pos in range(len(splayers) - 1, i + 1, -1):
                    if splayers[i]["total"] == splayers[pos]["total"]:
                        return pos + 1
                # Player did not have the same total as someone else
                return i + 1
        raise ValueError(f"PlayerResult for player {pid} not found in match {self.pk}")

    def get_newer_matches(self) -> QuerySet:
        exclude_q = Q(date__lt=self.date) | (Q(date=self.date) & Q(id__lte=self.pk))
        return Match.objects.exclude(exclude_q)

    def get_older_matches(self) -> QuerySet:
        exclude_q = Q(date__gt=self.date) | (Q(date=self.date) & Q(id__gte=self.pk))
        return Match.objects.exclude(exclude_q)

    def get_next_match_id(self) -> int | None:
        newer = self.get_newer_matches()
        if newer.exists():
            return newer.order_by("date", "id").values("id")[0]["id"]  # type: ignore[no-any-return]
        else:
            return None

    def get_prev_match_id(self) -> int | None:
        older = self.get_older_matches()
        if older.exists():
            return older.order_by("-date", "-id").values("id")[0]["id"]  # type: ignore[no-any-return]
        else:
            return None

    def __str__(self) -> str:
        return "%s - %s (ID: %s)" % (self.date, self.place.name, self.pk)

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"


class PlayerResult(models.Model):
    match = models.ForeignKey(Match, on_delete=CASCADE)
    player = models.ForeignKey(Player, on_delete=PROTECT)
    sum_spades = models.PositiveSmallIntegerField()
    sum_queens = models.PositiveSmallIntegerField()
    sum_solitaire_lines = models.PositiveSmallIntegerField()
    sum_solitaire_cards = models.PositiveSmallIntegerField()
    sum_pass = models.PositiveSmallIntegerField()
    sum_grand = models.PositiveSmallIntegerField()
    sum_trumph = models.PositiveSmallIntegerField()
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def rating_dif(self) -> Decimal | Literal["?"]:
        if not self.rating:
            return "?"
        older_matches = self.match.get_older_matches().values_list("id", flat=True)
        older_results = PlayerResult.objects.filter(player=self.player).filter(match__id__in=older_matches)
        if older_results.exists():
            previous_rating = older_results.order_by("-match__date", "-match__id")[0].rating
            if previous_rating is None:
                raise ValueError(f"Previous rating is None for {self.player.name=} in {self.match.id=}")
            return self.rating - previous_rating
        else:
            return self.rating - config.RATING_START

    def vals(self) -> dict:
        return {
            "player": {"id": self.player.id, "name": self.player.name},
            "spades": self.sum_spades,
            "queens": self.sum_queens,
            "solitaire_lines": self.sum_solitaire_lines,
            "solitaire_cards": self.sum_solitaire_cards,
            "pass": self.sum_pass,
            "grand": self.sum_grand,
            "trumph": self.sum_trumph,
            "total": self.total(),
            "rating_change": self.rating_dif(),
        }

    def total_before_trumph(self) -> int:
        return (
            self.sum_spades
            + self.sum_queens
            + self.sum_solitaire_lines
            + self.sum_solitaire_cards
            + self.sum_pass
            - self.sum_grand
        )

    def total(self) -> int:
        if self.id is None:  # Is one of the empty rows added by Admin TabularInline
            return 0  # type: ignore[unreachable]
        else:
            return (
                self.sum_spades
                + self.sum_queens
                + self.sum_solitaire_lines
                + self.sum_solitaire_cards
                + self.sum_pass
                - self.sum_grand
                - self.sum_trumph
            )

    def __str__(self) -> str:
        return "Results for %s" % self.player.name

    class Meta:
        unique_together = ("match", "player")


def clear_affected_results_rating(instance: Match, **kwargs: Any) -> None:  # noqa: F841
    newer = instance.get_newer_matches()
    newer_mids = list(newer.values_list("id", flat=True))
    affected_mids = newer_mids + [instance.id]
    PlayerResult.objects.filter(match_id__in=affected_mids).update(rating=None)


post_save.connect(clear_affected_results_rating, sender=Match)
post_delete.connect(clear_affected_results_rating, sender=Match)
