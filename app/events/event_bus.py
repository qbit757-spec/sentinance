from typing import Callable, Coroutine, Any
import structlog

logger = structlog.get_logger()


class EventBus:
    def __init__(self):
        self._listeners: dict[str, list[Callable[[Any], Coroutine[Any, Any, None]]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Any], Coroutine[Any, Any, None]]):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(handler)

    async def publish(self, event_type: str, data: Any):
        logger.info("publishing_event", event_type=event_type)
        if event_type in self._listeners:
            for handler in self._listeners[event_type]:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error("event_handler_failed", event_type=event_type, error=str(e))


event_bus = EventBus()


# Decoupled handlers examples
async def on_user_created(user_data: Any):
    logger.info("handler_user_created_executed", user_id=user_data.get("id"))


event_bus.subscribe("UserCreatedEvent", on_user_created)
