from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from database import ph_records


# 获取用户BY uuid
def get_user_by_uuid(db: Session, uuid: str):
    return db.query(ph_records).filter(ph_records.uuid == uuid).first()
