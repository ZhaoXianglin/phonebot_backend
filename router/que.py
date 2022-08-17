from fastapi import APIRouter, Depends
from database import ph_records, get_db
from sqlalchemy.orm import Session
import hashlib
from schemas import Page1, CommonRes, Que1, Que2, Que3, Que4, Scenario

que = APIRouter(
    prefix="/que",
    tags=["que"],
    responses={404: {"description": "Not found"}},
)


# demographic
@que.post("/pre1")
def page1(page: Page1, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        return CommonRes(status=1, msg='success')
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement or try again later.')


@que.post("/scenario")
def page1(page: Scenario, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        return CommonRes(status=1, msg='success')
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement or try again later.')


# post-test的第一页问题
@que.post("/que1")
def que1(page: Que1, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        return CommonRes(status=1, msg='success')
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement or try again later.')


# post-test的第二页的问题
@que.post("/que2")
def que2(page: Que2, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        md5 = hashlib.md5()
        md5.update(("jyc" + page.uuid).encode("utf-8"))
        code = md5.hexdigest()
        return CommonRes(status=1, msg=code[:6].upper())
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement or try again later.')


# post-test的第三页的问题
@que.post("/que3")
def que3(page: Que3, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        return CommonRes(status=1, msg='success')
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement or try again later.')


# post-test的第四页问题

@que.post("/que4")
def que4(page: Que4, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        md5 = hashlib.md5()
        md5.update(("jyc" + page.uuid).encode("utf-8"))
        code = md5.hexdigest()
        return CommonRes(status=1, msg=code[:6].upper())
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement or try again later.')
