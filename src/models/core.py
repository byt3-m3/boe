from dataclasses import dataclass


@dataclass
class ValueObject:
    pass


@dataclass(frozen=True)
class ImmutableValueObject:
    pass


