from fastapi import APIRouter, Depends, Request
from database import ph_records, get_db, ph_phones, get_session
from sqlalchemy.orm import Session

import json
import random
from schemas import Preference, CommonRes, Page2, userMsg, LoggerModel
from utils.tools import detect_intent_texts
from utils.recommend import InitializeUserModel, UpdateUserModel, GetRec, GetSysCri
from utils.function.user_model_default import user_model

chat = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)


def recommendPhone(pid: int):
    """
    查询一部手机
    :param pid: 手机的id值
    :return: 手机的详情
    """
    db = get_session()
    phone = db.query(ph_phones).filter(ph_phones.id == pid).first()
    db.close()
    return phone


# 初始化用户偏好
@chat.post("/prefer")
async def prefer(request: Request, page: Preference, db: Session = Depends(get_db)):
    print(page)
    # 查询用户
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        # 如果用户信息存在，说明做完了前测，可以继续
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        # 写入数据库
        db.flush()

        # 更新记录后包装用户模型
        u_model = user_model.copy()
        if page.brand in ['Apple', 'Samsung', 'Huawei']:
            u_model["user"]["preferenceData"]["brand"] = [page.brand]
        else:
            # 这里是不含'Apple', 'Samsung', 'Huawei'的全部品牌
            brand = ['Xiaomi', 'vivo', 'Oppo', 'Realme', 'Motorola', 'Honor',
                     'ZTE', 'BLU', 'Nokia', 'LG', 'Ulefone', 'Lava', 'TCL',
                     'OnePlus', 'alcatel', 'Asus', 'Lenovo', 'Sony', 'Meizu',
                     'Wiko', 'Tecno', 'Lava', 'Infinix', 'Google']
            if page.brand == '':
                # 如果没选品牌
                selected_brand = random.sample(brand, 5) + ['Apple', 'Samsung', 'Huawei']
                u_model["user"]["preferenceData"]["brand"] = selected_brand
                # print(random.sample(brand, 5))
            else:
                # 选了品牌但是不喜欢这三种'Apple', 'Samsung', 'Huawei'
                u_model["user"]["preferenceData"]["brand"] = random.sample(brand, 8)
        # 更新预算，这是个必选的
        u_model["user"]["preferenceData"]["price"] = [0, int(page.budget)]
        # 初始化电池
        if page.battery == "Large":
            u_model["user"]["preferenceData"]["battery"] = [4499, 13201]
        if page.battery == "Medium":
            u_model["user"]["preferenceData"]["battery"] = [4000, 4999]
        if page.battery == "Small":
            u_model["user"]["preferenceData"]["battery"] = [1299, 4049]

        # 初始化显示
        if page.display_size == "Large":
            u_model["user"]["preferenceData"]["displaysize"] = [6.51, 7.2]
        if page.display_size == "Middle":
            u_model["user"]["preferenceData"]["displaysize"] = [6.21, 6.64]
        if page.display_size == "Small":
            u_model["user"]["preferenceData"]["displaysize"] = [2.3, 6.43]

        # 初始化重量
        if page.weight == "Heavy":
            u_model["user"]["preferenceData"]["phone_weight"] = [191, 493]
        if page.weight == "Medium":
            u_model["user"]["preferenceData"]["phone_weight"] = [170, 201]
        if page.weight == "Light":
            u_model["user"]["preferenceData"]["phone_weight"] = [84, 183]

        print(u_model["user"]["preferenceData"])
        # u_model["user"]["preferenceData"]["camera"] = [int(page.cameras), 108]
        # 更新计算后的用户模型
        u_model = InitializeUserModel(u_model)
        u_model['topRecommendedItem'] = u_model['pool'][0]
        # 获取给用户返回的手机
        resphone = recommendPhone(u_model['pool'][0])
        # 将推荐项从pool中移除
        u_model['pool'].pop(0)
        # 将模型redis持久化
        # print(u_model)
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        resmsg = geneExpBasedOnProductFeatures(u_model['user']['user_preference_model'], resphone,
                                               page.explanation_style)
        return {'status': 1, 'msg': resmsg, 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


# 更新用户偏好,加入购物车
@chat.post("/updatemodel")
async def update_model(request: Request, page: LoggerModel, db: Session = Depends(get_db)):
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
        # 将模型redis持久化
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        # print(u_model, "=========after===========")
        resphone = recommendPhone(u_model['topRecommendedItem'])
        resmsg = geneExpBasedOnProductFeatures(u_model['user']['user_preference_model'], resphone,
                                               page.explanation_style)
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
        if words[1] == 'higher':
            return ['was', 'announced', "recently"]
        else:
            return ['was', 'announced', "earlier"]

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


def attr_to_name(attr, type=1):
    pre_the = " "
    if type == 1:
        pre_the = 'the '
    if attr == 'nettech':
        return pre_the + "cellular network"
    elif attr == "os1":
        return pre_the + 'OS'
    elif attr == "nfc":
        return pre_the + 'NFC'
    elif attr == "fullscreen":
        return pre_the + "screen"
    elif attr == "phone_size":
        return pre_the + "phone size"
    elif attr == "year":
        return pre_the + "release time"
    elif attr == "cpu":
        return pre_the + "processing speed"
    elif attr == "ram":
        return pre_the + "memory"
    elif attr == "displaysize":
        return pre_the + "screen size"
    elif attr == "phone_thickness":
        return pre_the + "thickness"
    elif attr == "phone_weight":
        return pre_the + "weight"
    elif attr == "phone_size":
        return pre_the + "body size"
    elif attr == "battery":
        return pre_the + "battery life"
    else:
        return pre_the + attr


def geneExpBasedOnProductFeatures(user_preference_model, currentItem, explanation_type):
    """
    生成推荐的解释
    :param user_preference_model:
    :param currentItem:
    :param explanation_type:1是 Non-social explanations 2是 Non-social explanations 3 是Social explanations (personal opinions)
    :return:
    """
    currentItem = row2dict(currentItem)
    # print(currentItem)
    keyAttr = user_preference_model['attribute_frequency']
    # print("关键属性", keyAttr)
    # print(keyAttr)
    sortedKeyValue = sort_dict_by_value(keyAttr, True)
    # based on product attributes top two keys
    # 去掉 categorical的属性
    categorical_attributes = ['brand', 'nettech', 'os1', 'nfc', 'fullscreen', 'year']
    keep_items = []
    for item in sortedKeyValue.keys():
        if item not in categorical_attributes:
            keep_items.append(item)
    topkey1 = keep_items[0]
    topkey2 = keep_items[1]

    # topvalue1 = currentItem[topkey1]
    # topvalue2 = currentItem[topkey2]
    # print(topvalue1, topvalue2, explanation_type)

    high = 'high'
    if topkey1 in ['brand', 'nettech', 'os1', 'nfc', 'fullscreen'] or topkey2 in ['brand', 'nettech', 'os1', 'nfc',
                                                                                  'fullscreen']:
        high = 'speical'
    if topkey2 == 'camera':
        topkey2 = 'cam1'
    if topkey1 == 'camera':
        topkey1 = 'cam1'
    if topkey1 == 'fullscreen':
        topkey1 = 'displaysize'
    if topkey2 == 'fullscreen':
        topkey2 = 'displaysize'

    explanation = ""
    # Non-social explanations
    if explanation_type == 1:
        explanation1 = "I recommend this phone because it can meet the " + high + " requirement of {0} and {1}.".format(
            attr_to_name(topkey1, 0), attr_to_name(topkey2, 0))
        explanation2 = "This phone can meet the " + high + " requirement of {0} and {1}, so it might fit you well.".format(
            attr_to_name(topkey1, 0), attr_to_name(topkey2, 0))
        explanation = random.choice([explanation1, explanation2])
    # Social explanations (third-party opinions)
    if explanation_type == 2:
        slot_customers = ["Most", "Some", "Many"]
        slot_think = ["who have similar preferences with you think", "who bought this phone think",
                      'liked this phone because']
        explanation = "<b>{0} of our customers {1}</b> it can meet their {2} requirement for {3} and {4}, so I recommend this phone.".format(
            random.choice(slot_customers), random.choice(slot_think), high, attr_to_name(topkey1, 0),
            attr_to_name(topkey2, 0))
    if explanation_type == 3:
        slot_my = ["tried it out", "tested it", "compared it with other phones"]
        slot_reason = ["can meet my " + high + " requirement for", "can fulfil my need for", "is well rated for"]
        explanation = "I recommend this phone because<b> I have {0} by myself</b> and think it {1} {2} and {3}.".format(
            random.choice(slot_my), random.choice(slot_reason),
            attr_to_name(topkey1), attr_to_name(topkey2))
    if explanation_type == 0:
        msgs = ['I find this phone for you.', 'You may like this phone.', 'Please check this phone.']
        explanation = random.choice(msgs)
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
@chat.post("/syscri")
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
@chat.post("/userMessage")
async def usermsgres(request: Request, page: userMsg, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        res = detect_intent_texts("phonebot-auym", page.uuid, page.message, 'en')
        print(res, 'dialogflow')
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
            # 添加新的品牌到池子里面
            u_model['new_pool'] = phone_ids
        recommended = GetRec(u_model)
        # print(recommended)
        if len(recommended['recommendation_list']) > 0:
            u_model['topRecommendedItem'] = recommended['recommendation_list'][0]
            # 移除已经推荐的项目
            u_model['recommendation_list'] = recommended['recommendation_list'][1:]
            if recommended['recommendation_list'][0] in u_model['pool']:
                u_model['pool'].remove(recommended['recommendation_list'][0])
        else:
            res['text'] = "error"
            u_model['topRecommendedItem'] = u_model['pool'][0]
            # 移除已经推荐的项目
            u_model['pool'].pop(0)
        # 清空最新的操作记录
        u_model['logger']['latest_dialog'] = []
        # 将模型redis持久化
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        resphone = recommendPhone(u_model['topRecommendedItem'])
        res['explain'] = geneExpBasedOnProductFeatures(u_model['user']['user_preference_model'], resphone,
                                                       page.explanation_style)
        # if len(res['text']) < 2 or res['text'] == 'error' or len(res['entities']) == 0:
        #     if len(res['entities']) == 0:
        #         res['explain'] = geneExpBasedOnProductFeatures(u_model['user']['user_preference_model'], resphone,
        #                                                        page.explanation_style)
        #     else:
        #         res['text'] = "I didn't find an appropriate phone for you, maybe you can try this one."
        #         res['explain'] = geneExpBasedOnProductFeatures(u_model['user']['user_preference_model'], resphone,
        #                                                        page.explanation_style)
        #
        # if 'explain' in res:
        #     return {'status': 1, 'msg': res['explain'], 'phone': resphone}
        # else:
        return {'status': 1, 'msg': res['explain'], 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


@chat.post("/page2")
async def page2(request: Request, page: Page2, db: Session = Depends(get_db)):
    user = db.query(ph_records).filter(ph_records.uuid == page.uuid).first()
    if user:
        update_info = page.dict(exclude_unset=True)
        for k, v in update_info.items():
            setattr(user, k, v)
        db.commit()
        db.flush()
        u_model = await request.app.state.redis.get(page.uuid)
        # print(u_model, "=========before===========")
        u_model = json.loads(u_model)
        u_model['logger']['likedItems'] = page.cart
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        return CommonRes(status=1, msg='success')
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')
