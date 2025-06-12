from decimal import Decimal

import pytest

from mokstats.rating import RatingCalculator, RatingResult

PLAYER_ID_1 = 1
PLAYER_ID_2 = 2
PLAYER_ID_3 = 3
PLAYER_ID_4 = 4
PLAYER_ID_5 = 5


@pytest.mark.django_db
def test_rating_calculator_win_5_players() -> None:
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult(PLAYER_ID_1, Decimal("100.0"), 1),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 3),
        RatingResult(PLAYER_ID_4, Decimal("100.0"), 4),
        RatingResult(PLAYER_ID_5, Decimal("100.0"), 5),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.player_id == PLAYER_ID_1:
            assert p_rating.rating == Decimal("101.60")
        elif p_rating.player_id == PLAYER_ID_2:
            assert p_rating.rating == Decimal("100.80")
        elif p_rating.player_id == PLAYER_ID_3:
            assert p_rating.rating == Decimal("100.00")
        elif p_rating.player_id == PLAYER_ID_4:
            assert p_rating.rating == Decimal("99.20")
        elif p_rating.player_id == PLAYER_ID_5:
            assert p_rating.rating == Decimal("98.40")


@pytest.mark.django_db
def test_rating_calculator_win_4_players() -> None:
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult(PLAYER_ID_1, Decimal("100.0"), 1),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 3),
        RatingResult(PLAYER_ID_4, Decimal("100.0"), 4),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.player_id == PLAYER_ID_1:
            assert p_rating.rating == Decimal("102.00")
        elif p_rating.player_id == PLAYER_ID_2:
            assert p_rating.rating == Decimal("100.6666666666666666666666667")
        elif p_rating.player_id == PLAYER_ID_3:
            assert p_rating.rating == Decimal("99.33333333333333333333333333")
        elif p_rating.player_id == PLAYER_ID_4:
            assert p_rating.rating == Decimal("98.00")


@pytest.mark.django_db
def test_rating_calculator_win_3_players_100() -> None:
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult(PLAYER_ID_1, Decimal("100.0"), 1),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 3),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.player_id == PLAYER_ID_1:
            assert p_rating.rating == Decimal("102.6666666666666666666666667")
        elif p_rating.player_id == PLAYER_ID_2:
            assert p_rating.rating == Decimal("100.00")
        elif p_rating.player_id == PLAYER_ID_3:
            assert p_rating.rating == Decimal("97.33333333333333333333333333")


@pytest.mark.django_db
def test_rating_calculator_win_3_players_200() -> None:
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult(PLAYER_ID_1, Decimal("200.0"), 1),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 3),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.player_id == PLAYER_ID_1:
            assert p_rating.rating == Decimal("201.3333333333333333333333333")
        elif p_rating.player_id == PLAYER_ID_2:
            assert p_rating.rating == Decimal("100.6666666666666666666666667")
        elif p_rating.player_id == PLAYER_ID_3:
            assert p_rating.rating == Decimal("98.00")


@pytest.mark.django_db
def test_rating_calculator_draw_pos2() -> None:
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult(PLAYER_ID_1, Decimal("100.0"), 4),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 2),
        RatingResult(PLAYER_ID_4, Decimal("100.0"), 1),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.player_id == PLAYER_ID_1:
            assert p_rating.rating == Decimal("98.00")
        elif p_rating.player_id == PLAYER_ID_2:
            assert p_rating.rating == Decimal("100.00")
        elif p_rating.player_id == PLAYER_ID_3:
            assert p_rating.rating == Decimal("100.00")
        elif p_rating.player_id == PLAYER_ID_4:
            assert p_rating.rating == Decimal("102.00")


@pytest.mark.django_db
def test_rating_calculator_draw_pos1() -> None:
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult(PLAYER_ID_1, Decimal("100.0"), 1),
        RatingResult(PLAYER_ID_2, Decimal("100.0"), 1),
        RatingResult(PLAYER_ID_3, Decimal("100.0"), 3),
        RatingResult(PLAYER_ID_4, Decimal("100.0"), 4),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.player_id == PLAYER_ID_1:
            assert p_rating.rating == Decimal("101.3333333333333333333333333")
        elif p_rating.player_id == PLAYER_ID_2:
            assert p_rating.rating == Decimal("101.3333333333333333333333333")
        elif p_rating.player_id == PLAYER_ID_3:
            assert p_rating.rating == Decimal("99.33333333333333333333333333")
        elif p_rating.player_id == PLAYER_ID_4:
            assert p_rating.rating == Decimal("98.00")
