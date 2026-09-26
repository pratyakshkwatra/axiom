from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..db.session import get_db
from ..services.ingestion import run_sync

router = APIRouter()

class SyncRequest(BaseModel):
    organization_id: str

@router.post("/")
def trigger_sync(request: SyncRequest, db: Session = Depends(get_db)):
    try:
        stats = run_sync(request.organization_id, db)
        return {"message": "Sync completed successfully", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
