"""
Models used by the ALPR module.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class PlateResult:
    """
    Result of a single detected license plate.
    """

    plate: str
    confidence: float

    # (x, y, w, h)
    bbox: tuple[int, int, int, int]

    # Cropped plate image
    image: Optional[np.ndarray] = None

    # Detection timestamp
    timestamp: Optional[str] = None