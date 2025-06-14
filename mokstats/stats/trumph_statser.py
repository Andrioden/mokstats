from django.db.models import QuerySet

from mokstats.models import PlayerResult


class TrumphStatser:
    def __init__(self, all_results: QuerySet[PlayerResult]):
        self.all_results = all_results
        self.matches_trumph_picker_not_lost = 0
        self.avg_trumph_sum_for_trumph_pickers = 0.0
        self.set_trumph_stats()

    def set_trumph_stats(self) -> None:
        match_sorted_results: dict[int, list[PlayerResult]] = {}
        for res in self.all_results.order_by("match"):
            if res.match_id not in match_sorted_results:
                match_sorted_results[res.match_id] = []
            match_sorted_results[res.match_id].append(res)

        trump_sum_for_trumph_pickers = []
        for match_results in match_sorted_results.values():
            trumph_picker_result = self._get_trumph_picker_result(match_results)
            if trumph_picker_result is None:
                continue

            # Average trumph picker sum list
            trump_sum_for_trumph_pickers.append(trumph_picker_result.sum_trumph)
            # Check if trumph picker avoided loss
            loser_id = self._get_match_loser_id(match_results)
            if loser_id is None:
                continue
            elif trumph_picker_result.player_id != loser_id:
                print("trumf picker not loser", trumph_picker_result.match_id)
                self.matches_trumph_picker_not_lost += 1

        self.avg_trumph_sum_for_trumph_pickers = sum(trump_sum_for_trumph_pickers) / len(trump_sum_for_trumph_pickers)

    @classmethod
    def _get_trumph_picker_result(cls, results: list[PlayerResult]) -> PlayerResult | None:
        highest_sum_before_trumph = max(res.total_before_trumph() for res in results)
        trump_pickers = [res for res in results if res.total_before_trumph() == highest_sum_before_trumph]
        if len(trump_pickers) == 1:
            return trump_pickers[0]
        else:
            return None  # Ignore matches with multiple trumph pickers

    @classmethod
    def _get_match_loser_id(cls, match_results: list[PlayerResult]) -> int | None:
        highest_total_sum = max(res.total() for res in match_results)
        loser_result = [res for res in match_results if res.total() == highest_total_sum]
        if len(loser_result) == 1:
            return loser_result[0].player_id
        else:
            return None  # Ignore matches with multiple trumph pickers
