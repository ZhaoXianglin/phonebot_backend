import pandas as pd
import numpy as np
import pprint
import copy
from utils.function import helper
from statistics import mean 
from scipy.stats import entropy

from sklearn.preprocessing import OneHotEncoder,MaxAbsScaler
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances

pp = pprint.PrettyPrinter(indent=4)

def calculate_dissimilarity_between_two_sets_of_vectors (user_listened_songs_vectors, crit_item_vectors):
    all_pairs_dissimilarity_list = cosine_distances(user_listened_songs_vectors, crit_item_vectors)
    mean_dissimilarity_between_two_sets = np.ravel(all_pairs_dissimilarity_list).mean()
    return mean_dissimilarity_between_two_sets


def calculate_dissimilarity_between_two_sets(user_listened_songs_info_df, crit_item_info_df,combined_songs_info_df, categorical_attributes, numerical_attributes):
    # Step 1: Preprocessing -> construct feature vectors
    user_listened_songs_vectors, crit_item_vectors = preprocessing_constrctur_feature_vectors(user_listened_songs_info_df, crit_item_info_df,combined_songs_info_df, categorical_attributes, numerical_attributes)

    # Step 2: Dissimilarity Calculation
    dissimilarity_between_two_sets = calculate_dissimilarity_between_two_sets_of_vectors (user_listened_songs_vectors, crit_item_vectors)

    return dissimilarity_between_two_sets

def entropy_for_one_attribute(attribute_df):
    attribute_value_prob = attribute_df.value_counts(normalize=True).to_dict()
    entropy_attribute_value = entropy(list(attribute_value_prob.values()))
    return entropy_attribute_value

def calculate_entropy_for_set(combined_songs_info_df, categorical_attributes, numerical_attributes):
    songs_info_df = copy.deepcopy(combined_songs_info_df)
    # Step 1: Preprocessing  -> discretization for numerical data
    for attribute in numerical_attributes:
        attribute_intervalindex, interval_label = helper.get_numerical_attribute_intervalindex(attribute)
        songs_info_df[attribute] = pd.cut(songs_info_df[attribute], attribute_intervalindex,right=False, labels = interval_label)

    # Step 2: Calculate the entropy
    entropy_dict = {}
    for attribute in categorical_attributes:
        entropy_dict[attribute] = entropy_for_one_attribute(songs_info_df[attribute])

    for attribute in numerical_attributes:
        entropy_dict[attribute] = entropy_for_one_attribute(songs_info_df[attribute])
    
    # pp.pprint(entropy_dict)
    entropy_set = sum(entropy_dict.values())

    return entropy_set
    
def calculate_unexpectedness_based_on_user_listened_songs(user_listened_songs_vectors, crit_item_vectors):

    all_pairs_dissimilarity_list = cosine_distances(crit_item_vectors, user_listened_songs_vectors)
    unexpectedness_hausdorff_distance_list = []
    for one_item_dissimilarity_list in all_pairs_dissimilarity_list:
        unexpectedness_hausdorff_distance_list.append(min(one_item_dissimilarity_list))
    
    set_unexpectedness_hausdorff_distance = mean(unexpectedness_hausdorff_distance_list)

    return set_unexpectedness_hausdorff_distance

def calculate_unexpectedness_for_set(user_listened_songs_info_df, crit_item_info_df,combined_songs_info_df, categorical_attributes, numerical_attributes):
    # Step 1: Preprocessing -> construct feature vectors
    user_listened_songs_vectors, crit_item_vectors = preprocessing_constrctur_feature_vectors(user_listened_songs_info_df, crit_item_info_df,combined_songs_info_df, categorical_attributes, numerical_attributes)
    
    # Step 2: Unexpectedness Calculation
    unexpectedness_for_set = calculate_unexpectedness_based_on_user_listened_songs (user_listened_songs_vectors, crit_item_vectors)

    return unexpectedness_for_set