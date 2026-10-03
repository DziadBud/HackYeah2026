from collections.abc import Iterator

from fastapi import HTTPException, status

from app.services.admin.errors import NotFoundError


def map_domain_errors() -> Iterator[None]:
    # yield dependency: keeps routes free of try/except
    try:
        yield
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"not found: {exc}") from exc
