from dataclasses import dataclass
from typing import List


@dataclass
class PlateResult:
    plate: str
    confidence: float
    bbox: tuple


class ALPREngine:
    def process(self, frame) -> List[PlateResult]:
        return []