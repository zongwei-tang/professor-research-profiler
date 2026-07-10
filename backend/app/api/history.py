from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.schemas import AnalysisResponse

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[AnalysisResponse])
def get_history_list(user_id: int, db: Session = Depends(get_db)):
    return crud.get_analysis_history(user_id, db)


@router.get("/one", response_model=AnalysisResponse)
def get_history_one(
    user_id: int,
    author_id: int,
    interest: str,
    language: str,
    provider: str,
    db: Session = Depends(get_db),
):
    result = crud.get_one_analysis(user_id, author_id, interest, language, provider, db)
    if result is None:
        raise HTTPException(status_code=404, detail="No matching history record")
    return result

@router.delete('/delete/one')
def delete_history(analysis_id: int, user_id: int, db: Session = Depends(get_db)):
    result = crud.delete_one_history(user_id=user_id, analysis_id=analysis_id, db=db)
    if result:
        return {
            'code': 200,
            'message': 'delete complete'
        }
    else:
        raise HTTPException(status_code=404, detail='failed to delete')
    
@router.delete('/delete/list')
def delete_history_list(user_id: int, db: Session=Depends(get_db)):
    result = crud.delete_history_list(user_id=user_id, db=db)
    if result:
        return {
            'code': 200,
            'message': 'delete complete'
        }
    else:
        raise HTTPException(status_code=404, detail='failed to delete')