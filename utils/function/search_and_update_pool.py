import pandas as pd
import numpy as np
import pprint
import copy
from function import helper 
from tool import time_helper
from function import helper, recommendation 
pp = pprint.PrettyPrinter(indent=4)

def update_recommendation_pool(user_preference_model, user_critique_preference, new_item_pool, integrated_item_pool, max_item_pool_number, categorical_attributes, numerical_attributes, key, method, alpha):

    sorted_estimated_score_dict = recommendation.compute_recommendation_by_MAUT(user_preference_model, user_critique_preference, integrated_item_pool, len(integrated_item_pool), categorical_attributes, numerical_attributes, method, alpha)
    
    integrated_item_pool_dict = {}
    new_item_pool_dict = {}

    for item in integrated_item_pool:
        integrated_item_pool_dict[item[key]] = item
    for item in new_item_pool:
        new_item_pool_dict[item[key]] = item

    max_item_pool_list = []
    for rec in sorted_estimated_score_dict:
        max_item_pool_list.append(rec[0])

    new_sorted_max_item_pool_list = [] ## make sure new item in the top list
    item_not_in_new_item_pool_list = []
    for item_id in max_item_pool_list:
        if item_id in new_item_pool_dict:
            new_sorted_max_item_pool_list.append(new_item_pool_dict[item_id])
        else:
            item_not_in_new_item_pool_list.append(integrated_item_pool_dict[item_id])
    


    for item in item_not_in_new_item_pool_list:
        new_sorted_max_item_pool_list.append(item)
        if len(new_sorted_max_item_pool_list) == max_item_pool_number:
            break

    # print(len(new_sorted_max_item_pool_list))
    
    updated_item_pool = new_sorted_max_item_pool_list
    # updated_item_pool_id = []
    # for item_id in new_sorted_max_item_pool_list:
    #     updated_item_pool_id.append(item_id)
    #     updated_item_pool.append(integrated_item_pool_dict[item_id])

    # print(updated_item_pool)
   
    return copy.deepcopy(updated_item_pool)