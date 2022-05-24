from fastapi import APIRouter, Depends, Request
from database import ph_records, get_db, get_session, generate_uuid, ph_phones
from sqlalchemy.orm import Session
from random import randint
import hashlib
import json
from schemas import Record, Accept, Preference, startPage, Page1, CommonRes, Page2, Page3, Page4, userMsg, LoggerModel
from utils.tools import detect_intent_texts
from utils.recommend import InitializeUserModel, UpdateUserModel, GetRec, GetSysCri
from utils.function.user_model_default import user_model

api = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


def recommendPhone(pid: int):
    db = get_session()
    phone = db.query(ph_phones).filter(ph_phones.id == pid).first()
    db.close()
    return phone


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
async def prefer(request: Request, page: Preference, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        # 更新记录后包装用户模型
        u_model = user_model.copy()
        # 更新品牌/价格/摄像头像素数
        u_model["user"]["preferenceData"]["brand"] = page.brands.split(",")
        u_model["user"]["preferenceData"]["price"] = [0, page.budget]
        u_model["user"]["preferenceData"]["camera"] = [0, int(page.cameras)]

        # 更新计算后的用户模型
        u_model = InitializeUserModel(u_model)
        u_model['topRecommendedItem'] = u_model['pool'][0]
        # 将模型redis持久化
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        # 获取给用户返回的手机
        resphone = recommendPhone(u_model['pool'][0])
        return {'status': 1, 'msg': 'success', 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


# 更新用户偏好
@api.post("/updatemodel")
async def updatemodel(request: Request, page: LoggerModel, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        u_model = await request.app.state.redis.get(page.uuid)
        print(u_model)
        u_model = json.loads(u_model)
        u_model['logger']['latest_dialog'] = page.logger
        u_model = UpdateUserModel(u_model)
        recommended = GetRec(u_model)
        print(recommended)
        u_model['topRecommendedItem'] = recommended['recommendation_list'][0]
        # 清空最新的操作记录
        u_model['logger']['latest_dialog'] = []
        # 将模型redis持久化
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        resphone = recommendPhone(recommended['recommendation_list'][0])
        return {'status': 1, 'msg': 'success', 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


def parseResponse(res):
    intent = res['intent']
    text = res['text']
    entities = res['entities']
    update_action = {
        "attr": "",
        "action": "",
    }
    if intent == "by_body":
        value = entities['phone-body']
        update_action['attr'] = "phone_thickness"
        if value == "thin":
            update_action['action'] = "low"
        elif value == "thick":
            update_action['action'] = "high"
    elif intent == "by_brand":
        value = entities['phone-brand']
        update_action['attr'] = "brand"
        update_action['action'] = value
    elif intent == "by_camera":
        value = entities['phone-camera']
        update_action['attr'] = "camera"
        if value == "selfie" | "professional":
            update_action['action'] = "high"
    elif intent == "by_cpu":
        value = entities['phone-cpu']
        #TODO: cpu参数不在数据里面，如果没有我们可以再看
        update_action['attr'] = "cpu"
        if value == "powerful":
            update_action['action'] = "high"
    elif intent == "by_os":
        update_action['attr'] = "os1"
        value = entities['phone-os']
        update_action['action'] = value
    elif intent == "by_popularity":
        value = entities['phone-popular']
        update_action['attr'] = "popularity"
        if value == "popular":
            update_action['action'] = "high"
    elif intent == "by_price":
        value = entities['phone-price']
        update_action['attr'] = "price"
        if value == "cheap":
            update_action['action'] = "low"
        elif value == "expensive":
            update_action['action'] = "high"
        elif value == "normal":
            update_action['action'] = "normal"
    elif intent == "by_weight":
        value = entities['phone-weight']
        update_action['attr'] = "phone_weight"
        if value == "light":
            update_action['action'] = "low"
        elif value == "heavy":
            update_action['action'] = "high"
    elif intent == "by_year":
        value = entities['phone-year']
        update_action['attr'] = "year"
        if value == "old":
            update_action['action'] = "low"
        elif value == "new":
            update_action['action'] = "high"
    elif intent == "phone_search_attribute":
        value1 = entities['critique-attribute']
        value2 = entities['critique-action']
        if value1 & value2:
            update_action['attr'] = value1
            update_action['action'] = value2
        else:
            return ("error message")
    elif intent == "by_feature":
        value = entities['phone-feature']
        #TODO:change network
        update_action['attr'] = value
        update_action['action'] = "true"

    updatemodel(update_action)

# 用户消息
@api.post("/userMessage")
def usermsgres(page: userMsg, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        res = detect_intent_texts("phonebot-auym", page.uuid, page.message, 'en')
        print(res['intent'], res['text'], res['entities'])
        #update user model
        parseResponse(res)
        return {'status': 1, 'msg': res['text'], 'phone': 'resphone'}
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
        md5.update(("jyc" + page.uuid).encode("utf-8"))
        code = md5.hexdigest()
        return CommonRes(status=1, msg=code)
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement or try again later.')
