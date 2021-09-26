from abc import ABC


class IPolicy(ABC):

    def evaluate(self) -> bool:
        pass


class Policy(IPolicy):
    def __init__(self, **kwargs):
        pass

    def evaluate(self) -> bool:
        pass
