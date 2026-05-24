from __future__ import annotations

from src.services import DocumentCopilotService


def main() -> None:
    service = DocumentCopilotService()
    service.ensure_demo_ready()
    result = service.ingest()
    print(result)


if __name__ == "__main__":
    main()
