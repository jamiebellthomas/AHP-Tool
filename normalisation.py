# This is where data from an input file is normalised
# How to use: python normalisation.py <input file> 
# Output: <input file>_normalised.csv
# How data is normalised depends on the type of data
# Summed up nicely in report but basically:
# 1. If data is categorical, it is converted to a numerical value between 0 and 1
# 2. If data is numerical, it is normalised to a range of 0 to 1
# 3. If the numerical data is beneficial, higher values are closer to 1
# 4. If the numerical data is detrimental, higher values are closer to 0

import sys
import csv
import numpy as np
import pandas as pd

# The input file is coming from a folder with the model name as the folder name
# Model name is the variable, input.csv is the file name and is the same for all models
# The output file is the same as the input file but with _normalised.csv at the end



# Normalise the data except for the first, second and last columns which are the operator ID, model name and the score respectively
def norm_main(model_name):
    input_file = f"Models/{model_name}/input.csv"
    # Read the input file into a pandas dataframe
    df = pd.read_csv(input_file)
    for column in df.columns[2:]:
        # remove all nan values
        df = df.dropna(subset=[column])
        df[column] = normalise(df[column])

    return df

def normalise(df_column):
    """
    Normalise beneficial data
    Input: pandas dataframe column
    Output: pandas dataframe column
    """
    # Define the beneficial and non-beneficial varaibles
    beneficial = ["Range","Endurance","Altitude","Payload","Cargo space", "MTOW", "Cruise speed", "Max speed", "Wind resistance"]
    non_beneficial = ["Length", "Width", "Height", "Wingspan", "Rotor diameter", "Fuel consumption"]
    non_numeric = ["Propulsion", "VTOL"]

    # Convert the column into a numpy array
    np_array = df_column.to_numpy()
    # Normalise the data
    # If the data is categorical, convert it to a numerical value
    if df_column.name in non_numeric:
        if df_column.name == "Propulsion":
            for i in range(len(np_array)):
                if np_array[i] == "Electric":
                    np_array[i] = 1
                elif np_array[i] == "Hybrid":
                    np_array[i] = 0.5
                else:
                    np_array[i] = 0
        elif df_column.name == "VTOL":
            for i in range(len(np_array)):
                if np_array[i] == "y":
                    np_array[i] = 1
                else:
                    np_array[i] = 0
        df_column = pd.Series(np_array)
        return df_column
    try:
        normalised = (np_array - np_array.min()) / (np_array.max() - np_array.min())
    except TypeError:
        # remove apostrophes from strings and convert to float
        for i in range(len(np_array)):
            np_array[i] = float(np_array[i].replace(",", ""))
        normalised = (np_array - np_array.min()) / (np_array.max() - np_array.min())
    if df_column.name in non_beneficial:
        normalised = 1 - normalised

    # Convert the numpy array back into a pandas dataframe column
    df_column = pd.Series(normalised)
    return df_column

if __name__ == "__main__":
    norm_main(sys.argv[1])



