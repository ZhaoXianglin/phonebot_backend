from fastapi import APIRouter, Depends
from database import ph_records, get_db, generate_uuid, ph_phones
from sqlalchemy.orm import Session
from schemas import IdRecord, Accept, startPage, CommonRes, tutorPage
from utils.tools import detect_intent_texts

api = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


@api.get('/')
async def index():
    intent, res_text = detect_intent_texts("phonebot-auym", '123456789', "hello", 'zh-CN')
    print(intent, '---')


@api.get('/phone')
async def phone(id: int, db: Session = Depends(get_db)):
    print(id)
    phone = db.query(ph_phones).filter(ph_phones.id == id).first()
    return phone


# 接受知情同意书，返回接受按钮
@api.post("/accept", response_model=IdRecord)
def accept(user: Accept, db: Session = Depends(get_db)):
    uuid = generate_uuid()
    db_user = ph_records(accT=user.accT, uuid=uuid, device=user.device)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # 更新条件
    if db_user.id % 4 == 0:
        db_user.identity_cue = 0
        db_user.explanation_style = 0
    if db_user.id % 4 == 1:
        db_user.identity_cue = 0
        db_user.explanation_style = 1
    if db_user.id % 4 == 2:
        db_user.identity_cue = 1
        db_user.explanation_style = 0
    if db_user.id % 4 == 3:
        db_user.identity_cue = 1
        db_user.explanation_style = 1
    # if db_user.id % 8 == 0:
    #     db_user.identity_cue = 0
    #     db_user.explanation_style = 0
    # if db_user.id % 8 == 1:
    #     db_user.identity_cue = 0
    #     db_user.explanation_style = 1
    # if db_user.id % 8 == 2:
    #     db_user.identity_cue = 0
    #     db_user.explanation_style = 2
    # if db_user.id % 8 == 3:
    #     db_user.identity_cue = 0
    #     db_user.explanation_style = 3
    # if db_user.id % 8 == 4:
    #     db_user.identity_cue = 1
    #     db_user.explanation_style = 0
    # if db_user.id % 8 == 5:
    #     db_user.identity_cue = 1
    #     db_user.explanation_style = 1
    # if db_user.id % 8 == 6:
    #     db_user.identity_cue = 1
    #     db_user.explanation_style = 2
    # if db_user.id % 8 == 7:
    #     db_user.identity_cue = 1
    #     db_user.explanation_style = 3
    db.commit()
    db.refresh(db_user)
    res = IdRecord(uuid=db_user.uuid, id=db_user.id, identity_cue=db_user.identity_cue,
                   explanation_style=db_user.explanation_style)
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


# 完成tutorial按钮
@api.post("/tutorial")
def tutorial(page: tutorPage, db: Session = Depends(get_db)):
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
