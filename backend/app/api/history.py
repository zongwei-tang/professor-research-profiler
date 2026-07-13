from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas import Analysis

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[Analysis])
def get_history_list(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return crud.get_analysis_history(user_id, db)


@router.delete('/delete/one')
def delete_history(analysis_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    result = crud.delete_one_history(user_id=user_id, analysis_id=analysis_id, db=db)
    if result:
        return {
            'code': 200,
            'message': 'delete complete'
        }
    else:
        raise HTTPException(status_code=404, detail='failed to delete')

@router.delete('/delete/list')
def delete_history_list(user_id: int = Depends(get_current_user_id), db: Session=Depends(get_db)):
    result = crud.delete_history_list(user_id=user_id, db=db)
    if result:
        return {
            'code': 200,
            'message': 'delete complete'
        }
    else:
        raise HTTPException(status_code=404, detail='failed to delete')