import sys

if sys.platform == "win32":
    import asyncio
    import signal
    from unittest.mock import MagicMock

    try:
        # Avoid socketpair hang on Windows when network sockets are restricted in sandbox/CI
        asyncio.proactor_events.BaseProactorEventLoop._make_self_pipe = (
            lambda self: (setattr(self, "_ssock", MagicMock()), setattr(self, "_csock", MagicMock()))
        )
        asyncio.proactor_events.BaseProactorEventLoop._close_self_pipe = lambda self: None
        asyncio.proactor_events.BaseProactorEventLoop._loop_self_reading = lambda self, f=None: None
        signal.set_wakeup_fd = lambda fd, *, warn_on_full_buffer=True: -1
    except Exception:
        pass
