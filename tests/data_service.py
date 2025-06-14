from mokstats.models import Match, Player, PlayerResult


class DataService:
    @classmethod
    def create_player_result(cls, match: Match, player: Player, sum_spades: int = 0) -> PlayerResult:
        return PlayerResult.objects.create(
            match=match,
            player=player,
            sum_spades=sum_spades,
            sum_queens=0,
            sum_solitaire_lines=0,
            sum_solitaire_cards=0,
            sum_pass=0,
            sum_grand=0,
            sum_trumph=0,
        )
