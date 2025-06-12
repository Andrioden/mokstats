from decimal import Decimal

import pytest

from mokstats.rating import RatingCalculator, RatingResult


@pytest.mark.django_db
def test_rating_calculator_win_5_players() -> None:
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult("Andriod", Decimal("100.0"), 1),
        RatingResult("Tine", Decimal("100.0"), 2),
        RatingResult("Ole", Decimal("100.0"), 3),
        RatingResult("Johnny", Decimal("100.0"), 4),
        RatingResult("Stian", Decimal("100.0"), 5),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == Decimal("101.60")
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == Decimal("100.80")
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == Decimal("100.00")
        elif p_rating.dbid == "Johnny":
            assert p_rating.rating == Decimal("99.20")
        elif p_rating.dbid == "Stian":
            assert p_rating.rating == Decimal("98.40")


@pytest.mark.django_db
def test_rating_calculator_win_4_players():
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult("Andriod", Decimal("100.0"), 1),
        RatingResult("Tine", Decimal("100.0"), 2),
        RatingResult("Ole", Decimal("100.0"), 3),
        RatingResult("Johnny", Decimal("100.0"), 4),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == Decimal("102.00")
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == Decimal("100.6666666666666666666666667")
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == Decimal("99.33333333333333333333333333")
        elif p_rating.dbid == "Johnny":
            assert p_rating.rating == Decimal("98.00")


@pytest.mark.django_db
def test_rating_calculator_win_3_players_100():
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult("Andriod", Decimal("100.0"), 1),
        RatingResult("Tine", Decimal("100.0"), 2),
        RatingResult("Ole", Decimal("100.0"), 3),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == Decimal("102.6666666666666666666666667")
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == Decimal("100.00")
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == Decimal("97.33333333333333333333333333")


@pytest.mark.django_db
def test_rating_calculator_win_3_players_200():
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult("Andriod", Decimal("200.0"), 1),
        RatingResult("Tine", Decimal("100.0"), 2),
        RatingResult("Ole", Decimal("100.0"), 3),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == Decimal("201.3333333333333333333333333")
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == Decimal("100.6666666666666666666666667")
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == Decimal("98.00")


@pytest.mark.django_db
def test_rating_calculator_draw_pos2():
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult("Andriod", Decimal("100.0"), 4),
        RatingResult("Tine", Decimal("100.0"), 2),
        RatingResult("Ole", Decimal("100.0"), 2),
        RatingResult("Johnny", Decimal("100.0"), 1),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == Decimal("98.00")
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == Decimal("100.00")
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == Decimal("100.00")
        elif p_rating.dbid == "Johnny":
            assert p_rating.rating == Decimal("102.00")


@pytest.mark.django_db
def test_rating_calculator_draw_pos1():
    # Arrange
    calc = RatingCalculator()
    results = [
        RatingResult("Andriod", Decimal("100.0"), 1),
        RatingResult("Tine", Decimal("100.0"), 1),
        RatingResult("Ole", Decimal("100.0"), 3),
        RatingResult("Johnny", Decimal("100.0"), 4),
    ]

    # Act
    new_player_ratings = calc.new_ratings(results)

    # Assert
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == Decimal("101.3333333333333333333333333")
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == Decimal("101.3333333333333333333333333")
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == Decimal("99.33333333333333333333333333")
        elif p_rating.dbid == "Johnny":
            assert p_rating.rating == Decimal("98.00")
