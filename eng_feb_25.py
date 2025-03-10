# =================================== IMPORTS ================================= #
import csv, sqlite3
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 
import plotly.figure_factory as ff
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from folium.plugins import MousePosition
import plotly.express as px
import datetime
import folium
import os
import sys
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.development.base_component import Component
# 'data/~$bmhc_data_2024_cleaned.xlsx'
# print('System Version:', sys.version)
# -------------------------------------- DATA ------------------------------------------- #

current_dir = os.getcwd()
current_file = os.path.basename(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = 'data/Engagement_Responses.xlsx'
file_path = os.path.join(script_dir, data_path)
data = pd.read_excel(file_path)
df = data.copy()

# Trim leading and trailing whitespaces from column names
df.columns = df.columns.str.strip()

# Trim whitespace from values in all columns
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Define a discrete color sequence
# color_sequence = px.colors.qualitative.Plotly

# Filtered df where 'Date of Activity:' is in December
df['Date of Activity'] = pd.to_datetime(df['Date of Activity'], errors='coerce')
df = df[df['Date of Activity'].dt.month == 2]

# Index using iloc
# print(df.iloc[:10, [1, 2]])

# print(df.head(10))
# print('Total Marketing Events: ', len(df))
# print('Column Names: \n', df.columns)
# print('DF Shape:', df.shape)
# print('Dtypes: \n', df.dtypes)
# print('Info:', df.info())
# print("Amount of duplicate rows:", df.duplicated().sum())

# print('Current Directory:', current_dir)
# print('Script Directory:', script_dir)
# print('Path to data:',file_path)

# ================================= Columns ================================= #

# Column Names: 

        # 'Timestamp', 
        # 'Date of Activity', 
        # 'Person submitting this form:',
        # 'Activity Duration (minutes):',
        # 'Care Network Activity:',
        # 'Entity name:', 
        # 'Brief Description:', 
        # 'Activity Status:',
        # 'BMHC Administrative Activity:', 
        # 'Total travel time (minutes):',
        # 'Community Outreach Activity:',
        # 'Number engaged at Community Outreach Activity:'

# =============================== Missing Values ============================ #

# missing = df.isnull().sum()
# print('Columns with missing values before fillna: \n', missing[missing > 0])

# ============================== Data Preprocessing ========================== #

# Check for duplicate columns
# duplicate_columns = df.columns[df.columns.duplicated()].tolist()
# print(f"Duplicate columns found: {duplicate_columns}")
# if duplicate_columns:
#     print(f"Duplicate columns found: {duplicate_columns}")



# ========================= Total Engagements ========================== #

# Total number of engagements:
total_engagements = len(df)
print('Total Engagements:', total_engagements)

# -------------------------- Engagement Hours -------------------------- #

# Sum of 'Activity Duration (minutes):' dataframe converted to hours:

# Convert 'Activity Duration (minutes):' to numeric
df['Activity Duration (minutes):'] = pd.to_numeric(df['Activity Duration (minutes):'], errors='coerce')
engagement_hours = df['Activity Duration (minutes):'].sum()/60
engagement_hours = round(engagement_hours)

# -------------------------- Total Travel Time ------------------------ #

# Clean the 'Total travel time (minutes):' column
df['Total travel time (minutes):'] = df['Total travel time (minutes):'].replace('Sustainable Food Center + APH Health Education Strategy Meeting & Planning Activities', np.nan)
df['Total travel time (minutes):'] = pd.to_numeric(df['Total travel time (minutes):'], errors='coerce') 
df['Total travel time (minutes):'] = df['Total travel time (minutes):'].fillna(0)  # Fill NaN with 0

# Sum 'Total travel time (minutes):' dataframe
total_travel_time = df['Total travel time (minutes):'].sum()/60
total_travel_time = round(total_travel_time)
# print(total_travel_time)

# travel time value counts
# print(df['Total travel time (minutes):'].value_counts())

# ---------------------------- Activity Status ----------------------- #

# Group by 'Activity Status:' dataframe
activity_status_group = df.groupby('Activity Status:').size().reset_index(name='Count')

# Support Pie Chart
status_pie = px.pie(
    activity_status_group,
    names='Activity Status:',
    values='Count',
).update_layout(
    title='Activity Status Pie Chart',
    height=450,
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=0,
    textinfo='value+percent',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ----------------------------- Admin Activity --------------------------- #

categories = [
    "(4) Outreach 1 to 1 Strategy Meetings",
    "BMHC Quarterly Team Meeting",
    "BMHC Team",
    "Community First Village Huddle",
    "Key Leaders Huddle",
    "National Kidney Foundation Strategy Meeting (Know Your Numbers Campaign Program)",
    "Outreach Team Meeting",
    "St. David's + Kazi 88.7FM Strategic Partnership Meeting & Strategy Planning Discussion/Activities",
    "Travis County Judge Andy Brown & Travis County Commissioner Ann Howard BMHC Tour & Discussion",
    "Record Keeping & Documentation",
    "HR Support",
    "Office Management",
    "2025 Calendar Year Outreach Preparation & Strategic Planning Activities",
    "Gudlife 2025 Strategic Planning Session",
    "Research & Planning",
    "Financial & Budgetary Management",
    "Compliance & Policy Enforcement",
    "IT",
    "Events Planning Meeting",
]

df['BMHC Administrative Activity:'] = (
    df['BMHC Administrative Activity:']
    .str.strip()
    .replace(
        {
            # Communication & Correspondence
            '(4) Outreach 1 to 1 Strategy Meetings': "Communication & Correspondence",
            'BMHC Quarterly Team Meeting': "Communication & Correspondence",
            'BMHC Team': "Communication & Correspondence",
            'Community First Village Huddle': "Communication & Correspondence",
            'Key Leaders Huddle': "Communication & Correspondence",
            'National Kidney Foundation Strategy Meeting (Know Your Numbers Campaign Program)': "Communication & Correspondence",
            'Outreach Team Meeting': "Communication & Correspondence",
            "St. David's + Kazi 88.7FM Strategic Partnership Meeting & Strategy Planning Discussion/Activities": "Communication & Correspondence",
            'Travis County Judge Andy Brown & Travis County Commissioner Ann Howard BMHC Tour & Discussion': "Communication & Correspondence",

            # Record Keeping & Documentation
            'Record Keeping & Documentation': "Record Keeping & Documentation",

            # HR Support
            'HR Support': "HR Support",
            'Office Management': "HR Support",

            # Research & Planning
            '2025 Calendar Year Outreach Preparation & Strategic Planning Activities': "Research & Planning",
            'Gudlife 2025 Strategic Planning Session': "Research & Planning",
            'Research & Planning': "Research & Planning",

            # Financial & Budgetary Management
            'Financial & Budgetary Management': "Financial & Budgetary Management",

            # Compliance & Policy Enforcement
            'Compliance & Policy Enforcement': "Compliance & Policy Enforcement",

            # IT
            'IT': "IT",

            # Everything else (fallback category)
            'Events Planning Meeting': "Research & Planning",
        }
    )
)

# Group by 'BMHC Administrative Activity:' dataframe:
admin_activity = df.groupby('BMHC Administrative Activity:').size().reset_index(name='Count')
# print("Admin Activities: \n", admin_activity.value_counts())
# print(admin_activity["BMHC Administrative Activity:"].unique())

admin_bar=px.bar(
    admin_activity,
    x="BMHC Administrative Activity:",
    y='Count',
    color="BMHC Administrative Activity:",
    text='Count',
).update_layout(
    height=850, 
    width=1900,
    title=dict(
        text='Admin Activity Bar Chart',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=-20,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Admin Activity",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels=False
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=True
        # visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b></b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Insurance Status Pie Chart
admin_pie=px.pie(
    admin_activity,
    names="BMHC Administrative Activity:",
    values='Count'
).update_layout(
    height=850,
    width=1700,
    # showlegend=False,
    showlegend=True,
    title='Admin Activity Pie Chart',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    textinfo='value+percent',
    # textinfo='none',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# -------------------------- Care Network Activity ----------------------- #

# Group by 'Care Network Activity:' dataframe:
care_network_activity = df.groupby('Care Network Activity:').size().reset_index(name='Count')

# print("Care Netowrk Activities: \n", care_network_activity.value_counts())

care_bar=px.bar(
    care_network_activity,
    x="Care Network Activity:",
    y='Count',
    color="Care Network Activity:",
    text='Count',
).update_layout(
    height=850, 
    width=1800,
    title=dict(
        text='Care Network Activity Bar Chart',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=-20,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Care Network Activity",
            font=dict(size=20),  # Font size for the title
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b></b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Insurance Status Pie Chart
care_pie=px.pie(
    care_network_activity,
    names="Care Network Activity:",
    values='Count'
).update_layout(
    height=850,
    width=1700,
    # showlegend=False,
    title='Care Network Activity Pie Chart',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    textinfo='value+percent',
    # textinfo='none',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# --------------------------Community Outreach Activity ---------------------- #

# Replace values in the original DataFrame before grouping
df['Community Outreach Activity:'] = df['Community Outreach Activity:'].replace({
    "Movement is medicine": "Movement is Medicine",
     "CTAAF Conference Presentation (advocacy of BMHC + AMEN movement is medicine )" : "CTAAF Conference Presentation"
})

# Group by 'Community Outreach Activity:' dataframe
community_outreach_activity = df.groupby('Community Outreach Activity:').size().reset_index(name='Count')

# print(community_outreach_activity.value_counts())

community_bar=px.bar(
    community_outreach_activity,
    x="Community Outreach Activity:",
    y='Count',
    color="Community Outreach Activity:",
    text='Count',
).update_layout(
    height=850, 
    width=1800,
    title=dict(
        text='Community Outreach Activity Bar Chart',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=-20,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Community Outreach Activity",
            font=dict(size=20),  # Font size for the title
        ),
        # showticklabels=False
        showticklabels=True 
    ),
    yaxis=dict(
        title=dict(
            text="Count",
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title="",
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=True
        visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textangle=0,
    textposition='auto',
    hovertemplate='<b></b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Insurance Status Pie Chart
community_pie=px.pie(
    community_outreach_activity,
    names="Community Outreach Activity:",
    values='Count'
).update_layout(
    height=850,
    width=1700,
    title='Community Outreach Activity Pie Chart',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    textinfo='value+percent',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ------------------------ Person Submitting Form -------------------- #

#  Duplicate values in 'Person submitting this form:' column:

# 0           Antonio Montggery       1
# 1           Antonio Montgomery      1
# 2              Cameron Morgan       1
# 3             Kiounis Williams      6
# 4            Kiounis Williams       3
# 5             Larry Wallace Jr     31

df['Person submitting this form:'] = (
    df['Person submitting this form:']
    .str.strip()
    .replace(
        {"Larry Wallace Jr": "Larry Wallace Jr.", 
        "Antonio Montggery": "Antonio Montgomery"}
    )
)

# df['Person submitting this form:'] = df['Person submitting this form:'].replace("Kiounis Williams ", "Kiounis Williams")

df_person = df.groupby('Person submitting this form:').size().reset_index(name='Count')
# print(person_group.value_counts())

person_bar=px.bar(
    df_person,
    x='Person submitting this form:',
    y='Count',
    color='Person submitting this form:',
    text='Count',
).update_layout(
    height=460, 
    width=780,
    title=dict(
        text='People Submitting Forms',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=-15,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Name",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels=False  # Hide x-tick labels
        # showticklabels=True  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        # title='Support',
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=False
        visible=True
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='outside',
    hovertemplate='<b>Name:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Person Pie Chart
person_pie=px.pie(
    df_person,
    names="Person submitting this form:",
    values='Count'  # Specify the values parameter
).update_layout(
    title='Ratio of People Filling Out Forms',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=0,
    textposition='auto',
    textinfo='value+percent',
    hovertemplate='<b>%{label} Status</b>: %{value}<extra></extra>',
)

# # ========================== DataFrame Table ========================== #

# Engagement Table
engagement_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df[col] for col in df.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

engagement_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=700,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# Group by 'Entity name:' dataframe
entity_name_group = df.groupby('Entity name:').size().reset_index(name='Count')

# Entity Name Table
entity_name_table = go.Figure(data=[go.Table(
    header=dict(
        values=list(entity_name_group.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,
        font=dict(size=12)
    ),
    cells=dict(
        values=[entity_name_group[col] for col in entity_name_group.columns],
        fill_color='lavender',
        align='left',
        height=25,
        font=dict(size=12)
    )
)])

entity_name_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),
    height=900,
    width=780,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# ============================== Dash Application ========================== #

import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    children=[ 
        html.Div(
            className='divv', 
            children=[ 
                html.H1('Partner Engagement Report', className='title'),
                html.H1('February 2025', className='title2'),
                html.Div(
                    className='btn-box', 
                    children=[
                        html.A(
                            'Repo',
                            href='https://github.com/CxLos/Eng_Feb_2025',
                            className='btn'
                        )
                    ]
                )
            ]
        ),
        
        # Data Table
        # html.Div(
        #     className='row0',
        #     children=[
        #         html.Div(
        #             className='table',
        #             children=[
        #                 html.H1(
        #                     className='table-title',
        #                     children='Engagement Data Table'
        #                 )
        #             ]
        #         ),
        #         html.Div(
        #             className='table2', 
        #             children=[
        #                 dcc.Graph(
        #                     className='data',
        #                     figure=engagement_table
        #                 )
        #             ]
        #         )
        #     ]
        # ),

        # Row 1: Engagements and Hours
        html.Div(
            className='row1',
            children=[
                html.Div(
                    className='graph11',
                    children=[
                        html.Div(className='high1', children=['Total Engagements:']),
                        html.Div(
                            className='circle1',
                            children=[
                                html.Div(
                                    className='hilite',
                                    children=[html.H1(className='high2', children=[total_engagements])]
                                )
                            ]
                        )
                    ]
                ),
                html.Div(
                    className='graph22',
                    children=[
                        html.Div(className='high3', children=['Engagement Hours:']),
                        html.Div(
                            className='circle2',
                            children=[
                                html.Div(
                                    className='hilite',
                                    children=[html.H1(className='high4', children=[engagement_hours])]
                                )
                            ]
                        ) 
                    ]
                )
            ]
        ),

        # Row 1: Engagements and Hours
        html.Div(
            className='row2',
            children=[
                html.Div(
                    className='graph11',
                    children=[
                        html.Div(className='high1', children=['Travel Hours']),
                        html.Div(
                            className='circle1',
                            children=[
                                html.Div(
                                    className='hilite',
                                    children=[html.H1(className='high2', children=[total_travel_time])]
                                )   
                            ]
                        )
                    ]
                ),
                html.Div(
                    className='graph2',
                    children=[
                        dcc.Graph(
                            figure=status_pie
                        )
                    ]
                )
            ]
        ),

        # html.Div(
        #     className='row3',
        #     children=[
        #         html.Div(
        #             className='graph1',
        #             children=[
        #                 dcc.Graph(
        #                     figure=admin_bar
        #                 )
        #             ]
        #         ),
        #         html.Div(
        #             className='graph2',
        #             children=[
        #                 dcc.Graph(
        #                     figure=admin_pie
        #                 )
        #             ]
        #         )
        #     ]
        # ),   
        
        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=admin_bar
                        )
                    ]
                ),
            ]
        ),   
        
        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=admin_pie
                        )
                    ]
                ),
            ]
        ),   

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=care_bar
                        )
                    ]
                ),
            ]
        ),   

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=care_pie
                        )
                    ]
                ),
            ]
        ),   

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=community_bar
                        )
                    ]
                ),
            ]
        ),   

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=community_pie
                        )
                    ]
                ),
            ]
        ),   

        # html.Div(
        #     className='row3',
        #     children=[
        #         html.Div(
        #             className='graph1',
        #             children=[
        #                 dcc.Graph(
        #                     figure=community_bar
        #                 )
        #             ]
        #         ),
        #         html.Div(
        #             className='graph2',
        #             children=[
        #                 dcc.Graph(
        #                     figure=community_pie
        #                 )
        #             ]
        #         )
        #     ]
        # ),   

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph1',
                    children=[
                        dcc.Graph(
                            figure=person_bar
                        )
                    ]
                ),
                html.Div(
                    className='graph2',
                    children=[
                        dcc.Graph(
                            figure=person_pie
                        )
                    ]
                )
            ]
        ),   
        
# ROW 2
# html.Div(
#     className='row2',
#     children=[
#         html.Div(
#             className='graph3',
#             children=[
#                 html.Div(
#                     className='table',
#                     children=[
#                         html.H1(
#                             className='table-title',
#                             children='Entity Name Table'
#                         )
#                     ]
#                 ),
#                 html.Div(
#                     className='table2', 
#                     children=[
#                         dcc.Graph(
#                             className='data',
#                             # figure=entity_name_table
#                         )
#                     ]
#                 )
#             ]
#         ),
#         html.Div(
#             className='graph4',
#             children=[                
#               html.Div(
#                     className='table',
#                     children=[
#                         html.H1(
#                             className='table-title',
#                             children=''
#                         )
#                     ]
#                 ),
#                 html.Div(
#                     className='table2', 
#                     children=[
#                         dcc.Graph(
                            
#                         )
#                     ]
#                 )
   
#             ]
#         )
#     ]
# ),

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=entity_name_table
                        )
                    ]
                ),
            ]
        ),   
])

print(f"Serving Flask app '{current_file}'! 🚀")

if __name__ == '__main__':
    app.run_server(debug=True)
                #    False)
# =================================== Updated Database ================================= #

# updated_path = 'data/bmhc_q4_2024_cleaned.xlsx'
# data_path = os.path.join(script_dir, updated_path)
# df.to_excel(data_path, index=False)
# print(f"DataFrame saved to {data_path}")

# updated_path1 = 'data/service_tracker_q4_2024_cleaned.csv'
# data_path1 = os.path.join(script_dir, updated_path1)
# df.to_csv(data_path1, index=False)
# print(f"DataFrame saved to {data_path1}")

# -------------------------------------------- KILL PORT ---------------------------------------------------

# netstat -ano | findstr :8050
# taskkill /PID 24772 /F
# npx kill-port 8050

# ---------------------------------------------- Host Application -------------------------------------------

# 1. pip freeze > requirements.txt
# 2. add this to procfile: 'web: gunicorn impact_11_2024:server'
# 3. heroku login
# 4. heroku create
# 5. git push heroku main

# Create venv 
# virtualenv venv 
# source venv/bin/activate # uses the virtualenv

# Update PIP Setup Tools:
# pip install --upgrade pip setuptools

# Install all dependencies in the requirements file:
# pip install -r requirements.txt

# Check dependency tree:
# pipdeptree
# pip show package-name

# Remove
# pypiwin32
# pywin32
# jupytercore

# ----------------------------------------------------

# Name must start with a letter, end with a letter or digit and can only contain lowercase letters, digits, and dashes.

# Heroku Setup:
# heroku login
# heroku create mc-impact-11-2024
# heroku git:remote -a mc-impact-11-2024
# git push heroku main

# Clear Heroku Cache:
# heroku plugins:install heroku-repo
# heroku repo:purge_cache -a mc-impact-11-2024

# Set buildpack for heroku
# heroku buildpacks:set heroku/python

# Heatmap Colorscale colors -----------------------------------------------------------------------------

#   ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
            #  'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
            #  'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
            #  'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
            #  'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
            #  'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
            #  'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
            #  'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
            #  'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
            #  'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
            #  'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
            #  'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
            #  'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
            #  'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
            #  'ylorrd'].

# rm -rf ~$bmhc_data_2024_cleaned.xlsx
# rm -rf ~$bmhc_data_2024.xlsx
# rm -rf ~$bmhc_q4_2024_cleaned2.xlsx