import json
from operator import itemgetter

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Avg, Count, Max, Min, QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .config import config
from .models import Match, Place, Player, PlayerResult
from .rating import RatingCalculator, RatingResult
from .utils import month_name, month_number_padded


def index(request: WSGIRequest) -> HttpResponse:
    return render(request, "index.html", {})


def players(request: WSGIRequest) -> HttpResponse:
    places_strings = request.GET.getlist("places[]", None)

    # Validate that all places exists
    place_ids = []
    for place_str in places_strings:
        place_ids.append(get_object_or_404(Place, name=place_str).id)
    if not place_ids:
        place_ids = list(Place.objects.values_list("id", flat=True))
    place_ids = sorted(place_ids)

    # Create stats
    _update_ratings()
    match_winners_cache: dict[int, list[Player]] = {}
    players = []
    for player in Player.objects.all():
        player_results = PlayerResult.objects.filter(player=player)
        player_result_ids = player_results.values_list("match_id", flat=True)
        matches = Match.objects.filter(id__in=player_result_ids, place_id__in=place_ids)
        # Played - Win Ratio
        won = 0
        for match in matches:
            winners = match_winners_cache.get(match.id)
            if winners is None:  # Not in cache
                winners = match.get_winners()
                match_winners_cache[match.id] = winners
            if player in winners:
                won += 1
        played_count = matches.count()
        if played_count == 0:
            win_percent = 0
        else:
            win_percent = int(round(won * 100.00 / played_count))
        # Get last rating
        p_rating: int | str
        if player_results.exists():
            p_rating = int(player_results.order_by("-match__date", "-match__id")[0].rating)  # type: ignore[arg-type]
        else:
            p_rating = "-"
        players.append(
            {
                "id": player.id,
                "name": player.name,
                "played": played_count,
                "won": won,
                "win_perc": win_percent,
                "rating": p_rating,
            }
        )

    places = []
    for place in Place.objects.all():
        p = {"name": place.name}
        p["selected"] = "selected" if (place.id in place_ids) else ""
        places.append(p)
    data = {"players": players, "places": places, "config": {"active_treshold": config.ACTIVE_PLAYER_MATCH_THRESHOLD}}

    return render(request, "players.html", data)


def player(request: WSGIRequest, pid: int) -> HttpResponse:
    _update_ratings()
    player = Player.objects.get(id=pid)
    player_result_ids = PlayerResult.objects.filter(player=player).values_list("match_id", flat=True)
    matches = Match.objects.filter(id__in=player_result_ids)
    # Won - Loss - Other counts
    won = 0
    lost = 0
    for match in matches:
        position = match.get_position(player.id)
        if position == 1:
            won += 1
        elif position == PlayerResult.objects.filter(match=match).count():
            lost += 1
    # Round performance
    all_calc = PlayerResultStatser(PlayerResult.objects.all())
    player_calc = PlayerResultStatser(PlayerResult.objects.filter(player=player))
    round_perf = []
    for round_type in ["spades", "queens", "solitaire", "pass", "grand", "trumph"]:
        if round_type == "solitaire":
            all_avg = all_calc.avg("sum_solitaire_lines + sum_solitaire_cards")
            player_avg = player_calc.avg("sum_solitaire_lines + sum_solitaire_cards")
        else:
            all_avg = all_calc.avg("sum_" + round_type)
            player_avg = player_calc.avg("sum_" + round_type)
        if round_type in ["grand", "trumph"]:
            good_average = player_avg >= all_avg
        else:
            good_average = player_avg < all_avg
        round_perf.append(
            {
                "name": round_type.capitalize(),
                "type": round_type,
                "all_average": all_avg,
                "player_average": player_avg,
                "performance": round((player_avg - all_avg) * 100 / all_avg, 1),
                "good": good_average,
            }
        )
    data = {
        "name": player.name,
        "id": player.id,
        "won": won,
        "lost": lost,
        "played": matches.count(),
        "ratings": player.get_ratings(),
        "round_performances": round_perf,
    }
    return render(request, "player.html", data)


def matches(request: WSGIRequest) -> HttpResponse:
    places = {}
    for place in Place.objects.all():
        places[place.id] = place.name
    matches = []
    for match in Match.objects.all().order_by("-date", "-id"):
        matches.append(
            {
                "id": match.id,
                "year": match.date.year,
                "month": month_name(match.date.month),
                "place": places[match.place_id],  # type: ignore[index]
            }
        )
    data = {"matches": matches}
    return render(request, "matches.html", data)


def match(request: WSGIRequest, mid: int) -> HttpResponse:
    _update_ratings()
    # Get match
    m = Match.objects.select_related("place").get(id=mid)
    results = []
    # Get players result for match
    for result in PlayerResult.objects.select_related("player", "match").filter(match=m):
        vals = result.vals()
        if vals["player"]["id"] in [p.id for p in m.get_winners()]:
            vals["winner"] = True
        else:
            vals["winner"] = False
        results.append(vals)
    # Sort matches by game position
    results = sorted(results, key=lambda result: result["total"])
    # Create context data and return http request
    data = {
        "year": m.date.year,
        "month": month_name(m.date.month),
        "day": m.date.day,
        "place": m.place.name,
        "results": results,
        "next_match_id": m.get_next_match_id(),
        "prev_match_id": m.get_prev_match_id(),
        "moffa_los": results[len(results) - 1]["player"]["name"] == "Bengt",
        "moffa_win": (results[0]["player"]["name"] == "Bengt") and (results[0]["total"] < 0),
        "aase_los": results[len(results) - 1]["player"]["name"] == "Aase",
        "andre_win": results[0]["player"]["name"] == "André",
    }
    return render(request, "match.html", data)


def stats(request: WSGIRequest) -> HttpResponse:
    """This is the stats page that show all the stats that didnt fit
    anywhere else.

    """
    results = PlayerResult.objects.select_related()
    prs = PlayerResultStatser(results)

    total_avg = round(
        sum(
            [
                (
                    r.sum_spades
                    + r.sum_queens
                    + r.sum_solitaire_lines
                    + r.sum_solitaire_cards
                    + r.sum_pass
                    - r.sum_grand
                    - r.sum_trumph
                )
                for r in results
            ]
        )
        / (results.count() * 1.0),
        1,
    )

    best_match_result = prs.bot_total(1)[0]
    worst_match_result = prs.top_total(1)[0]

    trumph_stats = TrumphStatser(results)
    match_count = Match.objects.count()

    data = {
        "spades": {"worst": prs.max("spades"), "gt0_average": prs.gt0_avg("spades")},
        "queens": {"worst": prs.max("queens"), "gt0_average": prs.gt0_avg("queens")},
        "solitaire_lines": {"worst": prs.max("solitaire_lines"), "gt0_average": prs.gt0_avg("solitaire_lines")},
        "solitaire_cards": {"worst": prs.max("solitaire_cards"), "gt0_average": prs.gt0_avg("solitaire_cards")},
        "solitaire_total": {
            "worst": prs.top(1, ["sum_solitaire_lines", "sum_solitaire_cards"])[0],
            "average": prs.avg("sum_solitaire_lines + sum_solitaire_cards"),
        },
        "pass": {"worst": prs.max("pass")},
        "grand": {"best": prs.max("grand")},
        "trumph": {
            "best": prs.max("trumph"),
            "average": prs.avg("sum_trumph"),
            "average_for_trumph_picker": round(trumph_stats.average_trumph_sum_for_trumph_pickers, 1),
            "saved_count": trumph_stats.matches_trumph_picker_not_lost,
            "saved_percent": round(trumph_stats.matches_trumph_picker_not_lost * 100 / float(match_count), 1),
        },
        "extremes": {
            "gain": prs.top(1, ["sum_spades", "sum_queens", "sum_solitaire_lines", "sum_solitaire_cards", "sum_pass"])[
                0
            ],
            "loss": prs.bot(1, ["-sum_grand", "-sum_trumph"])[0],
            "match_size": Match.objects.annotate(count=Count("playerresult"))
            .order_by("-count", "date", "id")
            .values("id", "count")[0],
        },
        "total": {"best": best_match_result, "worst": worst_match_result, "gt0_average": total_avg},
        "match_count": match_count,
    }
    return render(request, "stats.html", data)


def stats_best_results(request: WSGIRequest) -> HttpResponse:
    amount = int(request.GET.get("amount", 20))
    prs = PlayerResultStatser(PlayerResult.objects.select_related())
    data = {"results": prs.bot_total(amount), "title": "%s beste kampresultater" % amount}
    return render(request, "stats-result-list.html", data)


def stats_worst_results(request: WSGIRequest) -> HttpResponse:
    amount = int(request.GET.get("amount", 20))
    prs = PlayerResultStatser(PlayerResult.objects.select_related())
    data = {"results": prs.top_total(amount), "title": "%s dårligste kampresultater" % amount}
    return render(request, "stats-result-list.html", data)


def stats_top_rounds(request: WSGIRequest) -> HttpResponse:
    """Page that show the best results for a specific round type"""
    amount = int(request.GET.get("amount", 20))
    round_type = request.GET.get("round", None)
    if round_type == "solitaire":
        round_value_fields = ["sum_solitaire_lines", "sum_solitaire_cards"]
    else:
        round_value_fields = ["sum_%s" % round_type]
    prs = PlayerResultStatser(PlayerResult.objects.select_related())
    data = {"results": prs.top(amount, round_value_fields), "title": "%s toppresultater for %s " % (amount, round_type)}
    return render(request, "stats-result-list.html", data)


def stats_biggest_match_sizes(request: WSGIRequest) -> HttpResponse:
    match_amount = int(request.GET.get("amount", 20))
    biggest_matches = (
        Match.objects.annotate(count=Count("playerresult"))
        .order_by("-count", "date", "id")
        .values("id", "count", "place__name", "date")
    )
    data: dict[str, list[dict]] = {"matches": []}
    for match in biggest_matches[:match_amount]:
        data["matches"].append(
            {
                "mid": match["id"],
                "size": match["count"],
                "place": match["place__name"],
                "year": match["date"].year,
                "month": month_name(match["date"].month),
                # 'day': match['date'].day,
            }
        )
    return render(request, "stats-biggest-match-sizes.html", data)


def rating(request: WSGIRequest) -> HttpResponse:
    _update_ratings()
    if PlayerResult.objects.count() == 0:
        return render(request, "rating.html", {})
    max_rating = PlayerResult.objects.aggregate(Max("rating"))["rating__max"]
    max_obj = (
        PlayerResult.objects.select_related("player").filter(rating=max_rating).order_by("match__date", "match__id")[0]
    )
    min_rating = PlayerResult.objects.aggregate(Min("rating"))["rating__min"]
    min_obj = (
        PlayerResult.objects.select_related("player").filter(rating=min_rating).order_by("match__date", "match__id")[0]
    )
    # Only list active players
    active_players = []
    players = Player.objects.all()
    for p in players:
        if PlayerResult.objects.filter(player_id=p.id).count() >= config.ACTIVE_PLAYER_MATCH_THRESHOLD:
            active_players.append(p)
    # Create data context and return response
    data = {
        "max": {
            "pid": max_obj.player_id,
            "pname": max_obj.player.name,
            "mid": max_obj.match_id,
            "rating": max_obj.rating,
        },
        "min": {
            "pid": min_obj.player_id,
            "pname": min_obj.player.name,
            "mid": min_obj.match_id,
            "rating": min_obj.rating,
        },
        "players": [p.get_ratings() for p in active_players],
        "player_names": [p.name for p in active_players],
    }
    return render(request, "rating.html", data)


def rating_description(request: WSGIRequest) -> HttpResponse:
    data = {"K_VALUE": int(config.RATING_K), "START_RATING": int(config.RATING_START)}
    return render(request, "rating-description.html", data)


def activity(request: WSGIRequest) -> HttpResponse:
    matches = Match.objects.select_related("place").order_by("date")

    # First do a temporarly dynamic count that spawns from the start to the end
    data: dict[str, dict[int, dict[int, int]]] = {}
    first_year = matches[0].date.year
    last_year = matches[len(matches) - 1].date.year
    for match in matches:
        place = match.place.name
        if place not in data:
            data[place] = {}
            for year in range(first_year, last_year + 1):
                data[place][year] = {}
                for month in range(1, 13):
                    data[place][year][month] = 0
        # Add data
        data[place][match.date.year][match.date.month] += 1

    # use temporarly data to create fitting array for the template grapher
    response_places = []
    response_activities = []
    for place in data:
        place_activity = []
        for year in data[place]:
            for month in data[place][year]:
                c = data[place][year][month]
                month_str = month_number_padded(month)
                place_activity.append(["%s-%s-15" % (year, month_str), c])
        response_places.append(place)
        response_activities.append(place_activity)

    response_data_jsonified = {"places": json.dumps(response_places), "activity": json.dumps(response_activities)}
    return render(request, "activity.html", response_data_jsonified)


def credits(request: WSGIRequest) -> HttpResponse:
    return render(request, "credits.html", {})


def _update_ratings() -> None:
    players = {}
    match_ids = list(set(PlayerResult.objects.filter(rating=None).values_list("match_id", flat=True)))
    for match in Match.objects.filter(id__in=match_ids).order_by("date", "id"):
        player_positions = match.get_positions()
        rating_results = []
        for pp in player_positions:
            # Fetch the current rating value
            rated_results = (
                PlayerResult.objects.filter(player=pp["id"]).exclude(rating=None).order_by("-match__date", "-match__id")
            )
            if not rated_results.exists():
                rating = config.RATING_START
            else:
                rating = rated_results[0].rating  # type: ignore[assignment]
            rating_results.append(RatingResult(pp["id"], rating, pp["position"]))
        # Calculate new ratings
        new_player_ratings = RatingCalculator.new_ratings(rating_results)
        # Update
        for p in new_player_ratings:
            players[p.player_id] = p.rating
            PlayerResult.objects.filter(player=p.player_id).filter(match=match).update(rating=p.rating)


class PlayerResultStatser:
    """Does all kind of statistical fun fact calculations with the supplied PlayerResult object"""

    def __init__(self, all_results: QuerySet[PlayerResult]) -> None:
        self.all_results = all_results

    def max(self, round_type: str) -> dict:
        """Returns min or max value for a round type"""
        field = f"sum_{round_type}"
        val = self.all_results.aggregate(Max(field))[f"{field}__max"]
        results = self.all_results.filter(**{field: val})
        first = results.order_by("match__date", "match__id").select_related()[0]
        return {"sum": val, "mid": first.match_id, "pid": first.player_id, "pname": first.player.name}

    def avg(self, value_field_usage: str) -> float:
        select_query = {"total": f"({value_field_usage})"}
        average = 0.0
        for res in self.all_results.extra(select=select_query):
            average += res.total
        return round(average / self.all_results.count(), 1)

    def gt0_avg(self, round_type: str) -> float:
        """Average score for the round type for results with greater than 0."""
        field = f"sum_{round_type}"
        result = self.all_results.filter(**{f"{field}__gt": 0}).aggregate(Avg(field))
        return round(result[f"{field}__avg"], 1)  # type: ignore[no-any-return]

    def top_total(self, amount: int) -> list[dict]:
        return self.top(
            amount,
            [
                "sum_spades",
                "sum_queens",
                "sum_solitaire_lines",
                "sum_solitaire_cards",
                "sum_pass",
                "-sum_grand",
                "-sum_trumph",
            ],
        )

    def bot_total(self, amount: int) -> list[dict]:
        return self.bot(
            amount,
            [
                "sum_spades",
                "sum_queens",
                "sum_solitaire_lines",
                "sum_solitaire_cards",
                "sum_pass",
                "-sum_grand",
                "-sum_trumph",
            ],
        )

    def bot(self, max_results: int, fields: list[str]) -> list[dict]:
        return self.top(max_results, fields, False)

    def top(self, max_results: int, fields: list[str], reverse: bool = True) -> list[dict]:
        """
        Use format with a prefix to indicate if added or subtracted to the sum used to determine if its sort value:
        [
            "[prefix]<fieldname>",
        ]

        Example:
        [
            "sum_spades",
            "-sum_queens"
        ]

        """

        summarized_results = []
        for result in self.all_results:
            sum = 0
            for field in fields:
                field_multiplicator = 1
                if field[0] == "-":
                    field = field[1:]
                    field_multiplicator = -1
                sum += getattr(result, field) * field_multiplicator

            summarized_results.append(
                {"sum": sum, "mid": result.match_id, "pid": result.player_id, "pname": result.player.name}
            )

        return sorted(summarized_results, key=itemgetter("sum"), reverse=reverse)[:max_results]


class TrumphStatser:
    matches_trumph_picker_not_lost = 0

    def __init__(self, all_results: QuerySet[PlayerResult]):
        self.all_results = all_results
        self.set_trumph_stats()

    def set_trumph_stats(self) -> None:
        match_sorted_results: dict[int, list[PlayerResult]] = {}
        for res in self.all_results.order_by("match"):
            if res.match_id not in match_sorted_results:
                match_sorted_results[res.match_id] = []
            match_sorted_results[res.match_id].append(res)

        trump_sum_for_trumph_pickers = []
        for match_results in match_sorted_results.values():
            trumph_picker_player_result = self.get_trumph_picker_result_from_match_results(match_results)

            if trumph_picker_player_result is None:
                continue
            else:
                # Average trumph picker sum list
                trump_sum_for_trumph_pickers.append(trumph_picker_player_result.sum_trumph)
                # Check if trumph picker avoided loss due to trumph pick
                match_loser_id = self.get_match_loser_id_from_match_results(match_results)
                if match_loser_id is None:
                    pass
                elif trumph_picker_player_result.player_id != match_loser_id:
                    self.matches_trumph_picker_not_lost += 1

        self.average_trumph_sum_for_trumph_pickers = sum(trump_sum_for_trumph_pickers) / float(
            len(trump_sum_for_trumph_pickers)
        )

    def get_trumph_picker_result_from_match_results(self, match_results: list[PlayerResult]) -> PlayerResult | None:
        highest_sum_before_trumph = -1000
        has_multiple_trumphers = False
        trumph_picker_player_result = None

        for res in match_results:
            total_before_trumph = res.total_before_trumph()
            if total_before_trumph > highest_sum_before_trumph:
                highest_sum_before_trumph = total_before_trumph
                trumph_picker_player_result = res
                has_multiple_trumphers = False
            elif total_before_trumph == highest_sum_before_trumph:
                has_multiple_trumphers = True

        if has_multiple_trumphers:
            return None
        else:
            return trumph_picker_player_result

    def get_match_loser_id_from_match_results(self, match_results: list[PlayerResult]) -> int | None:
        highest_total_sum = -1000
        has_multiple_losers = False
        highest_player_result = None

        for res in match_results:
            total = res.total()
            if total > highest_total_sum:
                highest_total_sum = total
                highest_player_result = res
                has_multiple_losers = False
            elif total == highest_total_sum:
                has_multiple_losers = True

        if has_multiple_losers:
            return None
        else:
            return highest_player_result.player_id  # type: ignore
