from dataclasses import dataclass
from typing import Any, Callable

import numpy as np

from iarbre_data.utils.palettes import (
    BIOSPHERE_STOPS,
    LCZ_PALETTE,
    PLANTABILITY_STOPS,
    VEGESTRATE_PALETTE,
    VULNERABILITY_STOPS,
)

_LCZ_LETTERS = {"A": 11, "B": 12, "C": 13, "D": 14, "E": 15, "F": 16, "G": 17}


def _lcz_index_to_int(value: Any) -> int | None:
    if value is None:
        return None
    s = str(value).strip()
    if s in _LCZ_LETTERS:
        return _LCZ_LETTERS[s]
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def _vegestrate_strate_to_int(value: Any) -> int | None:
    return {"herbacee": 1, "arbustif": 2, "arborescent": 3}.get(
        str(value) if value else ""
    )


def _hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255


def render_fn_from_color_map(color_map: dict) -> Callable:
    def _render(data: np.ndarray) -> np.ndarray:
        rgba = np.zeros((*data.shape, 4), dtype=np.uint8)
        for v, c in color_map.items():
            rgba[data == v] = c
        return rgba

    return _render


@dataclass
class CalqueConfig:
    title: str = ""
    model_name: str | None = None
    field: str | None = None
    dtype: Any = np.uint8
    nodata: int | float = 0
    value_transform: Callable | None = None
    palette: dict[int, str] | None = None
    stops: list[tuple] | None = None
    tif_path: str | None = None

    def make_render_fn(self) -> Callable:
        if self.palette:
            lut = {v: _hex_to_rgba(c) for v, c in self.palette.items()}

            def _render_palette(data: np.ndarray) -> np.ndarray:
                rgba = np.zeros((*data.shape, 4), dtype=np.uint8)
                for v, color in lut.items():
                    rgba[data == v] = color
                return rgba

            return _render_palette

        if self.stops:
            values = np.array([s[0] for s in self.stops], dtype=np.float32)
            colors_arr = np.array(
                [_hex_to_rgba(s[1])[:3] for s in self.stops], dtype=np.float32
            )
            nodata = self.nodata

            def _render_stops(data: np.ndarray) -> np.ndarray:
                rgba = np.zeros((*data.shape, 4), dtype=np.uint8)
                mask = data != nodata
                flat = data[mask].astype(np.float32)
                for i in range(3):
                    rgba[mask, i] = np.clip(
                        np.interp(flat, values, colors_arr[:, i]), 0, 255
                    ).astype(np.uint8)
                rgba[mask, 3] = 255
                return rgba

            return _render_stops

        return lambda data: np.zeros((*data.shape, 4), dtype=np.uint8)


CALQUE_REGISTRY: dict[str, CalqueConfig] = {
    "lcz": CalqueConfig(
        title="Zones Climatiques Locales",
        model_name="Lcz",
        field="lcz_index",
        dtype=np.uint8,
        nodata=0,
        value_transform=_lcz_index_to_int,
        palette=LCZ_PALETTE,
    ),
    "vulnerability": CalqueConfig(
        title="Vulnérabilité",
        model_name="Vulnerability",
        field="vulnerability_index_day",
        dtype=np.float32,
        nodata=-9999.0,
        stops=VULNERABILITY_STOPS,
    ),
    "vegestrate": CalqueConfig(
        title="Végéstrate",
        model_name="Vegestrate",
        field="strate",
        dtype=np.uint8,
        nodata=0,
        value_transform=_vegestrate_strate_to_int,
        palette=VEGESTRATE_PALETTE,
    ),
    "biosphere": CalqueConfig(
        title="Intégrité Fonctionnelle Biosphère",
        model_name="BiosphereFunctionalIntegrity",
        field="indice",
        dtype=np.uint8,
        nodata=255,
        stops=BIOSPHERE_STOPS,
    ),
    "plantability": CalqueConfig(
        title="Plantabilité",
        tif_path="plantability.tif",
        dtype=np.float32,
        nodata=-9999.0,
        stops=PLANTABILITY_STOPS,
    ),
}
