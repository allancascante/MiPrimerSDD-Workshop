from pathlib import Path
import os
import signal
import sys

from .service import TaskService
from .storage import JsonTaskStore
from .tui import TaskApp


def main() -> int:
    if (not sys.stdin.isatty() or not sys.stdout.isatty()
            or os.environ.get("TERM", "").lower() == "dumb"):
        print("Curso-PSWE-07 requires an interactive terminal with cursor support.",
              file=sys.stderr)
        return 2
    service = TaskService(JsonTaskStore(Path.home() / ".curso-pswe-07" / "tasks.json"))
    app = TaskApp(service)
    previous = signal.signal(signal.SIGINT, lambda _number, _frame: app.exit(return_code=130))
    try:
        app.run()
        status = app.return_code
        if status is None:
            raise RuntimeError("TUI exited without a status")
        return status
    except KeyboardInterrupt:
        return 130
    finally:
        signal.signal(signal.SIGINT, previous)


if __name__ == "__main__":
    raise SystemExit(main())
