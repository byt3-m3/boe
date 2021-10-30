from src.models.service_models.event_registration_models import RegisteredEvent
from src.services.base import Service


class EventRegistrationService(Service):
    def __init__(self):
        self.registered_events = {}

    def register_event(self, event_name: str, event_handler: callable, event_factory: callable, event_model: object):
        if event_name not in self.registered_events.items():
            self.registered_events[event_name] = {}

            registered_event = RegisteredEvent(
                handler=event_handler,
                factory=event_factory,
                model=event_model,
                name=event_name
            )
            self.registered_events[event_name] = registered_event

    def list_events(self):
        """
        List registered events.

        :return:
        """
        return self.registered_events.items()

    def get_event(self, event_name) -> RegisteredEvent:
        return self.registered_events.get(event_name)
