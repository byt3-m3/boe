from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReturnValue:
    value: Any
