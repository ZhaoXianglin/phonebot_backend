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
        if page.displaysize == "Large":
            u_model["user"]["preferenceData"]["displaysize"] = [6.51, 7.2]
        if page.displaysize == "Middle":
            u_model["user"]["preferenceData"]["displaysize"] = [6.21, 6.64]
        if page.displaysize == "Small":
            u_model["user"]["preferenceData"]["displaysize"] = [2.3, 6.43]

        # 初始化重量
        if page.weight == "Heavy":
            u_model["user"]["preferenceData"]["phone_weight"] = [191, 493]
        if page.weight == "Medium":
            u_model["user"]["preferenceData"]["phone_weight"] = [170, 201]
        if page.weight == "Light":
            u_model["user"]["preferenceData"]["phone_weight"] = [84, 183]

        # u_model["user"]["preferenceData"]["camera"] = [int(page.cameras), 108]
        # 更新计算后的用户模型
        u_model = InitializeUserModel(u_model)
        print(u_model["user"]["user_preference_model"]["attribute_frequency"])
        if len(page.weight) > 2:
            u_model["user"]["user_preference_model"]["attribute_frequency"]["phone_weight"] += 1
        if len(page.displaysize) > 2:
            u_model["user"]["user_preference_model"]["attribute_frequency"]["displaysize"] += 1
        if len(page.battery) > 2:
            u_model["user"]["user_preference_model"]["attribute_frequency"]["battery"] += 1
        u_model['topRecommendedItem'] = u_model['pool'][0]
        # 获取给用户返回的手机
        resphone = recommendPhone(u_model['pool'][0])
        # 将推荐项从pool中移除
        u_model['pool'].pop(0)
        # 将模型redis持久化
        # print(u_model)
        await request.app.state.redis.set(page.uuid, json.dumps(u_model))
        resmsg1, resmsg2 = geneExpBasedOnProductFeatures(u_model['user']['user_preference_model'], resphone,
                                                         page.explanation_style)
        return {'status': 1, 'msg': resmsg1, 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


# 更新用户偏好,加入购物车
@chat.post("/updatemodel")
async def update_model(request: Request, page: LoggerModel, db: Session = Depends(get_db)):
    print(page)
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
        resmsg1, resmsg2 = geneExpBasedOnProductFeatures(u_model['user']['user_preference_model'], resphone,
                                                         page.explanation_style, page.phone)
        if len(resmsg1) < 2:
            resmsg1 = "I didn't find an appropriate phone for you, maybe you can try this one."
        return {'status': 1, 'msg': [resmsg1, resmsg2], 'phone': resphone}
    else:
        return CommonRes(status=0, msg='Error, Please accept the informed consent statement first or try again later.')


# 用户消息
@chat.post("/userMessage")
async def usermsgres(request: Request, page: userMsg, db: Session = Depends(get_db)):
    print(page)
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
        resmsg1, resmsg2 = geneExpBasedOnProductFeatures(u_model['user']['user_preference_model'], resphone,
                                                         page.explanation_style, page.phone)
        return {'status': 1, 'msg': [resmsg1, resmsg2], 'phone': resphone}
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


# ====================== 辅助函数 ==========
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


def getValueRange(key, value1, value2):
    """
    :param key: 比较的属性
    :param value1: 旧手机的属性
    :param value2: 新手机的值
    :return: 解释
    """
    compare_res = ''
    if key == "phone_size":
        if float(value1) == float(value2):
            explanation_value = "the same body size"
            compare_res = 'same'
        elif float(value1) < float(value2):
            explanation_value = "a larger body size"
            compare_res = 'low'
        else:
            explanation_value = "a smaller body size"
            compare_res = 'high'

    elif key == "phone_weight":
        if float(value1) == float(value2):
            explanation_value = "the same weight"
            compare_res = 'same'
        elif float(value1) < float(value2):
            explanation_value = "a heavier weight"
            compare_res = 'low'
        else:
            explanation_value = "a lighter weight"
            compare_res = 'high'
    elif key == "camera":
        if float(value1) == float(value2):
            explanation_value = "the same performance for photography"
            compare_res = 'same'
        elif float(value1) < float(value2):
            explanation_value = "a batter performance for photography"
            compare_res = 'high'
        else:
            explanation_value = "a worse performance for photography"
            compare_res = 'low'
    elif key == "storage":
        if float(value1) == float(value2):
            explanation_value = "the same space for storing files"
            compare_res = 'same'
        elif float(value1) < float(value2):
            explanation_value = "a larger space for storing files"
            compare_res = 'high'
        else:
            explanation_value = "a smaller space for storing files"
            compare_res = 'low'
    elif key == "ram":
        if float(value1) == float(value2):
            explanation_value = "the same response speed"
            compare_res = 'same'
        elif float(value1) < float(value2):
            explanation_value = "the capacity to have several applications open at the same time without affecting performance"
            compare_res = 'high'
        else:
            explanation_value = "the limitation of running more applications at the same time"
            compare_res = 'low'
    elif key == "price":
        if float(value1) == float(value2):
            explanation_value = "the same price"
            compare_res = 'same'
        elif float(value1) < float(value2):
            explanation_value = "a more expensive price"
            compare_res = 'low'
        else:
            explanation_value = "a more cost-effective price"
            compare_res = 'high'
    elif key == "cpu":
        if float(value1) == float(value2):
            explanation_value = "the same processing power"
            compare_res = 'same'
        elif float(value1) < float(value2):
            explanation_value = "a faster processing speed"
            compare_res = 'high'
        else:
            explanation_value = "A slower processing speed"
            compare_res = 'low'
    elif key == "battery":
        if float(value1) == float(value2):
            explanation_value = "the same standby time"
            compare_res = 'same'
        elif float(value1) < float(value2):
            explanation_value = "a longer standby time"
            compare_res = 'high'
        else:
            explanation_value = "a shorter standby time"
            compare_res = 'low'
    elif key == "displaysize":
        if float(value1) == float(value2):
            explanation_value = "the same visual effect"
            compare_res = 'same'
        elif float(value1) < float(value2):
            explanation_value = "a better visual effect"
            compare_res = 'high'
        else:
            explanation_value = "a worse visual effect"
            compare_res = 'low'
    elif key == "phone_thickness":
        if float(value1) == float(value2):
            explanation_value = "the same body thickness"
            compare_res = 'same'
        elif float(value1) < float(value2):
            explanation_value = "a thicker body"
            compare_res = 'low'
        else:
            explanation_value = "a slimmer body "
            compare_res = 'high'
    else:
        # 如果没有匹配的话
        explanation_value = "a better preference"
    return explanation_value, compare_res


# 比较适当的属性
def best_attr(phone1, phone2):
    """
    一定会返回两个属性
    :param phone1: 旧手机
    :param phone2: 新手机
    :return:
    """
    attrs = ['weight', 'cam1', 'storage', 'ram', 'price', 'cpu', 'battery', 'displaysize',
             'phone_thickness', 'd1']
    selected_attrs = []
    for item in attrs:
        if item == 'd1':
            print(phone1)
            print(phone2)
            if float(phone2['d1']) * float(phone2['d2']) < float(phone1['d1']) * float(phone1['d2']):
                selected_attrs.append('phone_size')
        elif item in ['weight', 'price', 'phone_thickness']:
            if float(phone2[item]) < float(phone1[item]):
                if item == 'weight':
                    selected_attrs.append('phone_weight')
                else:
                    selected_attrs.append(item)
        else:
            if item == 'cam1':
                if float(phone2[item]) > float(phone1[item]):
                    selected_attrs.append('camera')
            else:
                if float(phone2[item]) > float(phone1[item]):
                    selected_attrs.append(item)
    if len(selected_attrs) < 2:
        for item in attrs:
            if float(phone2[item]) == float(phone1[item]):
                if item == 'd1':
                    selected_attrs.append('phone_size')
                elif item == 'cam1':
                    selected_attrs.append('camera')
                elif item == 'weight':
                    selected_attrs.append('phone_weight')
                else:
                    selected_attrs.append(item)
    if len(selected_attrs) == 1:
        selected_attrs.append('price')
    if len(selected_attrs) == 0:
        selected_attrs.append('price')
        selected_attrs.append('phone_size')
    return selected_attrs


def geneExpBasedOnProductFeatures(user_preference_model, currentItem, explanation_type, oldItem=None):
    """
    生成推荐的解释
    :param user_preference_model:
    :param currentItem:
    :param explanation_type:1是 Non-social explanations 2是 Non-social explanations 3 是Social explanations (personal opinions)
    :return:
    """
    currentItem = row2dict(currentItem)

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
    topkey2 = random.choice(keep_items[1:])
    if oldItem is not None:
        topkey2 = best_attr(oldItem, currentItem)[0]
        if topkey2 == topkey1:
            topkey2 = best_attr(oldItem, currentItem)[1]

    high = 'high'
    if topkey1 in ['brand', 'nettech', 'os1', 'nfc', 'fullscreen'] or topkey2 in ['brand', 'nettech', 'os1', 'nfc',
                                                                                  'fullscreen']:
        high = 'speical'

    if topkey1 == 'fullscreen':
        topkey1 = 'displaysize'
    if topkey2 == 'fullscreen':
        topkey2 = 'displaysize'

    attr1 = topkey1
    attr2 = topkey2
    if topkey1 == 'phone_size':
        attr1 = 'd1'
    if topkey2 == 'phone_size':
        attr2 = 'd1'
    if topkey1 == 'phone_weight':
        attr1 = 'weight'
    if topkey2 == 'phone_weight':
        attr2 = 'weight'
    if topkey1 == 'camera':
        attr1 = 'cam1'
    if topkey2 == 'camera':
        attr2 = 'cam1'

    explanation = ""
    # Non-social explanations
    if explanation_type == 1:
        # 获得排名情况
        res = rank_phone(attr1, currentItem[attr1], attr2, currentItem[attr2])
        print(res, topkey1, topkey2)
        explanation = "I recommend this phone because it ranks top {0}% for <b>{1}</b> and top {2}% for <b>{3}</b> among 1200 phones in our product library.".format(
            res[0], attr_to_name_new(topkey1), res[1], attr_to_name_new(topkey2))

    # Social explanations (third-party opinions)
    if explanation_type == 2:
        slot_customers = ["Most", "Some", "Many"]
        slot_think = ["who have similar preferences with you think", "who bought this phone think",
                      'liked this phone because']
        explanation = "{0} of our customers {1} it can meet their {2} requirement for <b>{3}</b> and <b>{4}</b>, so I recommend this phone.".format(
            random.choice(slot_customers), random.choice(slot_think), high, attr_to_name(topkey1, 0),
            attr_to_name(topkey2, 0))
    if explanation_type == 3:
        slot_my = ["tried it out", "tested it", "compared it with other phones"]
        slot_reason = ["can meet my " + high + " requirement for", "can fulfil my need for"]
        explanation = "I recommend this phone becauseI have {0} by myself and think it {1} <b>{2}</b> and <b>{3}</b>.".format(
            random.choice(slot_my), random.choice(slot_reason),
            attr_to_name(topkey1, 0), attr_to_name(topkey2, 0))
    if explanation_type == 0:
        msgs = ['I find this phone for you.', 'You may like this phone.', 'Please check this phone.']
        explanation = random.choice(msgs)

    tpl = ""
    if oldItem is not None:
        compare1, compare_ras1 = getValueRange(topkey1, oldItem[attr1], currentItem[attr1])
        compare2, compare_ras2 = getValueRange(topkey2, oldItem[attr2], currentItem[attr2])
        if explanation_type == 1:
            if compare_ras1 == 'high':
                temp_val = cal_better_range(oldItem[attr1], currentItem[attr1])
                if temp_val != 0:
                    compare1 += " ({0}%)".format(temp_val)
            if compare_ras2 == 'high':
                temp_val = cal_better_range(oldItem[attr2], currentItem[attr2])
                if temp_val != 0:
                    compare2 += " ({0}%)".format(cal_better_range(oldItem[attr2], currentItem[attr2]))
        and_but = "but"
        if compare_ras1 == compare_ras2:
            and_but = "and"
        tpl = "Compared with the previous phone, this phone has {0} {1} {2}.".format(compare1, and_but, compare2)
    return explanation, tpl


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


def attr_to_name_new(attr):
    if attr == 'phone_size':
        return "body size (slim)"
    elif attr == "phone_weight":
        return "weight (light)"
    elif attr == "camera":
        return "cameras"
    elif attr == "storage":
        return "storage space"
    elif attr == "ram":
        return "memory"
    elif attr == "price":
        return "price"
    elif attr == "cpu":
        return "processing speed"
    elif attr == "battery":
        return "standby time"
    elif attr == "displaysize":
        return "screen size"
    elif attr == "phone_thickness":
        return "thickness (thin)"
    else:
        return attr


def sort_dict_by_value(d, reverse=False):
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


def rank_phone(attr1, val1, attr2, val2):
    val1 = float(val1)
    val2 = float(val2)
    numerical_attributes = ['d1', 'weight', 'price', 'phone_thickness']
    db = get_session()
    print(attr1, attr2)
    if attr1 == 'd1':
        count1 = db.query(ph_phones).filter(ph_phones.d1 > val1).count()
    if attr2 == 'd1':
        count2 = db.query(ph_phones).filter(ph_phones.d1 > val2).count()
    if attr1 == 'weight':
        count1 = db.query(ph_phones).filter(ph_phones.weight > val1).count()
    if attr2 == 'weight':
        count2 = db.query(ph_phones).filter(ph_phones.weight > val2).count()
    if attr1 == 'cam1':
        count1 = db.query(ph_phones).filter(ph_phones.cam1 > val1).count()
    if attr2 == 'cam1':
        count2 = db.query(ph_phones).filter(ph_phones.cam1 > val2).count()
    if attr1 == 'storage':
        count1 = db.query(ph_phones).filter(ph_phones.storage > val1).count()
    if attr2 == 'storage':
        count2 = db.query(ph_phones).filter(ph_phones.storage > val2).count()
    if attr1 == 'ram':
        count1 = db.query(ph_phones).filter(ph_phones.ram > val1).count()
    if attr2 == 'ram':
        count2 = db.query(ph_phones).filter(ph_phones.ram > val2).count()
    if attr1 == 'price':
        count1 = db.query(ph_phones).filter(ph_phones.price > val1).count()
    if attr2 == 'price':
        count2 = db.query(ph_phones).filter(ph_phones.price > val2).count()
    if attr1 == 'cpu':
        count1 = db.query(ph_phones).filter(ph_phones.cpu > val1).count()
    if attr2 == 'cpu':
        count2 = db.query(ph_phones).filter(ph_phones.cpu > val2).count()
    if attr1 == 'battery':
        count1 = db.query(ph_phones).filter(ph_phones.battery > val1).count()
    if attr2 == 'battery':
        count2 = db.query(ph_phones).filter(ph_phones.battery > val2).count()
    if attr1 == 'displaysize':
        count1 = db.query(ph_phones).filter(ph_phones.displaysize > val1).count()
    if attr2 == 'displaysize':
        count2 = db.query(ph_phones).filter(ph_phones.displaysize > val2).count()
    if attr1 == 'phone_thickness':
        count1 = db.query(ph_phones).filter(ph_phones.phone_thickness > val1).count()
    if attr2 == 'phone_thickness':
        count2 = db.query(ph_phones).filter(ph_phones.phone_thickness > val2).count()
    db.close()
    print(attr1, val1, count1, attr2, val2, count2)
    if attr1 in numerical_attributes:
        count1 = 1 - count1 / 1265
    else:
        count1 = count1 / 1265
    if attr2 in numerical_attributes:
        count2 = 1 - count2 / 1265
    else:
        count2 = count2 / 1265

    count1 = round(count1 * 100, 2)
    count2 = round(count2 * 100, 2)
    if count1 < 1:
        count1 = 1.00
    if count2 < 1:
        count2 = 1.00
    return count1, count2


def cal_better_range(val1, val2):
    return round(((float(val2) - float(val1)) / float(val1)) * 100, 2)
