"""
Shared chart colours.

Matches the GitHub-dark palette already used in assets/style.css so the
charts and the CSS components agree.
"""

UP = "#3fb950"
DOWN = "#f85149"
NEUTRAL = "#8b949e"

# Translucent variants for fills under a line.
UP_FILL = "rgba(63, 185, 80, 0.15)"
DOWN_FILL = "rgba(248, 81, 73, 0.15)"


def direction_color(value):
    """
    Green for a rise, red for a fall, grey when there is no change or
    no value at all.
    """

    if value is None:
        return NEUTRAL

    if value > 0:
        return UP

    if value < 0:
        return DOWN

    return NEUTRAL


def direction_fill(value):
    """
    Translucent counterpart to `direction_color`.
    """

    if value is None or value == 0:
        return "rgba(139, 148, 158, 0.12)"

    return UP_FILL if value > 0 else DOWN_FILL


def direction_colors(values):
    """
    Per-point colours for a bar chart.
    """

    return [direction_color(value) for value in values]
