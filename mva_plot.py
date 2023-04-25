# Read in the data
import pandas as pd
import pickle
import numpy as np
import sys
model_name = sys.argv[1]
offset = 0.1
# This needs to match the offset defined in mva.py when the data was generated
########################################################################################
data = pd.read_csv(f'Models/{model_name}/mva.csv')
# Plot a heat map where the axes are the two principal criteria. 
# the colour of the point shows what the best alternative is
import plotly.express as px
import plotly.graph_objects as go

with open(f"Models/{model_name}/{model_name}.pkl", 'rb') as f:
# Extract axes names and scales just as in mva.py
    criteria_dictionary, sub_criteria_dictionary = pickle.load(f)
# 2 largest weightings are the criteria to be varied
analysis_variable = sorted(criteria_dictionary, key=criteria_dictionary.get, reverse=True)[:2]
print(analysis_variable)
resolution = 50
start_value1 = criteria_dictionary[analysis_variable[0]]
start_value2 = criteria_dictionary[analysis_variable[1]]
print(start_value1)
print(start_value2)                       
# make a meshgrid from the start value to zero with resolution points
x = np.linspace(start_value1+offset, 0, resolution)
y = np.linspace(start_value2+offset, 0, resolution)
# z is the best alternative code
z = data['Best Alternative Code']
# make z into a list
z = z.tolist()
# make z into a square array with resolution rows and resolution columns
z = np.reshape(z, (resolution,resolution))
# make the plot
fig = px.imshow(np.real(z), x=np.real(y), y=np.real(x), labels=dict(x=analysis_variable[1], y=analysis_variable[0], color="Alternative Score"))
# add legend
fig.update_layout(legend = dict(font = dict(family = "Courier", size = 20, color = "black")))
# make axis labels bigger
fig.update_xaxes(tickfont=dict(size=20)) 
fig.update_yaxes(tickfont=dict(size=20))
# make axis titles bigger
fig.update_xaxes(title_font=dict(size=20))
fig.update_yaxes(title_font=dict(size=20))
# Add a point at the start value (the value of the criteria before the analysis analysis)
fig.add_trace(
    go.Scatter(
        x=[np.real(start_value2)],
        y=[np.real(start_value1)],
        mode="markers",
        marker=dict(color="red", size=20),
        name="Start Value",
    )
)
fig.show()