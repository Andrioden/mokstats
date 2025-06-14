from django.db.models import QuerySet

from mokstats.models import PlayerResult


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
