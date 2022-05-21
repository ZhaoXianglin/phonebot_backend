import pandas as pd
import numpy as np
import pprint
import copy
from utils.function import helper, recommendation, diversity_calculation
from efficient_apriori import apriori
import sys
# from analysis.data_processing_analysis import pca_analysis
sys.path.append("..") 
from utils.function.tool import time_helper, store_data

pp = pprint.PrettyPrinter(indent=4)


def determine_trigger_sc_or_not(interaction_log, cur_rec, categorical_attributes, numerical_attributes):

    results_trigger_sc = False
    # Constratints
    num_recommendation_cycle_constraints = 3

    # Conditions
    num_disliked_songs_condition = 3 # If the user clicks the “Next” button for n consecutive times.
    num_listened_songs_condition = 4 # If the number of listened songs (from last SC) (== num_recommendation_cycle) >= n
    # num_liked_songs_condition = 3 # If the total number of liked songs in the current genre >= n

    cur_rec_genre = cur_rec['genre']
    if 'latest_dialog' in interaction_log.keys():
        previous_dialogue = interaction_log['dialog'] + interaction_log['latest_dialog']
    else:
        previous_dialogue = interaction_log['dialog'] 
    # print(previous_dialogue)

    # Constraints
    recommendation_cycle_condition = False
    
    # Hard Constraint:  system suggest critique do not occur within 2 turns 
    # step1 : find the postion of latest system suggested critiques
    number_utterance = 0
    pos_sys_crit = 0
    for utterance_info in previous_dialogue:
        action = utterance_info['action'].lower()
        if action == "system_suggest" or action == "user_critique" :
            if 'critique' in utterance_info.keys():
                pos_sys_crit = number_utterance
        number_utterance += 1
   
    # print('pos_sys_crit: ', pos_sys_crit)
    # step2 : calculate the number of recommendation cycles start from the latest system-suggested critiques to the current turns
    num_recommendation_cycle = 0
    for utterance_info in previous_dialogue[pos_sys_crit:]:
        if utterance_info['action'].lower() == 'recommend':
            num_recommendation_cycle += 1 

    if num_recommendation_cycle >= num_recommendation_cycle_constraints:
        recommendation_cycle_condition = True

    # Hard constraint is satisfied: -> satisfiy any of following condition - related to 
    # (1) Listened History 
    # If the user clicks the “Next” button for n consecutive times.
    # If the total number of liked songs in the current genre > n

    if recommendation_cycle_condition:
        num_satisfied_listend_songs = 0
        num_satisfied_liked_songs = 0
        # num_satisfied_disliked_songs = 0
        num_consectively_disliked_songs = 0

        for utterance_info in previous_dialogue[pos_sys_crit:]:
            if utterance_info['agent']=='you':
                if utterance_info['action'].lower() == 'next' or 'next' in utterance_info['text'].lower():
                    num_consectively_disliked_songs += 1
                if utterance_info['action'].lower() == 'accept_song':
                    num_consectively_disliked_songs = 0 
        # print("cur_rec_genre:", cur_rec_genre) 

        liked_songs_id_list = []
        for each in interaction_log['likedSongs']:
            liked_songs_id_list.append(each['id'])

        for song_info in interaction_log['listenedSongs']:
            # print(song_info['genre'])
            if song_info['genre'] == cur_rec_genre:
                num_satisfied_listend_songs += 1
                if song_info['id'] in liked_songs_id_list:
                    num_satisfied_liked_songs += 1

        print("num_consectively_disliked_songs:", num_consectively_disliked_songs)
        print("num_satisfied_listend_songs:", num_satisfied_listend_songs)
        print("num_satisfied_liked_songs:", num_satisfied_liked_songs)
        # if num_satisfied_liked_songs >= num_liked_songs_condition :
        #     time_helper.print_current_time()
        #     print("num_satisfied_liked_songs: %d." % num_satisfied_liked_songs)
        #     results_trigger_sc = True
        if num_recommendation_cycle >= num_listened_songs_condition:
            time_helper.print_current_time()
            print("num_recommendation_cycle: %d." % num_recommendation_cycle)
            results_trigger_sc = True

        elif num_consectively_disliked_songs >= num_disliked_songs_condition :
            time_helper.print_current_time()
            print("num_consectively_disliked_songs: %d." % num_consectively_disliked_songs)
            results_trigger_sc = True

        else:
            results_trigger_sc = False

    else: 
        results_trigger_sc = False
    

    return results_trigger_sc


