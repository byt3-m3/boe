from dataclasses import dataclass

from eventsourcing.domain import Aggregate, AggregateEvent
from typing import Any

@dataclass
class CoreAggregate(Aggregate):
    class PermissionEvent(AggregateEvent):
        context: Any
