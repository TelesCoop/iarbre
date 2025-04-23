PLANTABILITY_THRESHOLDS = [-5, -2, -0.75, 0.15, 2.5, 5]
PLANTABILITY_NORMALIZED = [0, 2, 4, 6, 8, 10]

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
