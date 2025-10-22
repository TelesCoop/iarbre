from enum import IntEnum


class PlantabilityNormalizedThreshold(IntEnum):
    IMPOSSIBLE = 0
    VERY_CONSTRAINED = 2
    CONSTRAINED = 4
    NEUTRAL = 6
    FAVORED = 8
    VERY_FAVORED = 10


PLANTABILITY_THRESHOLDS = [-5, -2, -0.75, 0.15, 2.5, 5]
PLANTABILITY_NORMALIZED = PLANTABILITY_NORMALIZED = [
    threshold.value for threshold in PlantabilityNormalizedThreshold
]

colors = {
    PLANTABILITY_THRESHOLDS[0]: "#C4C4C4",
    PLANTABILITY_THRESHOLDS[1]: "#BF5A16",
    PLANTABILITY_THRESHOLDS[2]: "#DDAD14",
    PLANTABILITY_THRESHOLDS[3]: "#A6CC4A",
    PLANTABILITY_THRESHOLDS[4]: "#55B250",
    PLANTABILITY_THRESHOLDS[5]: "#025400",
}

rgb_colors = {
    k: tuple(int(v.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    for k, v in colors.items()
}


def score_thresholding(value):
    """Function to compute the plantabilty normalize index based on thresholds."""
    for i, threshold in enumerate(PLANTABILITY_THRESHOLDS[:-1]):
        if value <= threshold:
            return i * 2
    return PLANTABILITY_THRESHOLDS[-1]
