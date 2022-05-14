from fastapi import APIRouter, Depends
from database import ph_records, get_db, generate_uuid, ph_phones
from sqlalchemy.orm import Session
from random import randint
import hashlib
import json
from schemas import Record, Accept, Preference, startPage, Page1, CommonRes, Page2, Page3, Page4, userMsg

api = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


def recommendPhone():
    with open('newPhone.json', 'r') as f:
        phones = json.load(f)
        phone_num = len(phones['pool'])
        item = randint(0, phone_num)
        return phones['pool'][item]


@api.get('/')
async def index():
    return recommendPhone()


@api.get('/phone')
async def phone(id: int, db: Session = Depends(get_db)):
    print(id)
    phone = db.query(ph_phones).filter(ph_phones.id == id).first()
    return phone


# 接受知情同意书，返回接受按钮
@api.post("/accept", response_model=Record)
def accept(user: Accept, db: Session = Depends(get_db)):
    uuid = generate_uuid()
    db_user = ph_records(accT=user.accT, uuid=uuid, device=user.device)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    res = Record(uuid=db_user.uuid)
    return res


# 点击开始按钮
@api.post("/start")
def start(page: startPage, db: Session = Depends(get_db)):
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


# demographic
@api.post("/page1")
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


# 初始化用户偏好
@api.post("/prefer")
def prefer(page: Preference, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        resphone = recommendPhone()

        return {'status': 1, 'msg': 'success', 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


# 用户消息
@api.post("/userMessage")
def usermsgres(page: userMsg, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        resphone = recommendPhone()
        return {'status': 1, 'msg': 'success', 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


# chatbot页面提交时间
@api.post("/page2")
def page2(page: Page2, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        return CommonRes(status=1, msg='success')
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


# post-test的第一页问题
@api.post("/page3")
def page4(page: Page3, db: Session = Depends(get_db)):
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
@api.post("/page4")
def page4(page: Page4, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        md5 = hashlib.md5()
        md5.update("jyc" + page.uuid)
        code = md5.hexdigest()
        return CommonRes(status=1, msg={'msg': 'success', 'code': code})
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement or try again later.')
