from fastapi import APIRouter, Depends, status

from app.schemas.public.documents import GeneratedDocument, MiddlemanRequest
from app.services.public.deps import get_document_service
from app.services.public.interfaces import DocumentService

router = APIRouter(tags=["documents"])


@router.post("/middleman", response_model=GeneratedDocument, status_code=status.HTTP_201_CREATED)
def middleman(
    body: MiddlemanRequest, svc: DocumentService = Depends(get_document_service)
) -> GeneratedDocument:
    return svc.middleman(body)
