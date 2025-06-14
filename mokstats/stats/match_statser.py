from mokstats.models import PlayerResult


class MatchStatser:
    def __init__(self) -> None:
        self.results = PlayerResult.objects.select_related()
        self.count = 0
        self.trumph_multiple_pickers = 0
        self.trumph_matches_picker_not_lost = 0
        self.trumph_avg_total_for_trumph_pickers = 0.0
        self.total_avg = 0.0
        self._init()

    def _init(self) -> None:
        trump_sum_for_trumph_pickers = []
        for match_results in self._match_sorted_results().values():
            self.count += 1
            trumph_picker_candidates = self._get_trumph_picker_candidates(match_results)
            # Multiple trumph pickers in a match?
            if len(trumph_picker_candidates) > 1:
                self.trumph_multiple_pickers += 1
                continue
            # Save sum for average calculation
            trump_sum_for_trumph_pickers.append(trumph_picker_candidates[0].sum_trumph)
            # Check if trumph picker avoided loss
            loser_id = self._get_match_losers(match_results)
            if len(loser_id) > 1:
                continue  # Multiple losers, ignore this match
            elif trumph_picker_candidates[0].player_id != loser_id[0].player_id:
                self.trumph_matches_picker_not_lost += 1

        self.trumph_avg_total_for_trumph_pickers = sum(trump_sum_for_trumph_pickers) / len(trump_sum_for_trumph_pickers)
        self.total_avg = round(sum([r.total() for r in self.results]) / (self.results.count() * 1.0), 1)

    def _match_sorted_results(self) -> dict[int, list[PlayerResult]]:
        match_sorted_results: dict[int, list[PlayerResult]] = {}
        for res in self.results.order_by("match"):
            if res.match_id not in match_sorted_results:
                match_sorted_results[res.match_id] = []
            match_sorted_results[res.match_id].append(res)
        return match_sorted_results

    @classmethod
    def _get_trumph_picker_candidates(cls, results: list[PlayerResult]) -> list[PlayerResult]:
        highest_total_before_trumph = max(res.total_before_trumph() for res in results)
        return [res for res in results if res.total_before_trumph() == highest_total_before_trumph]

    @classmethod
    def _get_match_losers(cls, match_results: list[PlayerResult]) -> list[PlayerResult]:
        highest_total = max(res.total() for res in match_results)
        return [res for res in match_results if res.total() == highest_total]
