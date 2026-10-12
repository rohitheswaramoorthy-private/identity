"""
Patents & Copyrights API routes.
"""

from fastapi import APIRouter, Query
from typing import List
from backend.models import PatentRecord
from backend.patents.service import PatentsService

router = APIRouter(prefix="/api/patents", tags=["patents"])
service = PatentsService()

@router.get("", response_model=List[PatentRecord])
async def get_patents(brand: str = Query(..., min_length=1)):
    return await service.get_records(brand)
