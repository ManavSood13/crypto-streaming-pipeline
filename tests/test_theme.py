import pandas as pd
import pytest

from src.dashboard.theme import (
    UP,
    DOWN,
    NEUTRAL,
    direction_color,
    direction_colors,
    direction_fill,
)
from src.dashboard.charts import create_performance_chart


@pytest.mark.parametrize(
    "value,expected",
    [
        (2.5, UP),
        (0.0001, UP),
        (-2.5, DOWN),
        (-0.0001, DOWN),
        (0, NEUTRAL),
        (None, NEUTRAL),
    ],
)
def test_direction_color(value, expected):
    assert direction_color(value) == expected


def test_direction_colors_maps_each_value():
    assert direction_colors([1, -1, 0]) == [UP, DOWN, NEUTRAL]


def test_direction_fill_is_translucent():
    assert direction_fill(1).startswith("rgba")
    assert direction_fill(-1).startswith("rgba")
    assert direction_fill(None).startswith("rgba")


def test_direction_fill_matches_direction():
    assert "63, 185, 80" in direction_fill(1)
    assert "248, 81, 73" in direction_fill(-1)


def test_performance_chart_colours_bars_by_sign():
    frame = pd.DataFrame(
        [
            {"symbol": "AAA", "price_change_percent": 1.5},
            {"symbol": "BBB", "price_change_percent": -2.0},
            {"symbol": "CCC", "price_change_percent": 0.0},
        ]
    )

    figure = create_performance_chart(frame)

    # The chart sorts ascending before plotting.
    assert list(figure.data[0].marker.color) == [DOWN, NEUTRAL, UP]
