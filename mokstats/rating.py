from dataclasses import dataclass
from decimal import Decimal

from .config import config
from .models import Match, PlayerResult


@dataclass
class RatingResult:
    player_id: int
    rating: Decimal
    position: int


class RatingCalculator:
    @classmethod
    def update_ratings(cls) -> None:
        players = {}
        match_ids = list(set(PlayerResult.objects.filter(rating=None).values_list("match_id", flat=True)))
        for match in Match.objects.filter(id__in=match_ids).order_by("date", "id"):
            player_positions = match.get_positions()
            rating_results = []
            for pp in player_positions:
                # Fetch the current rating value
                rated_results = (
                    PlayerResult.objects.filter(player=pp["id"])
                    .exclude(rating=None)
                    .order_by("-match__date", "-match__id")
                )
                if not rated_results.exists():
                    rating = config.RATING_START
                else:
                    rating = rated_results[0].rating  # type: ignore[assignment]
                rating_results.append(RatingResult(pp["id"], rating, pp["position"]))
            # Calculate new ratings
            new_player_ratings = cls._new_ratings(rating_results)
            # Update
            for p in new_player_ratings:
                players[p.player_id] = p.rating
                PlayerResult.objects.filter(player=p.player_id).filter(match=match).update(rating=p.rating)

    @classmethod
    def _new_ratings(cls, player_rating_results: list[RatingResult]) -> list[RatingResult]:
        total_rating = sum([p.rating for p in player_rating_results])
        points_for_position = cls._points_for_position(player_rating_results)
        total_points = sum(points_for_position)
        # unsported_positions =
        # print total_rating
        # print points_for_position
        # print total_points
        for p in player_rating_results:
            # from_rating = p.rating
            win_chance = p.rating / total_rating
            expected_points = total_points * win_chance
            actual_points = points_for_position[p.position - 1]
            p.rating += config.RATING_K * (actual_points - expected_points)
        return player_rating_results

    @classmethod
    def _points_for_position(cls, player_rating_results: list[RatingResult]) -> list[Decimal]:
        """Calculates how much each match positions awards in points, if
        no-one has the same position the for loop does nothing except adding
        and dividing again. The match position to point mapping works as following:
        A total amount of point fluxation is calculated, this defines how much points
        is lost and gained totaly among all players. Then the point fluxation is
        divided among all positions, starting with max and ending with 0.

        """
        # Create the normal position to point mapping
        # Change this part if the balance between position, player count and points awarded
        # needs to be changed.
        point_flux = config.RATING_K * 2  # Total amount of points in movement for 1 match
        points_parts = sum(i for i in range(len(player_rating_results)))
        points = []
        for i in reversed(list(range(len(player_rating_results)))):
            points.append(Decimal(point_flux * i / points_parts))  # Position to points mapping
        # Check if someone has matching positions, then rework the mapping.
        sorted_positions = sorted([p.position for p in player_rating_results])
        for y in range(len(sorted_positions)):
            ypos = sorted_positions[y]
            shared_points = Decimal(0.0)
            shared_by = []
            # Find sharing positions
            for i in range(len(sorted_positions)):
                ipos = sorted_positions[i]
                if ypos == ipos:
                    shared_points += points[i]
                    shared_by.append(i)
                    y = i
            # Divide sharing sum among sharers
            points_each = shared_points / len(shared_by)
            for sharer_pos in shared_by:
                points[sharer_pos] = points_each
        return points
