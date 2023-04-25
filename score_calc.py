# This is where the normalised data is read in and scores are calculated using the weights from the hierarchy in the .pkl file
# Input is a model name, scores will be saved to a csv file called <model name>_scores.csv

from normalisation import norm_main
import pandas as pd
import numpy as np
import pickle
import os
import sys

# Try and open Models/{model_name}/input_normalised.csv, if FileNotFoundError, run normalisation.py with model_name as input


def read_in(model_name):
    df = norm_main(model_name)
    # Read in the hierarchy
    with open(f"Models/{model_name}/{model_name}.pkl", 'rb') as f:
        criteria_dictionary, sub_criteria_dictionary = pickle.load(f)
    # Make all values in the sub_criteria_dictionary real numbers
    for key in sub_criteria_dictionary:
        for sub_key in sub_criteria_dictionary[key]:
            sub_criteria_dictionary[key][sub_key] = np.real(sub_criteria_dictionary[key][sub_key])
    # Make all values in the criteria_dictionary real numbers
    for key in criteria_dictionary:
        criteria_dictionary[key] = np.real(criteria_dictionary[key])

    # Create an empty df to store the weighted scores
    weighted_scores = pd.DataFrame(columns=list(sub_criteria_dictionary.keys()))
    # Set the first two columns to the same as the input df
    weighted_scores['Operator'] = df['Operator']
    weighted_scores['Model'] = df['Model']
    return df, criteria_dictionary, sub_criteria_dictionary, weighted_scores

def sub_criteria_weighted_scores(normalised_df, sub_criteria_dictionary:dict, weighted_scores):
    # Iterate over all rows of data, calculate the weighted scores for each sub-criteria and add to weighted_scores df
    # The output should be the same format as the input, but with the weighted scores instead of the normalised scores
    for key in sub_criteria_dictionary:
        for sub_key in sub_criteria_dictionary[key]:
            # Convery all values in column into floats
            normalised_df[sub_key] = normalised_df[sub_key].astype(float)
            weighted_scores[sub_key] = np.real(normalised_df[sub_key] * sub_criteria_dictionary[key][sub_key])
    return weighted_scores

def criteria_weighted_scores(normalised_df, sub_criteria_dictionary:dict,criteria_dictionary:dict):
    # Iterate over all rows of data, calculate the weighted scores for each sub-criteria and add to weighted_scores df
    # The output should be the same format as the input, but with the weighted scores instead of the normalised scores
    for key in sub_criteria_dictionary:
        # If sub_criteria is in the dataframe, add it to the column called key
        for sub_key in sub_criteria_dictionary[key]:
            if sub_key not in normalised_df.columns:
                # remove sub_key from sub_criteria_dictionary
                sub_criteria_dictionary[key].pop(sub_key)
    # Now go through the sub_criteria_dictionary and add the scores for the sub criteria in the same criteria
    for key in sub_criteria_dictionary:
        normalised_df[key] = normalised_df[sub_criteria_dictionary[key].keys()].sum(axis=1)
    # Now multiply the weighted scores by the criteria weights
    for key in criteria_dictionary:
        normalised_df[key] = np.real(normalised_df[key] * criteria_dictionary[key])
    # Now add the criteria scores together to get the alternative score and add to the dataframe
    normalised_df['Alternative Score'] = normalised_df[criteria_dictionary.keys()].sum(axis=1)
    # Move Operator and Model to the first and second columns from their current positions
    cols = list(normalised_df.columns)
    
    
    return normalised_df

def main():
    model_name = sys.argv[1]
    data, criteria_dictionary, sub_criteria_dictionary, weighted_scores = read_in(model_name)
    print(data)
    weighted_scores = sub_criteria_weighted_scores(data, sub_criteria_dictionary, weighted_scores)
    weighted_scores = criteria_weighted_scores(weighted_scores, sub_criteria_dictionary, criteria_dictionary)
    print(weighted_scores)
    weighted_scores.to_csv(f"Models/{model_name}/{model_name}_scores.csv", index=False)
    return None

if __name__ == "__main__":
    main()
