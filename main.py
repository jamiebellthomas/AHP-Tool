# This script aims to combine a few other scriptys
# First the data will be imported
# The data will then be checked for errors in the user's inputs
# The data will then be checked for consisteicy in the user's decision making
# The output will be a pkl model that can be called in other scripts
import numpy as np
import pickle
import pandas as pd
from inputChecker import *
from AHPTier import *
import sys
import os
import shutil
import csv

data = pd.read_excel('hierarchy.xlsx', sheet_name='Sheet1', header=0, index_col=0)
    
def main():
    sys.stdout = open("output.log", "w")
    parents,number = criteria_info(data)
    print("---------------------")
    print("Checking for a valid model name...")
    model_name_bool,model_name = model_name_check(data)
    if model_name_bool == True:
        print(model_name_bool)
    if model_name_bool == False:
        return False, model_name

    print("---------------------")
    print("Checking the uniqueness of parent criteria...")
    parent_criteria_unique = criteria_unique(parents)
    if parent_criteria_unique == True:
        print(parent_criteria_unique)
    if parent_criteria_unique == False:
        print("---------------------")
        return False, model_name

    print("---------------------")
    print("Checking that the parent criteria defined at the top of the input spreadsheet match the parent criteria defined in the subsequent tiers...")
    parents_matching = parent_match(data,parents ,number)
    if parents_matching == True:
        print(parents_matching)
    if parents_matching == False:
        print("---------------------")
        return False, model_name

    print("---------------------")
    print("Checking the uniqueness of sub-criteria...")
    sub_criteria_uniqueness = sub_criteria_unique(data,number)
    if sub_criteria_uniqueness == True:
        print(sub_criteria_uniqueness)
    if sub_criteria_uniqueness == False:
        print("---------------------")
        return False, model_name

    print("---------------------")
    print("Checking parent criteria have been added in a sequential manner (no gaps)...")
    sequential_criteria = criteria_sequentially(data)
    if sequential_criteria == True:
        print(sequential_criteria) 
    if sequential_criteria == False:
        print("---------------------")
        return False, model_name

    print("---------------------")
    print("Checking sub-criteria have been added in a sequential manner (no gaps)...")
    sequential_sub_criteria = sub_criteria_sequentially(data,number)
    if sequential_sub_criteria == True:
        print(sequential_sub_criteria)
    if sequential_sub_criteria == False:
        print("---------------------")
        return False, model_name

    print("---------------------")
    print("Checking that the pairwise comparison table for parent criteria is complete...")
    parent_table_check = criteria_importance_table_checker(data)
    if parent_table_check == True:
        print(parent_table_check)
    if parent_table_check == False:
        print("---------------------")
        return False, model_name

    print("---------------------")
    print("Checking that the pairwise comparison tables for sub-criteria are complete...")
    sub_criteria_table_check = sub_criteria_importance_table_checker(data,number)
    if sub_criteria_table_check == True:
        print(sub_criteria_table_check)
    if sub_criteria_table_check == False:
        print("---------------------")
        return False, model_name

    print("---------------------")
    print("USER INPUT CHECKS COMPLETE")

    # The next step is to check the consistency of the user's decision making

    # Now the each pairwise comparison table will be passed into an AHP object, the weightings will be calculated and the consistency will be checked
    # The weightings will then be added to a dictionary
    # The dictionary will then be added to a dictionary of dictionaries
    # Finally, the dictionary of dictionaries will then be saved as a pkl file

    # First let's create call AHPTier to create an AHP object for the parent criteria
    # The procedure for this was mocked up in hierarchyReader.py script
    print("---------------------")
    print("Now the consistency of the user's decision making will be checked")
    print("---------------------")
    

    parent_criteria_class = generate_criteria_tier(data)
    parent_criteria_class.weighting_calculator()
    if parent_criteria_class.consistency_checker() == False:
        print("Parent Criteria Consistency Check: Failed")
        print("Check the pairwise comparison table for parent criteria and ensure your decision making is consistent")
        print("---------------------")
        return False, model_name
    else:
        print("Parent Criteria Consistency Check: Passed")
        print("---------------------")
        print("Pairwise comparison table for parent criteria:")
        print(parent_criteria_class.importance_matrix)
        parent_criteria_weightings_dictionary = parent_criteria_class.weightings_dictionary()
    print("---------------------")

    # Now let's create call AHPTier to create an AHP object for the sub-criteria
    # First let's extract the sub-criteria pair wise tables from the input spreadsheet and save them in a dictionary where the key is the parent criteria
    # This will help us keep track of the hierarchy structure
    sub_criteria_dictionary = {}
    for i in range(1,len(parent_criteria_class.criteria)+1):
        # Now let's create a dictionary of dictionaries where the key is the parent criteria and the value is an instance of the AHPTier class
        sub_criteria_tier,parent = generate_sub_criteria_tier(data,i)
        sub_criteria_dictionary[parent] = [sub_criteria_tier]
        sub_criteria_dictionary[parent].append(sub_criteria_tier.weighting_calculator())
        sub_criteria_dictionary[parent].append(sub_criteria_tier.consistency_checker())
        # Iterate through the sub-criteria dictionary and call the weighting_calculator method on each instance of the AHPTier class
    con_check = True
    for key in sub_criteria_dictionary:
        if sub_criteria_dictionary[key][2] == True:
            print("Sub-criteria consistency check for parent criteria:", key, "- Passed")
            print("---------------------")
            print("Pairwise comparison table for sub-criteria for parent criteria:", key)
            print(sub_criteria_dictionary[key][0].importance_matrix)
            print("---------------------")
        if sub_criteria_dictionary[key][2] == False:
            print("Sub-criteria consistency check for parent criteria:",key, "Failed")
            print("Check the pairwise comparison table for sub-criteria and ensure your decision making is consistent")
            print("---------------------")
            con_check = False
    if con_check == False:
        print("Consistency check failed")
        return False, model_name
    sub_criteria_weightings_dictionary = {}
    for key in sub_criteria_dictionary:
        sub_criteria_weightings_dictionary[key] = sub_criteria_dictionary[key][0].weightings_dictionary()
    print("Parent criteria weightings dictionary:")
    print(parent_criteria_weightings_dictionary)
    print("---------------------")
    print("Sub-criteria weightings dictionary:")
    print(sub_criteria_weightings_dictionary)
    print("---------------------")
    # Now we need to create a CSV file that contains the titles for each attribute in the sub-criteria weightings dictionary
    # Users will then input the values for each attribute in the CSV file and the CSV file will be read in by another script

    # First let's create a list of the attributes in the sub-criteria weightings dictionary
    sub_criteria_weightings_dictionary_attributes = []
    for key in sub_criteria_weightings_dictionary:
        for attribute in sub_criteria_weightings_dictionary[key]:
            sub_criteria_weightings_dictionary_attributes.append(attribute)
    # Now let's remove any duplicates from the list
    sub_criteria_weightings_dictionary_attributes = list(dict.fromkeys(sub_criteria_weightings_dictionary_attributes))
    # Add 'Model' and 'Operator' to the start of the list
    sub_criteria_weightings_dictionary_attributes.insert(0,'Model')
    sub_criteria_weightings_dictionary_attributes.insert(0,'Operator')


    print("A CSV file containing the attribute names has been created in the Models folder")
    print("Please input the values for each attribute in the CSV file")
    print("---------------------")



    # Now let's save the parent criteria weightings dictionary and the sub-criteria weightings dictionary of dictionaries as a pkl file
    # The pkl file will be saved in the Models folder and will be named after the model name the user has specified

    print(f"Exporting model as a pkl file to {os.getcwd()}\Models\{model_name}")
    path = f'Models/{model_name}'
    if not os.path.exists(path):
        os.makedirs(path)
    # Now let's create a CSV file that contains the attribute names
    with open(f'Models/{model_name}/input.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(sub_criteria_weightings_dictionary_attributes)          
    with open(f'Models/{model_name}/{model_name}.pkl', 'wb') as f:
        pickle.dump((parent_criteria_weightings_dictionary, sub_criteria_weightings_dictionary), f)
    print("...")
    print("Export completed")
    print("---------------------")
    # close thte output log file
    sys.stdout.close()
    # Move the output log file to the Models folder
    shutil.move('output.log', f'Models\{model_name}\output.log')
    sys.stdout = sys.__stdout__
    return True, model_name
    
if __name__ == "__main__":
    result, model_name = main()

if result == False:
    # close thte output log file
    sys.stdout.close()
    # Move the output log file to the Models folder
    path = f'Models/{model_name}'
    if not os.path.exists(path):
        os.makedirs(path)
    shutil.move('output.log', f'Models/{model_name}/output.log')
    sys.stdout = sys.__stdout__
    print("---------------------")
    print("Model creation failed")
    print("Check the output log file for more information")
    print(f"Path: {os.getcwd()}\Models\{model_name}\output.log")
    print("---------------------")

if result == True:
    print("---------------------")
    print("Model creation successful")
    print(f"Path: {os.getcwd()}\Models\{model_name}")
    print("---------------------")
    
    

    





