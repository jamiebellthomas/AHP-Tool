import numpy as np
import pandas as pd
class AHPTier():
    def __init__(self,importance_matrix:np.array,criteria:list,):
        self.importance_matrix = np.array(importance_matrix,dtype=float)
        self.criteria = criteria
    def weighting_calculator(self):
        """
        Calculates the weightings of the criteria in the tier
        Returns:
            criteria_weightings (np.array): The weightings of the criteria in the tier
        """
        
        # Round all values to 4 decimal places
        for i in range(len(self.importance_matrix)):
            for j in range(len(self.importance_matrix)):
                self.importance_matrix[i,j] = round(self.importance_matrix[i,j],4)
        # Find all real eigenvalues and eigenvectors
        self.eigenvalues, self.eigenvectors = np.linalg.eig(self.importance_matrix)
        # Find the index of the largest eigenvalue
        self.max_index = np.argmax(self.eigenvalues)
        # Find the largest eigenvalue
        self.max_eigenvalue = self.eigenvalues[self.max_index]
        # Find the corresponding eigenvector
        self.max_eigenvector = self.eigenvectors[:,self.max_index]
        # Normalize the eigenvector
        self.max_eigenvector = self.max_eigenvector / np.sum(self.max_eigenvector)
        self.criteria_weightings = self.max_eigenvector
        # Round all values to 4 decimal places and remove and imaginary components
        for i in range(len(self.criteria_weightings)):
            self.criteria_weightings[i] = self.criteria_weightings[i].real
            self.criteria_weightings[i] = round(self.criteria_weightings[i],4)
        return self.criteria_weightings
    def consistency_checker(self):
        """
        Checks the consistency of the importance matrix
        Returns:
            consistent (bool): True if the importance matrix is consistent
        """
        # Calculate the consistency index
        self.CI = (self.max_eigenvalue - len(self.importance_matrix)) / (len(self.importance_matrix) - 1)
        # Calculate the consistency ratio
        # Random index values for 2-12 criteria
        self.random_index = {1:0,2:0,3:0.58,4:0.9,5:1.12,6:1.24,7:1.32,8:1.41,9:1.45,10:1.49,11:1.51,12:1.48}
        # Initialise consistency ratio
        self.CR = 0
        # If there are more than 2 criteria, calculate the consistency ratio
        # Otherwise, DivideByZeroError is raised
        if len(self.importance_matrix) > 2:
            self.CR = self.CI / self.random_index[len(self.importance_matrix)]
        # If the consistency ratio is less than 0.1, the importance matrix is consistent
        self.consistent = False
        if self.CR < 0.1:
            self.consistent = True
        return self.consistent
    def weightings_dictionary(self):
        """
        Creates a dictionary of the criteria and their weightings
        Returns:
            weightings (dict): A dictionary of the criteria and their weightings
        """
        # Initialise dictionary
        self.weightings = {}
        # Add criteria and weightings to dictionary
        for i in range(len(self.criteria)):
            self.weightings[self.criteria[i]] = self.criteria_weightings[i]
        return self.weightings
    

def generate_criteria_tier(data:pd.DataFrame):
    """
    Creates an AHPTier object for the parent criteria
    Args:
        data (pd.DataFrame): The hierarchy data
    Returns:
        AHPTier: An AHPTier object for the parent criteria
    """
    #Read in hierarchy
    hierarchy = data
    # Read in criteria row
    criteria_row = list(hierarchy.iloc[1])
    # Remove NaNs so only criteria remain
    hierarchy_criteria = [x for x in criteria_row if str(x) != 'nan']
    # Index of hierarchy criteria
    hierarchy_criteria_index = [i for i, x in enumerate(criteria_row) if str(x) != 'nan']
    # Table of hierarchy criteria
    hierarchy_criteria_table = hierarchy.iloc[2:2+len(hierarchy_criteria),hierarchy_criteria_index]
    # Convert dataframe to numpy array
    hierarchy_criteria_table = hierarchy_criteria_table.to_numpy()
    # Create AHPTier object
    return AHPTier(hierarchy_criteria_table,hierarchy_criteria)


def generate_sub_criteria_tier(data:pd.DataFrame,sub_criteria_number:int):
    """
    Creates an AHPTier object for a sub criteria tier and returns its parent
    Args:
        data (pd.DataFrame): The hierarchy data
        sub_criteria_number (int): The number of the sub criteria tier
    Returns:
        AHPTier: An AHPTier object for the sub criteria tier
        str: The parent of the sub criteria tier
    """
    #Read in hierarchy
    hierarchy = data
    # Read in sub criteria row
    sub_criteria_row = list(hierarchy.iloc[13+(21*(sub_criteria_number-1))])
    # Remove NaNs so only sub criteria remain
    sub_criteria = [x for x in sub_criteria_row if str(x) != 'nan']
    # Index of sub criteria
    sub_criteria_index = [i for i, x in enumerate(sub_criteria_row) if str(x) != 'nan']
    # Table of sub criteria
    # 14 is the row number of the first sub criteria
    # 21 is the number of rows between each sub criteria
    # 21*(sub_criteria_number-1) is the number of rows to skip to get to the sub criteria
    sub_criteria_table = hierarchy.iloc[14+(21*(sub_criteria_number-1)):14+(21*(sub_criteria_number-1))+len(sub_criteria),sub_criteria_index]
    # Convert dataframe to numpy array
    sub_criteria_table = sub_criteria_table.to_numpy()
    # Define parent
    parent_row = list(hierarchy.iloc[12+(21*(sub_criteria_number-1))])
    parent = [x for x in parent_row if str(x) != 'nan']
    parent = parent[-1]

    return AHPTier(sub_criteria_table,sub_criteria),parent
        
