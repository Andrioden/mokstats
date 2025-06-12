from decimal import Decimal

import pytest

from mokstats.rating import RatingCalculator, RatingResult


@pytest.mark.django_db
def test_rating_calculator_win_5_players() -> None:
    calc = RatingCalculator()

    results = [RatingResult("Andriod", Decimal('100.0'), 1),
               RatingResult("Tine", Decimal('100.0'), 2),
               RatingResult("Ole", Decimal('100.0'), 3),
               RatingResult("Johnny", Decimal('100.0'), 4),
               RatingResult("Stian", Decimal('100.0'), 5)
               ]
    new_player_ratings = calc.new_ratings(results)
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == 104.5
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == 101.5
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == 98.5
        elif p_rating.dbid == "Johnny":
            assert p_rating.rating == 95.5
        elif p_rating.dbid == "Stian":
            assert p_rating.rating == 95.5


@pytest.mark.django_db
def test_rating_calculator_win_4_players():
    calc = RatingCalculator()

    results = [RatingResult("Andriod", Decimal('100.0'), 1),
               RatingResult("Tine", Decimal('100.0'), 2),
               RatingResult("Ole", Decimal('100.0'), 3),
               RatingResult("Johnny", Decimal('100.0'), 4)
               ]
    new_player_ratings = calc.new_ratings(results)
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == 104.5
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == 101.5
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == 98.5
        elif p_rating.dbid == "Johnny":
            assert p_rating.rating == 95.5

@pytest.mark.django_db
def test_rating_calculator_win_3_players():
    calc = RatingCalculator()

    results = [RatingResult("Andriod", Decimal('100.0'), 1),
               RatingResult("Tine", Decimal('100.0'), 2),
               RatingResult("Ole", Decimal('100.0'), 3)]
    new_player_ratings = calc.new_ratings(results)
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == 104.5
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == 101.5
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == 98.5

@pytest.mark.django_db
def test_rating_calculator_win_3_players_2():
    calc = RatingCalculator()
    results = [RatingResult("Andriod", Decimal('200.0'), 1),
               RatingResult("Tine", Decimal('100.0'), 2),
               RatingResult("Ole", Decimal('100.0'), 3)]
    new_player_ratings = calc.new_ratings(results)
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == 104.5
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == 101.5
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == 98.5

@pytest.mark.django_db
def test_rating_calculator_draw():
    calc = RatingCalculator()
    results = [RatingResult("Andriod", Decimal('100.0'), 4),
               RatingResult("Tine", Decimal('100.0'), 2),
               RatingResult("Ole", Decimal('100.0'), 2),
               RatingResult("Johnny", Decimal('100.0'), 1)
               ]
    new_player_ratings = calc.new_ratings(results)
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == 95.5
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == 100.0
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == 100.0
        elif p_rating.dbid == "Johnny":
            assert p_rating.rating == 104.5

@pytest.mark.django_db
def test_rating_calculator_draw_2():
    calc = RatingCalculator()
    results = [RatingResult("Andriod", Decimal('100.0'), 1),
               RatingResult("Tine", Decimal('100.0'), 1),
               RatingResult("Ole", Decimal('100.0'), 3),
               RatingResult("Johnny", Decimal('100.0'), 4)
               ]
    new_player_ratings = calc.new_ratings(results)
    for p_rating in new_player_ratings:
        if p_rating.dbid == "Andriod":
            assert p_rating.rating == 103.0
        elif p_rating.dbid == "Tine":
            assert p_rating.rating == 103.0
        elif p_rating.dbid == "Ole":
            assert p_rating.rating == 98.5
        elif p_rating.dbid == "Johnny":
            assert p_rating.rating == 95.5
