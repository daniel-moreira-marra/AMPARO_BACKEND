from typing import Callable, Dict, List, Any

# Simple registry for event handlers
_handlers: Dict[str, List[Callable]] = {}


def register_handler(event_name: str, handler: Callable):
    """Registers a handler for a specific event."""
    if event_name not in _handlers:
        _handlers[event_name] = []
    _handlers[event_name].append(handler)


def dispatch(event_name: str, **kwargs: Any):
    """Dispatches an event to all registered handlers."""
    handlers = _handlers.get(event_name, [])
    for handler in handlers:
        handler(**kwargs)
