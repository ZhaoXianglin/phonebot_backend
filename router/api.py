from fastapi import APIRouter, Depends, Request
from database import ph_records, get_db, get_session, generate_uuid, ph_phones
from sqlalchemy.orm import Session
from random import randint
import hashlib
import json
import random
from schemas import Record, IdRecord, Accept, Preference, startPage, Page1, CommonRes, Page2, Page3, Page4, userMsg, \
    LoggerModel
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
@api.post("/accept", response_model=IdRecord)
def accept(user: Accept, db: Session = Depends(get_db)):
    uuid = generate_uuid()
    db_user = ph_records(accT=user.accT, uuid=uuid, device=user.device)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    res = IdRecord(uuid=db_user.uuid, id=db_user.id, condition=db_user.id % 3 + 1)
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
        u_model["user"]["preferenceData"]["camera"] = [int(page.cameras), 108]

        # 更新计算后的用户模型
        u_model = InitializeUserModel(u_model)
        u_model['topRecommendedItem'] = u_model['pool'][0]
        # 获取给用户返回的手机
        resphone = recommendPhone(u_model['pool'][0])
        # 将推荐项从pool中移除
        u_model['pool'].pop(0)
        # 将模型redis持久化
        print(u_model)
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        return {'status': 1, 'msg': 'success', 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


# 更新用户偏好,加入购物车
@api.post("/updatemodel")
async def updatemodel(request: Request, page: LoggerModel, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        u_model = await request.app.state.redis.get(page.uuid)
        # print(u_model, "=========before===========")
        u_model = json.loads(u_model)
        # 防止池空
        if len(u_model['pool']) < 20:
            print("Danger: pool")
            u_model = InitializeUserModel(u_model)

        u_model['logger']['latest_dialog'] = page.logger
        u_model = UpdateUserModel(u_model)
        if hasattr(u_model, 'recommendation_list'):
            if len(u_model['recommendation_list']) > 0:
                u_model['topRecommendedItem'] = u_model['recommendation_list'][0]
                # 移除已经推荐的项目
                u_model['pool'].remove(u_model['recommendation_list'][0])
                u_model['recommendation_list'] = u_model['recommendation_list'][1:]
            else:
                recommended = GetRec(u_model)
                if len(recommended['recommendation_list']) > 0:
                    u_model['topRecommendedItem'] = recommended['recommendation_list'][0]
                    # 移除已经推荐的项目
                    u_model['recommendation_list'] = recommended['recommendation_list'][1:]
                    u_model['pool'].remove(recommended['recommendation_list'][0])
                else:
                    u_model['topRecommendedItem'] = u_model['pool'][0]
                    # 移除已经推荐的项目
                    u_model['pool'].pop(0)
        else:
            recommended = GetRec(u_model)
            if len(recommended['recommendation_list']) > 0:
                u_model['topRecommendedItem'] = recommended['recommendation_list'][0]
                # 移除已经推荐的项目
                u_model['recommendation_list'] = recommended['recommendation_list'][1:]
                u_model['pool'].remove(recommended['recommendation_list'][0])
            else:
                u_model['topRecommendedItem'] = u_model['pool'][0]
                # 移除已经推荐的项目
                u_model['pool'].pop(0)
        # 清空最新的操作记录
        u_model['logger']['latest_dialog'] = []
        # 将模型redis持久化
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        # print(u_model, "=========after===========")
        resphone = recommendPhone(u_model['topRecommendedItem'])
        resmsg = geneExpBasedOnProductFeatures(u_model['user']['user_preference_model'], resphone)
        if len(resmsg) < 2:
            resmsg = "I didn't find an appropriate phone for you, maybe you can try this one."
        return {'status': 1, 'msg': resmsg, 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


def wordGene(words):
    if words[0] == 'os1': words[0] = 'OS'
    if words[0] == 'nettech': words[0] = 'network type'
    if words[0] == 'phone_size': words[0] = 'phone size'
    if words[0] == 'phone_thickness': words[0] = 'phone thickness'
    if words[0] == 'phone_weight': words[0] = 'phone weight'
    if words[0] == 'display_size': words[0] = 'display size'
    if words[0] == 'brand':
        return ['from', words[1], '']
    if words[0] == 'year':
        return ['announced', 'after', words[1]]

    if words[1] == 'ture':
        return ['with', words[0], '']
    if words[1] == 'false':
        return ['without', words[0], '']
    return ['with', words[1], words[0]]


def createCriRes(critique):
    if len(critique) == 2:
        tp1 = wordGene(critique[0].split("|"))
        tp2 = wordGene(critique[1].split("|"))

        if tp1[0] in ['with', 'without'] and tp2[0] in ['with', 'without'] and tp1[0] != tp2[0]:
            hyphenation = 'but'
        else:
            hyphenation = "and"
        tpl = "Do you want to see phones {0} {1} {2} {3} {4} {5} {6}?".format(tp1[0], tp1[1], tp1[2], hyphenation,
                                                                              tp2[0], tp2[1], tp2[2]).replace("  ", " ")
        return tpl
    else:
        return "I have some phones to recommend to you, would you like to take a look?"


def sort_dict_by_value(d, reverse=False):
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))


def getValueRange(key, value):
    # TODO: judge the range of the key
    explanation_value = ""
    if key == "nettech" or key == "os1":
        explanation_value = " supports " + value
    elif key == "nfc" or key == "fullscreen":
        explanation_value = " supports " + key
    elif key == "brand":
        explanation_value = " is made by " + value
        print(explanation_value)
    elif key == "year":
        # TODO: this value need to be checked again
        if int(value[:4]) > 3:
            explanation_value = " is one of the latest mobile phone released this year."
        else:
            explanation_value = " may has a discount although it is not the latest phone."
    elif key == "phone_size":
        if float(value) > 3:
            explanation_value = " has a large size."
        else:
            explanation_value = " has a small size."
    elif key == "phone_weight":
        if float(value) > 3:
            explanation_value = " looks heavy."
        else:
            explanation_value = " is lightweight."
    elif key == "camera":
        if float(value) > 3:
            explanation_value = " has decent cameras."
        else:
            explanation_value = " has cameras that can meet daily requirements."
    elif key == "storage":
        if float(value) > 3:
            explanation_value = " has a larger storage space."
        else:
            explanation_value = " has a relatively small storage space."
    elif key == "ram":
        if float(value) > 3:
            explanation_value = " has a larger internal storage."
        else:
            explanation_value = " has a modest internal storage."
    elif key == "price":
        if float(value) > 3:
            explanation_value = " is more advanced but also costs more money."
        else:
            explanation_value = " has a lower price."

    return explanation_value


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


def geneExpBasedOnProductFeatures(user_preference_model, currentItem):
    """
    初始化的时候推荐，
    :param user_preference_model:
    :param currentItem:
    :return:
    """
    currentItem = row2dict(currentItem)
    keyAttr = user_preference_model['attribute_frequency']
    sortedKeyValue = sort_dict_by_value(keyAttr, True)
    # based on product attributes top two keys
    keyIndex = random.randint(0, 3)
    topkey1 = list(sortedKeyValue.keys())[keyIndex]
    topkey2 = list(sortedKeyValue.keys())[3 - keyIndex]
    topvalue1 = currentItem[topkey1]
    topvalue2 = currentItem[topkey2]
    explanation = "We recommend this phone because this phone" + getValueRange(topkey1,
                                                                               topvalue1) + " and it" + getValueRange(
        topkey2, topvalue2) + "."
    return explanation


def geneExpBasedOnCrit(user_critique_preference):
    """
    用户发送信息的时候触发
    :param user_critique_preference:
    :return:
    """
    key1 = user_critique_preference['attribute']
    value1 = user_critique_preference['crit_direction']
    explanation = "We recommend this phone because you want the phones that have " + value1 + " " + key1 + "."
    return explanation


# 获取系统推荐
@api.post("/syscri")
async def syscri(request: Request, page: LoggerModel, db: Session = Depends(get_db)):
    # 调用GetSysCri，有两种情况，一种是点击三次try another 情况，另一种是点击let bot suggest
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        u_model = await request.app.state.redis.get(page.uuid)
        u_model = json.loads(u_model)
        # 防止池空
        if len(u_model['pool']) < 20:
            print("Danger: pool")
            u_model = InitializeUserModel(u_model)

        u_model['logger']['latest_dialog'] = page.logger
        response = GetSysCri(u_model)
        # 组装给前端的返回
        phones = {'crit': [], 'phones': []}
        for n, item in enumerate(response['result']):
            phones['crit'].append(createCriRes(item['critique']))
            phones['phones'].append(item['recommendation'])
            for pid in item['recommendation']:
                # 从pool中去掉系统推荐的9项
                if pid in u_model['pool']:
                    print(pid)
                    u_model['pool'].remove(pid)
                if pid in u_model['recommendation_list']:
                    u_model['recommendation_list'].remove(pid)
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        return {'status': 1, 'msg': 'success', 'phones': phones}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


def parseResponse(res):
    intent = res['intent']
    entities = res['entities']
    update_action = {
        "attr": "",
        "action": "",
    }
    if intent == "by_body":
        value = entities['phone-body']
        update_action['attr'] = "phone_thickness"
        if value == "thin":
            update_action['action'] = "lower"
        elif value == "thick":
            update_action['action'] = "higher"
    elif intent == "by_brand":
        value = entities['phone-brand']
        update_action['attr'] = "brand"
        update_action['action'] = value
    elif intent == "by_camera":
        value = entities['phone-camera']
        update_action['attr'] = "camera"
        if value == "selfie" or "professional":
            update_action['action'] = "higher"
    elif intent == "by_cpu":
        value = entities['phone-cpu']
        update_action['attr'] = "cpu"
        if value == "powerful":
            update_action['action'] = "higher"
    elif intent == "by_os":
        update_action['attr'] = "os1"
        value = entities['phone-os']
        update_action['action'] = value
    elif intent == "by_net":
        update_action['attr'] = "nettech"
        value = entities['phone-net']
        update_action['action'] = value
    elif intent == "by_popularity":
        value = entities['phone-popular']
        update_action['attr'] = "popularity"
        if value == "popular":
            update_action['action'] = "higher"
    elif intent == "by_price":
        value = entities['phone-price']
        update_action['attr'] = "price"
        if value == "cheap":
            update_action['action'] = "lower"
        elif value == "expensive":
            update_action['action'] = "higher"
        elif value == "normal":
            update_action['action'] = "normal"
    elif intent == "by_weight":
        value = entities['phone-weight']
        update_action['attr'] = "phone_weight"
        if value == "light":
            update_action['action'] = "lower"
        elif value == "heavy":
            update_action['action'] = "higher"
    elif intent == "by_year":
        value = entities['phone-year']
        update_action['attr'] = "year"
        if value == "old":
            update_action['action'] = "lower"
        elif value == "new":
            update_action['action'] = "higher"
    elif intent == "phone_search_attribute":
        value1 = entities['phone-attribute']
        value2 = entities['critique-action']
        if len(value1) > 0:
            update_action['attr'] = value1[0]
        if len(value2) > 0:
            update_action['action'] = value2[0]
    elif intent == "by_feature":
        value = entities['phone-feature']
        update_action['attr'] = value
        update_action['action'] = "true"

    return {update_action['attr']: update_action['action']}


# 用户消息
@api.post("/userMessage")
async def usermsgres(request: Request, page: userMsg, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        res = detect_intent_texts("phonebot-auym", page.uuid, page.message, 'en')
        parse_res = parseResponse(res)
        page.logger[-1]['critique'].append(parse_res)
        u_model = await request.app.state.redis.get(page.uuid)
        u_model = json.loads(u_model)
        # print(u_model, '-------------')
        u_model['logger']['latest_dialog'] = page.logger
        u_model = UpdateUserModel(u_model)
        # print(u_model, '+++++++++++++')
        # 处理品牌扩展
        if parse_res.__contains__("brand") and parse_res.get('brand') not in u_model['user']['preferenceData']['brand']:
            other_phone = db.query(ph_phones.id).filter(ph_phones.brand == parse_res.get('brand')).all()
            phone_ids = []
            for item in other_phone:
                phone_ids.append(item[0])
            u_model['pool'].extend(phone_ids)
        recommended = GetRec(u_model)
        # print(recommended)
        if len(recommended['recommendation_list']) > 0:
            u_model['topRecommendedItem'] = recommended['recommendation_list'][0]
            # 移除已经推荐的项目
            u_model['recommendation_list'] = recommended['recommendation_list'][1:]
            u_model['pool'].remove(recommended['recommendation_list'][0])
        else:
            res['text'] = "I didn't find an appropriate phone for you, maybe you can try this one."
            u_model['topRecommendedItem'] = u_model['pool'][0]
            # 移除已经推荐的项目
            u_model['pool'].pop(0)
        # 清空最新的操作记录
        u_model['logger']['latest_dialog'] = []
        # 将模型redis持久化
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        resphone = recommendPhone(u_model['topRecommendedItem'])
        if len(res['text']) < 2:
            res['text'] = "I didn't find an appropriate phone for you, maybe you can try this one."
        return {'status': 1, 'msg': res['text'], 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


# prestudy 页面提交时间
@api.post("/page2")
async def page2(request: Request, page: Page2, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            if k == 'page2T':
                setattr(user, k, v)
        db.commit()
        db.flush()
        u_model = await request.app.state.redis.get(page.uuid)
        # print(u_model, "=========before===========")
        u_model = json.loads(u_model)
        u_model['logger']['likedItems'] = page.phonelist
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
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
        return CommonRes(status=1, msg=code[:8].upper())
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement or try again later.')

# 转发请求内容
