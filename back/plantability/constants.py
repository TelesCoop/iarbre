PLANTABILITY_THRESHOLDS = [-3, -2, -0.5, 0.75, 1.5]

colors = {
    -5: "#C4C4C4",
    -2: "#BF5A16",
    -0.75: "#DDAD14",
    0.15: "#A6CC4A",
    1.5: "#55B250",
    5: "#025400",
}

rgb_colors = {
    k: tuple(int(v.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    for k, v in colors.items()
}
