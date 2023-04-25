from normalisation import norm_main
import pickle
import numpy as np
import pandas as pd
from score_calc import sub_criteria_weighted_scores, criteria_weighted_scores
import sys
model_name = sys.argv[1]
offset = 0.1 #How much higher the start value is than the current value in the hierarchy (sum of two analysis weights must be less than 1)
# This script generates a csv file with the best alternative score for each combination of the two criteria that are being varied
########################################################################################
df = norm_main(model_name)

# Next we're going to read in the hierarchy for the requested model

with open(f"Models/{model_name}/{model_name}.pkl", 'rb') as f:
    criteria_dictionary, sub_criteria_dictionary = pickle.load(f)
# Now we're going to make all values in the sub_criteria_dictionary real numbers
for key in sub_criteria_dictionary:
    for sub_key in sub_criteria_dictionary[key]:
        sub_criteria_dictionary[key][sub_key] = np.real(sub_criteria_dictionary[key][sub_key])
# And do the same for the criteria_dictionary
for key in criteria_dictionary:
    criteria_dictionary[key] = np.real(criteria_dictionary[key])
# 2 largest weightings are the criteria to be varied
analysis_variable = sorted(criteria_dictionary, key=criteria_dictionary.get, reverse=True)[:2]
offset = 0.1
start_value1 = criteria_dictionary[analysis_variable[0]]
start_value2 = criteria_dictionary[analysis_variable[1]]                               
resolution = 50
# Create a meshgrid from the start value to zero. Resolution is the number of points in the meshgrid
x = np.linspace(start_value1+offset, 0, resolution)
y = np.linspace(start_value2+offset, 0, resolution)
xx, yy = np.meshgrid(x, y, indexing='ij')
# xx and yy are the differnt values that can be taken by the two criteria in the variable space
# We want to make a loop that will try all these values and see how the alternative score changes
# The weightings still need to sum to 1, so we need to make sure that the other criteria are changed accordingly
# Extract names deom model column of df and make a dictionary with the names as keys and the values as an empty list
scores = {}
# Make a list of the model names from the Model column of the dataframe, this is so we can add the scores to the correct list
model_names = df['Model'].tolist()
for model in model_names:
    scores[model] = []
# Add the criteria to the scores dictionary
for criteria in criteria_dictionary:
    scores[criteria] = []
# Now we have a dictionary with the model names and the criteria as keys and empty lists as values
for i in range(len(xx)):
    for j in range(len(xx[i])):
        # Change the values of the criteria in the criteria_dictionary
        criteria_dictionary[analysis_variable[0]] = xx[i][j]
        criteria_dictionary[analysis_variable[1]] = yy[i][j]
        sum = xx[i][j] + yy[i][j]
        # Work out how many other criteria there are and how much they need to be changed by
        remaining_criteria = len(criteria_dictionary) - 2
        delta = ((start_value1+start_value2)-sum)/remaining_criteria
        for criteria in criteria_dictionary:
            if criteria not in analysis_variable:
                criteria_dictionary[criteria] += delta

        # Create an empty df to store the weighted scores
        # This is where the normalised data is read in and scores are calculated using the weights from the hierarchy in the .pkl file
        weighted_scores = pd.DataFrame(columns=list(sub_criteria_dictionary.keys()))
        # Now we have everything we need to calculate the weighted scores
        weighted_scores = sub_criteria_weighted_scores(df, sub_criteria_dictionary, weighted_scores)
        weighted_scores = criteria_weighted_scores(weighted_scores, sub_criteria_dictionary, criteria_dictionary)
        # The alternative score is last column in the dataframe, make it into a list
        alternative_score = weighted_scores.iloc[:,-1].tolist()
        # Add the first value to the first list, the second value to the second list and so on
        for index, model in enumerate(model_names):
            scores[model].append(alternative_score[index])

        # Add weighting of each criteria to its own list in the scores list
        for criteria in criteria_dictionary:
            scores[criteria].append(criteria_dictionary[criteria])
        
        # If any criteria weightings are less than 0, set hammerhead ev20, albatross 2.2 and XV-L to 0, reset the criteria weightings and skip this iteration
        # Its easier to let it calculate the scores and then check if weightings are less than 0 than to check if they are less than 0 before calculating the scores and then skip the iteration
        if any(criteria_dictionary[criteria] < 0 for criteria in criteria_dictionary):
            for model in model_names:
                scores[model][-1] = 0
        # Reset the criteria weightings to the start values so that the next iteration starts from the same place
        for criteria in criteria_dictionary:
                if criteria not in analysis_variable:
                    criteria_dictionary[criteria] -= delta
                    
# Now we have a list of lists, we want to make a dataframe from it
scores_df = pd.DataFrame(scores)
# Make a column that is the name of the alternative with the highest score out of the Albartross 2.2, Hammerhead ev20 and XV-L alternatives
scores_df['Best Alternative'] = scores_df[model_names].idxmax(axis=1)
# Make a column that is a code of the best alternative (1, 2 or 3) for use in the sensitivity analysis
model_codes = {}
for i, model in enumerate(model_names):
    model_codes[model] = i+1
scores_df['Best Alternative Code'] = scores_df[model_names].idxmax(axis=1).replace(model_codes)
# Make a column that is the score of the best alternative
scores_df['Best Alternative Score'] = scores_df[model_names].max(axis=1)
# If all three scores are zero, set the best alternative to 'None'
scores_df.loc[scores_df['Best Alternative Score'] == 0, 'Best Alternative'] = 'None'
# Also set the best alternative code to 'None'
scores_df.loc[scores_df['Best Alternative Score'] == 0, 'Best Alternative Code'] = 'None'


# Save the dataframe to a csv file
scores_df.to_csv(f'Models/{model_name}/mva.csv', index=False)

# print counts of the best alternative
print('Counts of the best alternative')
print(scores_df['Best Alternative'].value_counts())
print(f'Data exported to: Models/{model_name}/mva.csv')
print(f'Run mva_plot.py {model_name} to plot the results')
print(f'Colour codes: {model_codes}')


