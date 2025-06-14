import datetime

import pytest

from mokstats.models import Match, Place, Player
from tests.data_service import DataService


@pytest.mark.django_db
def test_match_get_position() -> None:
    # Arrange - Place/Player
    place = Place.objects.create(name="Place")
    player1 = Player.objects.create(name="Andre")
    player2 = Player.objects.create(name="Tine")
    player3 = Player.objects.create(name="Aase")

    # Test - Match 1
    match1 = Match.objects.create(date=datetime.datetime.now(), place=place)
    DataService.create_player_result(match1, player1)
    DataService.create_player_result(match1, player2)
    DataService.create_player_result(match1, player3)
    assert match1.get_position(player1.id) == 1
    assert match1.get_position(player2.id) == 1
    assert match1.get_position(player3.id) == 1

    # Test - Match 2
    match2 = Match.objects.create(date=datetime.datetime.now(), place=place)
    DataService.create_player_result(match2, player1, sum_spades=1)
    DataService.create_player_result(match2, player2, sum_spades=0)
    DataService.create_player_result(match2, player3, sum_spades=0)
    assert match2.get_position(player1.id) == 3
    assert match2.get_position(player2.id) == 1
    assert match2.get_position(player3.id) == 1

    # Test - Match 3
    match3 = Match.objects.create(date=datetime.datetime.now(), place=place)
    DataService.create_player_result(match3, player1, sum_spades=1)
    DataService.create_player_result(match3, player2, sum_spades=1)
    DataService.create_player_result(match3, player3, sum_spades=0)
    assert match3.get_position(player1.id) == 2
    assert match3.get_position(player2.id) == 2
    assert match3.get_position(player3.id) == 1

    # Test - Match 4
    match4 = Match.objects.create(date=datetime.datetime.now(), place=place)
    DataService.create_player_result(match4, player1, sum_spades=11)
    DataService.create_player_result(match4, player2, sum_spades=22)
    DataService.create_player_result(match4, player3, sum_spades=33)
    assert match4.get_position(player1.id) == 1
    assert match4.get_position(player2.id) == 2
    assert match4.get_position(player3.id) == 3
