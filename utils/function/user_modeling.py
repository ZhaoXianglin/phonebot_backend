import pandas as pd
import numpy as np
import pprint
import datetime
import ast
import copy
from utils.function import helper
from utils.function.tool import time_helper

pp = pprint.PrettyPrinter(indent=4)


def categorical_attribute_preference(preferred_value_list):
    value_dict = {}
    for value in preferred_value_list:
        value_dict[value] = 1
    return value_dict


def numerical_attribute_preference(preferred_value_min_max, attribute):
    rank_dict = {}
    if len(preferred_value_min_max) == 0:
        _rank, rank_total = helper.get_numerical_attribute_rank(attribute, -1)
        for i in range(1, rank_total + 1):
            rank_dict[str(i)] = 1
        return rank_dict

    min_rank, rank_total = helper.get_numerical_attribute_rank(attribute, preferred_value_min_max[0])
    max_rank, rank_total = helper.get_numerical_attribute_rank(attribute, preferred_value_min_max[1])

    for i in range(1, rank_total + 1):
        rank_string = str(i)
        if min_rank <= i and i <= max_rank:
            rank_dict[rank_string] = 1
        else:
            rank_dict[rank_string] = 0

    return rank_dict


#  ---- 2022/05
#  version 1: initialize_user_preference_value --- based on the user's specified preference data
def initialize_user_preference_value_based_on_specified_preference(user_preference_data, categorical_attributes,
                                                                   numerical_attributes):
    """
    :param user_preference_data:  用户模型的一部分 传入 user_profile['user']['preferenceData']
    :param categorical_attributes: 分类的数据
    :param numerical_attributes: 分等级的数据
    :return:
    """
    user_preference_value_dict = {}
    # 这里循环创建了一个字典，提到的项目设置为1
    for attr in categorical_attributes:
        if attr not in user_preference_data.keys():
            user_preference_data[attr] = []
        user_preference_value_dict[attr] = categorical_attribute_preference(user_preference_data[attr])
    for attr in numerical_attributes:
        if attr not in user_preference_data.keys():
            user_preference_data[attr] = []
        user_preference_value_dict[attr] = numerical_attribute_preference(user_preference_data[attr], attr)

    pp.pprint(user_preference_value_dict)
    time_helper.print_current_time()
    print("Initialize User Model ---- Initialize preference value based on the user's specified preference data.")

    return user_preference_value_dict


#  ---- 2020/09
#  version 2: initialize_user_preference_value --- based on selected preferred mobile phone (user_preference_data contains N preferred mobile phone name)
def initialize_user_preference_value_based_on_preferred_item(user_preference_data, item_info_dict,
                                                             categorical_attributes, numerical_attributes):
    user_preference_value_dict = {}
    user_preferred_item = user_preference_data['phones']
    user_preferred_item_dict = {}
    for item_id in user_preferred_item:
        user_preferred_item_dict[len(user_preferred_item_dict) + 1] = item_info_dict[item_id]

    user_preferred_item_df = pd.DataFrame.from_dict(user_preferred_item_dict, orient='index')
    # pp.pprint(user_preferred_item_df)
    for attr in categorical_attributes:
        user_preferred_item_attr_df = user_preferred_item_df[attr]
        user_preference_value_dict[attr] = user_preferred_item_attr_df.value_counts().to_dict()
    for attr in numerical_attributes:
        user_preferred_item_attr_df = user_preferred_item_df[attr].astype(str)
        user_preferred_item_attr_value_dict = user_preferred_item_attr_df.value_counts().to_dict()
        attr_rank_label_list = helper.get_numerical_attribute_rank_label(attr)
        for rank in attr_rank_label_list:
            if rank not in user_preferred_item_attr_value_dict.keys():
                user_preferred_item_attr_value_dict[rank] = 0
        user_preference_value_dict[attr] = user_preferred_item_attr_value_dict

    # pp.pprint(user_preference_value_dict)
    time_helper.print_current_time()
    print("Initialize User Model ---- Initialize preference value based on the user's selected preferred items.")

    return user_preference_value_dict


def initialize_user_preference_attribute_frequency(categorical_attributes, numerical_attributes):
    user_preference_attribute_frequency_dict = {}
    for attr in categorical_attributes:
        user_preference_attribute_frequency_dict[attr] = 1
    for attr in numerical_attributes:
        user_preference_attribute_frequency_dict[attr] = 1

    time_helper.print_current_time()
    print("Initialize User Model ---- Initialize attribute frequency as 1 for all attributes.")

    return user_preference_attribute_frequency_dict


def initialize_user_preference_model(user_preference_data, item_info_dict, categorical_attributes,
                                     numerical_attributes):
    """
    初始化用户偏好
    :param user_preference_data: 用户模型的一部分 传入 user_profile['user']['preferenceData']
    :param item_info_dict: 没用到
    :param categorical_attributes: categorical_attributes = ['brand', 'nettech', 'os1', 'nfc', 'fullscreen']
    :param numerical_attributes: numerical_attributes = ['phone_size', 'phone_weight', 'camera', 'storage', 'ram', 'price', 'year', 'cpu', 'battery',
                        'displaysize']
    :return:
    """
    #  ---- 2022/05
    #  version 1: initialize_user_preference_value --- based on specified preference value (e.g. specific brand, or range of price...)
    user_initial_preference_value = initialize_user_preference_value_based_on_specified_preference(user_preference_data,
                                                                                                   categorical_attributes,
                                                                                                   numerical_attributes)

    user_preference_attribute_frequency = initialize_user_preference_attribute_frequency(categorical_attributes,
                                                                                         numerical_attributes)
    user_preference_model = {'preference_value': user_initial_preference_value,
                             'attribute_frequency': user_preference_attribute_frequency}
    # pp.pprint(user_preference_model)
    # time_helper.print_current_time()
    # print("Initialize User Model ---- Preference Model about %d categorical attributes." % len(categorical_attributes))
    # time_helper.print_current_time()
    # print("Initialize User Model ---- Preference Model about %d numerical attributes." % len(numerical_attributes))
    return user_preference_model


def update_user_critique_preference(updated_user_critique_preference, attr, criti_value, critique_item_info,
                                    numerical_attributes, pos_or_neg='pos'):
    new_critique_preference = {}
    new_critique_preference['pos_or_neg'] = pos_or_neg
    new_critique_preference['attribute'] = attr
    new_critique_preference['crit_direction'] = criti_value
    if attr in numerical_attributes:
        if criti_value == 'normal':
            new_critique_preference['crit_direction'] = 'similar'
        new_critique_preference['value'] = critique_item_info[attr]
    updated_user_critique_preference.append(copy.deepcopy(new_critique_preference))

    return updated_user_critique_preference


def update_user_constraints(updated_user_critique_preference, constraint_number):
    top_k_constraints = []
    top_k_constraints_attr_list = []  # store the attributes that has been constrained
    for i in range(len(updated_user_critique_preference)):
        if len(updated_user_critique_preference) - i > 0:
            constraint = updated_user_critique_preference[len(updated_user_critique_preference) - i - 1]
            if constraint['pos_or_neg'] == 'neg' or constraint['attribute'] in top_k_constraints_attr_list:
                continue
            else:
                top_k_constraints.append(constraint)
                top_k_constraints_attr_list.append(constraint['attribute'])

        if len(top_k_constraints) == constraint_number:
            return top_k_constraints
    return top_k_constraints


def update_user_preference_value(updated_user_preference_value, liked_item_info, categorical_attributes,
                                 numerical_attributes):
    # pp.pprint(updated_user_preference_value)

    for attr in categorical_attributes:
        item_v = str(liked_item_info[attr])

        if attr == 'nettech':
            item_v_split = item_v.split('/')
            for item_v_ in item_v_split:
                item_v = item_v_.strip()
                if item_v in updated_user_preference_value[attr].keys():
                    updated_user_preference_value[attr][item_v] = updated_user_preference_value[attr][item_v] + 1
                else:
                    updated_user_preference_value[attr][item_v] = 1

        else:
            if item_v in updated_user_preference_value[attr].keys():
                updated_user_preference_value[attr][item_v] = updated_user_preference_value[attr][item_v] + 1
            else:
                updated_user_preference_value[attr][item_v] = 1

    for attr in numerical_attributes:
        item_v = liked_item_info[attr]
        # value_rank, rank_total = helper.get_numerical_attribute_rank(attr, item_v)
        value_rank = str(item_v)
        updated_user_preference_value[attr][value_rank] = updated_user_preference_value[attr][value_rank] + 1

    # pp.pprint(updated_user_preference_value)
    return copy.deepcopy(updated_user_preference_value)


def update_user_model(user_model, user_interaction_dialog, current_recommended_item,
                      categorical_attributes, numerical_attributes, item_info_dict):
    """
    :param user_model: 用户模型
    :param user_interaction_dialog: 用户和chatbot交互的记录
    :param current_recommended_item: 当前推荐的项目id
    :param categorical_attributes:  预定义的手机属性项
    :param numerical_attributes:  预定义的手机属性项
    :param item_info_dict: 所有的手机，key是id，value是手机json 记录
    :return:
    """
    updated_user_preference_value = user_model['user_preference_model']['preference_value']
    updated_user_attribute_frequency = user_model['user_preference_model']['attribute_frequency']
    updated_user_constraints = user_model['user_constraints']
    updated_user_critique_preference = user_model['user_critique_preference']
    numerical_crit_direction_limit = ['higher', 'lower', 'normal', 'similar']

    for utterance_info in user_interaction_dialog:
        current_action = utterance_info['action'].lower()
        # Condition 1: user critiquing / system suggest critiquing - Yes
        # -> update (1) user critique preference, (2) preference model: attribute frequency, (3) user constraints,

        time_helper.print_current_time()
        print("Update User Model ---- User Action: %s." % current_action)

        if current_action == "user_critique" or current_action == "accept_suggestion":
            critique_list = []
            if 'critique' in utterance_info.keys():
                critique_list = utterance_info['critique']
            critique_item_info = item_info_dict[current_recommended_item]

            time_helper.print_current_time()
            print("Update User Model (%s) ---- Number of Critiques: %d." % (current_action, len(critique_list)))

            for crit in critique_list:
                for attr, criti_value in crit.items():
                    if attr not in numerical_attributes and attr not in categorical_attributes:
                        time_helper.print_current_time()
                        print("Unrecognized attributes: %s." % attr)
                        continue

                    if attr in numerical_attributes and criti_value not in numerical_crit_direction_limit:
                        time_helper.print_current_time()
                        print("Unrecognized critique direction: %s." % criti_value)
                        continue

                    # preference model: attribute frequency
                    updated_user_attribute_frequency[attr] = updated_user_attribute_frequency[attr] * 2 + 1
                    time_helper.print_current_time()
                    print("update attribute frequence: attribute (%s) - %f. " % (
                        attr, updated_user_attribute_frequency[attr]))
                    # user critique preference
                    updated_user_critique_preference = update_user_critique_preference(updated_user_critique_preference,
                                                                                       attr,
                                                                                       criti_value, critique_item_info,
                                                                                       numerical_attributes, 'pos')
            # pp.pprint(updated_user_critique_preference)

            # user constraint
            constraint_number = 5
            updated_user_constraints = update_user_constraints(updated_user_critique_preference, constraint_number)
            # pp.pprint(updated_user_constraints)

            time_helper.print_current_time()
            print("Update User Model ---- Number of Current User Constraints: %d." % len(updated_user_constraints))

        # Condition 2:  system suggest critiquing - No
        # -> update (1) user critique negative
        if current_action == 'reject_suggestion':
            critique_list = []
            if 'critique' in utterance_info.keys():
                critique_list = utterance_info['critique']
            critique_song_info = current_recommended_item

            time_helper.print_current_time()
            print("Update User Model (%s) ---- Number of Critiques: %d." % (current_action, len(critique_list)))

            for crit in critique_list:
                for attr, criti_value in crit.items():

                    check_consective_reject_SC = False
                    # check if there are consective rejected critiques within the same attribute (decrease the attribute frequency)
                    if len(updated_user_critique_preference) > 0:
                        latest_user_critique_preference = updated_user_critique_preference[-1]
                        # time_helper.print_current_time()
                        # print("latest_critique: ", latest_user_critique_preference)
                        if attr in numerical_attributes and latest_user_critique_preference['pos_or_neg'] == 'neg' and \
                                latest_user_critique_preference['attribute'] == attr:
                            check_consective_reject_SC = True
                            updated_user_attribute_frequency[attr] = updated_user_attribute_frequency[attr] / 2
                            time_helper.print_current_time()
                            print("update attribute frequence: attribute (%s) - %f. " % (
                                attr, updated_user_attribute_frequency[attr]))

                    if check_consective_reject_SC == False:
                        updated_user_attribute_frequency[attr] = updated_user_attribute_frequency[attr] * 0.75
                        time_helper.print_current_time()
                        print("update attribute frequence: attribute (%s) - %f. " % (
                            attr, updated_user_attribute_frequency[attr]))

                    # user critique preferencef
                    updated_user_critique_preference = update_user_critique_preference(updated_user_critique_preference,
                                                                                       attr, criti_value,
                                                                                       critique_song_info,
                                                                                       numerical_attributes, 'neg')

        # Condition 3: accept the recommendation
        if current_action == "accept_item" or current_action == "request_rate":
            # ------------------------------------------------
            # Update preference value based on the liked items
            # ------------------------------------------------
            liked_item_info = item_info_dict[current_recommended_item]
            updated_user_preference_value = update_user_preference_value(updated_user_preference_value, liked_item_info,
                                                                         categorical_attributes, numerical_attributes)

            time_helper.print_current_time()
            print("Update User Model ---- Update preference value based on the accepted item.")

    updated_user_preference_model = {'preference_value': updated_user_preference_value,
                                     'attribute_frequency': updated_user_attribute_frequency}

    return updated_user_preference_model, updated_user_constraints, updated_user_critique_preference
