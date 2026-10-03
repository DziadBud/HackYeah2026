from collections.abc import Iterator

from fastapi import HTTPException, status

from app.services.admin.errors import (
    EmbedPublishError,
    InvalidUploadError,
    NotFoundError,
    UploadTooLargeError,
)


def map_domain_errors() -> Iterator[None]:
    # yield dependency: keeps routes free of try/except
    try:
        yield
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"not found: {exc}") from exc
    except InvalidUploadError as exc:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, str(exc)) from exc
    except UploadTooLargeError as exc:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)) from exc
    except EmbedPublishError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
