import numpy as np
import pandas as pd
import operator
import math
import time, datetime
import sys

sys.path.append("..")
from utils.function.tool import time_helper, load_data, store_data


def get_numerical_attribute_interval_label(attribute, value):
    attribut_interval, interval_label = get_numerical_attribute_intervalindex(attribute)
    intervals = pd.IntervalIndex.from_breaks(attribut_interval, closed='left')
    interval_find = list(intervals.contains(value))
    index = interval_find.index(True)
    value_interval_label = interval_label[index]
    return value_interval_label


# -------------------------------------------------------------------------------------------
#  Numerical Attribute Processing (for Phone Domain)
# -------------------------------------------------------------------------------------------

# def get_numerical_attribute_label_phone(attribute, intervalindex_true=False):

#     attribute_intervalindex = None
#     phone_data_file = 'data/new_phone_data_v2.json'
#     phone_data_df = load_data.load_phone_data_df(phone_data_file)

#     attributes_cut_with_quantile_5 = ['displaysize', 'displayratio','cam1','cam2', 'battery'  ]
#     attributes_cut_with_quantile_10 =  ['price', 'popularity']
#     # print(phone_data_df.head())
#     quantile_list = None
#     label_list = None

#     print (attribute)
#     if attribute in attributes_cut_with_quantile_5:
#         quantile_5 = list(np.around(np.arange(0,1.1, 0.2), decimals=1))
#         quantile_list = list(phone_data_df[attribute].quantile(quantile_5))
#         quantile_list[-1] = math.ceil(quantile_list[-1]+0.01)
#     if attribute in attributes_cut_with_quantile_10:
#         quantile_10 = list(np.around(np.arange(0,1.1, 0.1), decimals=1))
#         quantile_list = list(phone_data_df[attribute].quantile(quantile_10))
#         quantile_list[-1] = math.ceil(quantile_list[-1]+0.01)
#     print (quantile_list)


#     intervalindex = pd.IntervalIndex.from_breaks(quantile_list, closed='left')
#     interval_label = intervalindex.astype(str)
#     if intervalindex_true == True:
#         return quantile_list, interval_label
#     else:
#         return interval_label

# def get_numerical_attribute_label_phone(attribute, intervalindex_true=False):


#     quantile_list = None
#     label_list = None

#     if attribute == 'displaysize':
#         quantile_list = [2.8, 5.5, 5.8, 6.2, 6.4, 8]
#     if attribute == 'displayratio':
#         quantile_list = [26.7, 70.9, 76.3, 81.4, 84.2, 95]
#     if attribute == 'cam1':
#         quantile_list = [2.0, 12.0, 13.0, 13.0, 23.0, 109]
#     if attribute == 'cam2':
#         quantile_list = [0.3, 5.0, 8.0, 13.0, 20.0, 41]
#     if attribute == 'battery':
#         quantile_list = [3.0, 3000.0, 3300.0, 3973.2, 4025.0, 9001]
#     if attribute == 'price':
#         quantile_list = [40.0, 109.0, 140.4, 163.5, 196.2, 218.475, 272.5, 325.9, 403.3, 545.0, 2100]
#     if attribute == 'popularity':
#         quantile_list = [1435.0, 74639.6, 156367.4, 267744.7, 417682.6, 657124.5, 1050671.0, 1603503.2, 2658505.0, 5206509.6, 40991523]

#     intervalindex = pd.IntervalIndex.from_breaks(quantile_list, closed='left')
#     interval_label = intervalindex.astype(str)
#     if intervalindex_true == True:
#         return quantile_list, interval_label
#     else:
#         return interval_label

def get_numerical_attribute_rank(attribute, value):
    # Phone Data Numerical Bin Edges List for Rank
    # phone_data_numerical_bin_edges = 'data/phone_data_numerical_bin_edges.json'
    # phone_data_numerical_bin_edges_dict = load_data.load_json_data(phone_data_numerical_bin_edges)

    phone_data_numerical_bin_edges_dict = get_phone_data_numerical_bin_edges_dict()
    attribute_bin_edges = phone_data_numerical_bin_edges_dict[attribute]
    rank_total = len(attribute_bin_edges) - 1
    # print(rank_total)
    if value < attribute_bin_edges[0]:
        return 1, rank_total

    value_rank = 1
    for bin_edge in attribute_bin_edges[1:]:
        if value < bin_edge:
            return value_rank, rank_total
        value_rank += 1

    return value_rank, rank_total


def get_numerical_attribute_rank_label(attribute):
    phone_data_numerical_bin_edges_dict = get_phone_data_numerical_bin_edges_dict()
    attribute_bin_edges = phone_data_numerical_bin_edges_dict[attribute]
    rank_total = len(attribute_bin_edges) - 1
    rank_label_list = []
    i = 1
    while i <= rank_total:
        rank_label_list.append(str(i))
        i = i + 1
    return rank_label_list


def get_phone_data_numerical_bin_edges_dict():
    phone_data_numerical_bin_edges_dict = {
        "storage": [
            4.0,
            32.0,
            64.0,
            128.0,
            513.0
        ],
        "ram": [
            0.5,
            3.0,
            4.0,
            6.0,
            8.0,
            19.0
        ],
        "phone_size": [
            117.4,
            173.8,
            176.7,
            180.1,
            181.6,
            203.0
        ],
        "phone_thickness": [
            6.800000190734863,
            8.0,
            8.399999618530273,
            8.899999618530273,
            9.199999809265137,
            24.0
        ],
        "phone_weight": [
            84.5,
            171.0,
            184.0,
            192.0,
            202.0,
            493.0
        ],
        "resolution": [
            240.0,
            720.0,
            1080.0,
            1645.0
        ],
        "displaysize": [
            2.4000000953674316,
            6.21999979019165,
            6.440000057220459,
            6.519999980926514,
            6.650000095367432,
            8.0
        ],
        "battery": [
            1300.0,
            4000.0,
            4050.0,
            4500.0,
            5000.0,
            13201.0
        ],
        "price": [
            40.0,
            95.278,
            130.0,
            160.0,
            199.874,
            230.0,
            270.0,
            330.0,
            425.5000000000001,
            579.6000000000001,
            15001.0
        ],
        "popularity": [
            5160.0,
            63579.8,
            128130.20000000001,
            205095.99999999997,
            331792.8,
            490979.0,
            731826.6,
            1084198.4,
            1812992.4000000001,
            3118038.600000002,
            17963701.0
        ],
        'camera': [2.0, 13.0, 48.0, 50.0, 109.0],
        "year": [
            2019,
            2020,
            2021,
            2023
        ],
        "cpu": [
            2,
            4,
            6,
            9,
        ]
    }
    return phone_data_numerical_bin_edges_dict


def get_numerical_attribute_interval_label_phone(attribute, value):
    attribut_interval, interval_label = get_numerical_attribute_label_phone(attribute, intervalindex_true=True)
    # print(attribut_interval)
    intervals = pd.IntervalIndex.from_breaks(attribut_interval, closed='left')

    interval_find = list(intervals.contains(value))
    index = interval_find.index(True)
    value_interval_label = interval_label[index]
    # print(value_interval_label)
    return value_interval_label


def check_critique_satisfiability_numerical_attribute_phone(attribute, item_value, crit_direction, crit_value):
    satisfied_flag = False
    attribut_interval, interval_label = get_numerical_attribute_label_phone(attribute, intervalindex_true=True)
    intervals = pd.IntervalIndex.from_breaks(attribut_interval, closed='left')

    cur_interval_find = list(intervals.contains(crit_value))
    cur_index = cur_interval_find.index(True)

    item_interval_find = list(intervals.contains(item_value))
    item_index = item_interval_find.index(True)

    if item_index == cur_index and crit_direction == 'similar':
        satisfied_flag = True
    if item_index < cur_index and crit_direction == 'lower':
        satisfied_flag = True
    if item_index > cur_index and crit_direction == 'higher':
        satisfied_flag = True

    return satisfied_flag


def check_critique_satisfiability_numerical_datetime_phone(attribute, item_value, crit_direction, crit_value):
    satisfied_flag = False

    item_year = datetime.datetime.fromtimestamp(item_value).year
    crit_item_year = datetime.datetime.fromtimestamp(crit_value).year
    if item_year == crit_item_year and crit_direction == 'similar':
        satisfied_flag = True
    if item_year < crit_item_year and crit_direction == 'lower':
        satisfied_flag = True
    if item_year > crit_item_year and crit_direction == 'higher':
        satisfied_flag = True

    return satisfied_flag


def check_critique_satisfiability_numerical_discrete_phone(attribute, item_value, crit_direction, crit_value):
    satisfied_flag = False

    if item_value == crit_value and crit_direction == 'similar':
        satisfied_flag = True
    if item_value < crit_value and crit_direction == 'lower':
        satisfied_flag = True
    if item_value > crit_value and crit_direction == 'higher':
        satisfied_flag = True
    return satisfied_flag


def get_datetime_year_from_timestamp(timestamp):
    year = datetime.datetime.fromtimestamp(timestamp).year
    return year


def convert_to_critique_preference_dict(user_critique_preference):
    categorical_critique_dict = {}
    numerical_critique_dict = {}
    min_number = -1
    max_number = 999999

    for i in range(len(user_critique_preference)):
        each_crit = user_critique_preference[len(user_critique_preference) - i - 1]
        pos_or_neg = each_crit['pos_or_neg']
        attr = each_crit['attribute']
        crit_direction = each_crit['crit_direction']
        crit_value = ''

        # numerical attributes
        if 'value' in each_crit.keys():
            crit_value = each_crit['value']
            if attr not in numerical_critique_dict.keys():
                if pos_or_neg == 'pos':
                    if crit_direction == 'lower':
                        critique_preference_on_attribute = [min_number, crit_value]
                        numerical_critique_dict[attr] = critique_preference_on_attribute
                    elif crit_direction == 'higher':
                        critique_preference_on_attribute = [crit_value, max_number]
                        numerical_critique_dict[attr] = critique_preference_on_attribute
                    else:
                        print("Crit_direction - - ERROR -- " + crit_direction)
                        # input()
                if pos_or_neg == 'neg':
                    if crit_direction == 'lower':
                        critique_preference_on_attribute = [crit_value, max_number]
                        numerical_critique_dict[attr] = critique_preference_on_attribute
                    elif crit_direction == 'higher':
                        critique_preference_on_attribute = [min_number, crit_value]
                        numerical_critique_dict[attr] = critique_preference_on_attribute
                    else:
                        print("Crit_direction - - ERROR -- " + crit_direction)
                        # input()
            else:
                critique_preference_on_attribute = numerical_critique_dict[attr]
                if pos_or_neg == 'pos':
                    if crit_direction == 'lower':
                        if crit_value > critique_preference_on_attribute[0] and crit_value < \
                                critique_preference_on_attribute[1]:
                            critique_preference_on_attribute[1] = crit_value
                            numerical_critique_dict[attr] = critique_preference_on_attribute
                    elif crit_direction == 'higher':
                        if crit_value > critique_preference_on_attribute[0] and crit_value < \
                                critique_preference_on_attribute[1]:
                            critique_preference_on_attribute[0] = crit_value
                            numerical_critique_dict[attr] = critique_preference_on_attribute
                    else:
                        print("Crit_direction - - ERROR -- " + crit_direction)
                        # input()
                if pos_or_neg == 'neg':
                    if crit_direction == 'lower':
                        if crit_value > critique_preference_on_attribute[0] and crit_value < \
                                critique_preference_on_attribute[1]:
                            critique_preference_on_attribute[0] = crit_value
                            numerical_critique_dict[attr] = critique_preference_on_attribute
                    elif crit_direction == 'higher':
                        if crit_value > critique_preference_on_attribute[0] and crit_value < \
                                critique_preference_on_attribute[1]:
                            critique_preference_on_attribute[1] = crit_value
                            numerical_critique_dict[attr] = critique_preference_on_attribute
                    else:
                        print("Crit_direction - - ERROR -- " + crit_direction)
                        # input()


        # categorical attributes
        else:
            if attr not in categorical_critique_dict.keys():
                categorical_critique_dict[attr] = {'pos': [], 'neg': []}
                if pos_or_neg == 'pos':
                    categorical_critique_dict[attr]['pos'] = [crit_direction]
                if pos_or_neg == 'neg':
                    categorical_critique_dict[attr]['neg'] = [crit_direction]

            else:
                critique_preference_on_attribute = categorical_critique_dict[attr]

                if pos_or_neg == 'pos':
                    if crit_direction not in critique_preference_on_attribute['neg']:
                        crit_direction_list = critique_preference_on_attribute[pos_or_neg]
                        crit_direction_list.append(crit_direction)
                        critique_preference_on_attribute[pos_or_neg] = list(set(crit_direction_list))
                    else:  # use recent critique if there is inconsistency
                        continue
                if pos_or_neg == 'neg':
                    if crit_direction not in critique_preference_on_attribute['pos']:
                        crit_direction_list = critique_preference_on_attribute[pos_or_neg]
                        crit_direction_list.append(crit_direction)
                        critique_preference_on_attribute[pos_or_neg] = list(set(crit_direction_list))
                categorical_critique_dict[attr] = critique_preference_on_attribute

    return categorical_critique_dict, numerical_critique_dict


def sort_dict(value_dict):
    sorted_list = sorted(value_dict.items(), key=operator.itemgetter(1), reverse=True)

    return sorted_list


def convert_list_of_dict_to_dict(list_of_dict, key_name):
    converted_dict = {}
    for i_dict in list_of_dict:
        key = i_dict[key_name]
        converted_dict[key] = i_dict

    return converted_dict
