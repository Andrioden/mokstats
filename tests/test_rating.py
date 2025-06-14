from decimal import Decimal

import pytest

from mokstats.rating import RatingCalculator, RatingResult

PLAYER_ID_1 = 1
PLAYER_ID_2 = 2
PLAYER_ID_3 = 3
PLAYER_ID_4 = 4
PLAYER_ID_5 = 5


@pytest.mark.unittest
def test_rating_calculator_win_5_players() -> None:
    # Arrange
    results = [
        RatingResult(PLAYER_ID_1, Decimal("100.0"), 1),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 3),
        RatingResult(PLAYER_ID_4, Decimal("100.0"), 4),
        RatingResult(PLAYER_ID_5, Decimal("100.0"), 5),
    ]

    # Act
    new_player_ratings = RatingCalculator.new_ratings(results)

    # Assert
    assert new_player_ratings[0].rating == Decimal("101.60")
    assert new_player_ratings[1].rating == Decimal("100.80")
    assert new_player_ratings[2].rating == Decimal("100.00")
    assert new_player_ratings[3].rating == Decimal("99.20")
    assert new_player_ratings[4].rating == Decimal("98.40")


@pytest.mark.unittest
def test_rating_calculator_win_4_players() -> None:
    # Arrange
    results = [
        RatingResult(PLAYER_ID_1, Decimal("100.0"), 1),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 3),
        RatingResult(PLAYER_ID_4, Decimal("100.0"), 4),
    ]

    # Act
    new_player_ratings = RatingCalculator.new_ratings(results)

    # Assert
    assert new_player_ratings[0].rating == Decimal("102.00")
    assert new_player_ratings[1].rating == Decimal("100.6666666666666666666666667")
    assert new_player_ratings[2].rating == Decimal("99.33333333333333333333333333")
    assert new_player_ratings[3].rating == Decimal("98.00")


@pytest.mark.unittest
def test_rating_calculator_win_3_players_100() -> None:
    # Arrange
    results = [
        RatingResult(PLAYER_ID_1, Decimal("100.0"), 1),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 3),
    ]

    # Act
    new_player_ratings = RatingCalculator.new_ratings(results)

    # Assert
    assert new_player_ratings[0].rating == Decimal("102.6666666666666666666666667")
    assert new_player_ratings[1].rating == Decimal("100.00")
    assert new_player_ratings[2].rating == Decimal("97.33333333333333333333333333")


@pytest.mark.unittest
def test_rating_calculator_win_3_players_200() -> None:
    # Arrange
    results = [
        RatingResult(PLAYER_ID_1, Decimal("200.0"), 1),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 3),
    ]

    # Act
    new_player_ratings = RatingCalculator.new_ratings(results)

    # Assert
    assert new_player_ratings[0].rating == Decimal("201.3333333333333333333333333")
    assert new_player_ratings[1].rating == Decimal("100.6666666666666666666666667")
    assert new_player_ratings[2].rating == Decimal("98.00")


@pytest.mark.unittest
def test_rating_calculator_draw_pos2() -> None:
    # Arrange
    results = [
        RatingResult(PLAYER_ID_1, Decimal("100.0"), 4),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_4, Decimal("100.0"), 1),
    ]

    # Act
    new_player_ratings = RatingCalculator.new_ratings(results)

    # Assert
    assert new_player_ratings[0].rating == Decimal("98.00")
    assert new_player_ratings[1].rating == Decimal("100.00")
    assert new_player_ratings[2].rating == Decimal("100.00")
    assert new_player_ratings[3].rating == Decimal("102.00")


@pytest.mark.unittest
def test_rating_calculator_draw_pos1() -> None:
    # Arrange
    results = [
        RatingResult(PLAYER_ID_1, Decimal("100.0"), 1),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 1),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 3),
        RatingResult(PLAYER_ID_4, Decimal("100.0"), 4),
    ]

    # Act
    new_player_ratings = RatingCalculator.new_ratings(results)

    # Assert
    assert new_player_ratings[0].rating == Decimal("101.3333333333333333333333333")
    assert new_player_ratings[1].rating == Decimal("101.3333333333333333333333333")
    assert new_player_ratings[2].rating == Decimal("99.33333333333333333333333333")
    assert new_player_ratings[3].rating == Decimal("98.00")
