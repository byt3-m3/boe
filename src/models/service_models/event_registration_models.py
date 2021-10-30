from dataclasses import dataclass


@dataclass
class RegisteredEvent:
    name: str
    handler: callable
    factory: callable
    model: object
