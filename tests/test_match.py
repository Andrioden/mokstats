import datetime

import pytest

from mokstats.models import Match, Place, Player, PlayerResult


@pytest.mark.django_db
def test_match_get_position() -> None:
    # Arrange - Place/Player
    place = Place.objects.create(name="Lolplace")

    player1 = Player.objects.create(name="Andre")
    player2 = Player.objects.create(name="Tine")
    player3 = Player.objects.create(name="Aase")

    # Arrange - Match 1
    match1 = Match.objects.create(date=datetime.datetime.now(), place=place)
    PlayerResult.objects.create(sum_spades=0, match=match1, player=player1, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    PlayerResult.objects.create(sum_spades=0, match=match1, player=player2, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    PlayerResult.objects.create(sum_spades=0, match=match1, player=player3, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    # Arrange - Match 2
    match2 = Match.objects.create(date=datetime.datetime.now(), place=place)
    PlayerResult.objects.create(sum_spades=1, match=match2, player=player1, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    PlayerResult.objects.create(sum_spades=0, match=match2, player=player2, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    PlayerResult.objects.create(sum_spades=0, match=match2, player=player3, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    # Arrange - Match 3
    match3 = Match.objects.create(date=datetime.datetime.now(), place=place)
    PlayerResult.objects.create(sum_spades=1, match=match3, player=player1, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    PlayerResult.objects.create(sum_spades=1, match=match3, player=player2, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    PlayerResult.objects.create(sum_spades=0, match=match3, player=player3, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    # Arrange - Match 4
    match4 = Match.objects.create(date=datetime.datetime.now(), place=place)
    PlayerResult.objects.create(sum_spades=11, match=match4, player=player1, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    PlayerResult.objects.create(sum_spades=22, match=match4, player=player2, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)
    PlayerResult.objects.create(sum_spades=33, match=match4, player=player3, sum_queens=0,
                                sum_solitaire_lines=0, sum_solitaire_cards=0, sum_pass=0, sum_grand=0, sum_trumph=0)

    # Assert - Match 1
    assert match1.get_position(player1.id) == 1
    assert match1.get_position(player2.id) == 1
    assert match1.get_position(player3.id) == 1
    # Assert - Match 2
    assert match2.get_position(player1.id) == 3
    assert match2.get_position(player2.id) == 1
    assert match2.get_position(player3.id) == 1
    # Assert - Match 3
    assert match3.get_position(player1.id) == 2
    assert match3.get_position(player2.id) == 2
    assert match3.get_position(player3.id) == 1
    # Assert - Match 4
    assert match4.get_position(player1.id) == 1
    assert match4.get_position(player2.id) == 2
    assert match4.get_position(player3.id) == 3
