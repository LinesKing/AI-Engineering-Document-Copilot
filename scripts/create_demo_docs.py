from __future__ import annotations

from src.config import get_settings
from src.documents.demo import create_demo_documents


def main() -> None:
    settings = get_settings()
    created = create_demo_documents(settings.document_source_path)
    for path in created:
        print(path)


if __name__ == "__main__":
    main()
