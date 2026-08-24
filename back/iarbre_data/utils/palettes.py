# front/src/utils/climateZone.ts — CLIMATE_ZONE_COLOR
LCZ_PALETTE: dict[int, str] = {
    1: "#8C0000",
    2: "#D10000",
    3: "#FF0000",
    4: "#BF4D00",
    5: "#FA6600",
    6: "#FF9955",
    7: "#FAEE05",
    8: "#BCBCBC",
    9: "#FFCCAA",
    11: "#006A00",
    12: "#00AA00",
    13: "#648525",
    14: "#B9DB79",
    15: "#000000",
    16: "#FBF7AE",
    17: "#6A6AFF",
}

# front/src/utils/vegetation.ts — STRATE_MAP
VEGESTRATE_PALETTE: dict[int, str] = {
    1: "#C8D96F",
    2: "#3A9144",
    3: "#14452F",
}

# front/src/utils/vulnerability.ts — VulnerabilityColor
VULNERABILITY_STOPS: list[tuple[int, str]] = [
    (1, "#4474b5"),
    (2, "#75add1"),
    (3, "#aad9e9"),
    (4, "#5aaf7b"),
    (5, "#9cbf4e"),
    (6, "#d7e360"),
    (7, "#fdae60"),
    (8, "#f56c43"),
    (9, "#d73026"),
]

# front/src/utils/biosphere_functional_integrity.ts — BiosphereIntegrityColor
BIOSPHERE_STOPS: list[tuple[int, str]] = [
    (0, "#d73026"),
    (12, "#BF5A16"),
    (25, "#A6CC4A"),
    (50, "#55B250"),
    (75, "#025400"),
    (100, "#025400"),
]

PLANTABILITY_STOPS: list[tuple[float, str]] = [
    (-5, "#C4C4C4"),
    (-2, "#BF5A16"),
    (-0.75, "#DDAD14"),
    (0.15, "#A6CC4A"),
    (2.5, "#55B250"),
    (5, "#025400"),
]

VEGESTRATE_COLOR_MAP: dict[int, tuple[int, int, int, int]] = {
    0: (0, 0, 0, 0),
    1: (200, 217, 111, 255),
    2: (58, 145, 68, 255),
    3: (20, 69, 47, 255),
}
