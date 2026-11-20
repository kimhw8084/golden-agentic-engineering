"""Pure sample-acceptance logic used by the NiceGUI synthetic fixture."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Measurement:
    sample_id: str
    value: float
    lower_limit: float
    upper_limit: float

    @property
    def accepted(self) -> bool:
        return self.lower_limit <= self.value <= self.upper_limit


def make_measurement(sample_id: str, value: float, lower_limit: float, upper_limit: float) -> Measurement:
    sample_id = sample_id.strip()
    if not sample_id:
        raise ValueError('Sample ID is required.')
    if lower_limit > upper_limit:
        raise ValueError('Lower limit must be less than or equal to upper limit.')
    if not all(map(_finite, (value, lower_limit, upper_limit))):
        raise ValueError('Measurements and limits must be finite numbers.')
    return Measurement(sample_id, value, lower_limit, upper_limit)


def _finite(value: float) -> bool:
    import math
    return math.isfinite(value)
