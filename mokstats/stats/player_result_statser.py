from _operator import itemgetter
from django.db.models import Avg, Max

from mokstats.models import Player, PlayerResult


class PlayerResultStatser:
    """Does all kind of statistical fun fact calculations with the supplied PlayerResult object"""

    def __init__(self, player: Player | None = None) -> None:
        if player:
            self.results = PlayerResult.objects.filter(player=player).select_related()
        else:
            self.results = PlayerResult.objects.select_related()

    def max(self, round_type: str) -> dict:
        """Returns min or max value for a round type"""
        field = f"sum_{round_type}"
        val = self.results.aggregate(Max(field))[f"{field}__max"]
        results = self.results.filter(**{field: val})
        first = results.order_by("match__date", "match__id").select_related()[0]
        return {"sum": val, "mid": first.match_id, "pid": first.player_id, "pname": first.player.name}

    def avg(self, value_field_usage: str) -> float:
        select_query = {"total": f"({value_field_usage})"}
        average = 0.0
        for res in self.results.extra(select=select_query):
            average += res.total
        return round(average / self.results.count(), 1)

    def gt0_avg(self, round_type: str) -> float:
        """Average score for the round type for results with greater than 0."""
        field = f"sum_{round_type}"
        result = self.results.filter(**{f"{field}__gt": 0}).aggregate(Avg(field))
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

    def bot(self, amount: int, fields: list[str]) -> list[dict]:
        return self.top(amount, fields, False)

    def top(self, amount: int, fields: list[str], reverse: bool = True) -> list[dict]:
        """
        Fields:

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

        # Step 1 - Build result sums
        match_sizes = {}
        sum_results = []
        for result in self.results:
            if result.match_id not in match_sizes:
                match_sizes[result.match_id] = 0
            match_sizes[result.match_id] += 1
            sum_ = 0
            for field in fields:
                if field[0] == "-":
                    field = field[1:]
                field_multiplication = -1 if field[0] == "-" else 1
                sum_ += getattr(result, field) * field_multiplication

            sum_results.append(
                {"sum": sum_, "mid": result.match_id, "pid": result.player_id, "pname": result.player.name}
            )

        # Step 2 - Append match size to each result
        for res in sum_results:
            res["match_size"] = match_sizes[res["mid"]]  # type: ignore[index]

        # Step 3 - Sort results and return top N
        return sorted(sum_results, key=itemgetter("sum"), reverse=reverse)[:amount]
