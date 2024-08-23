import pandas as pd
import logging
import os
import json

# Function to deduplicate columns
def deduplicate_columns(columns):
    new_columns = []
    seen = {}
    for column in columns:
        if column not in seen:
            seen[column] = 1
            new_columns.append(column)
        else:
            seen[column] += 1
            new_columns.append(f"{column}_{seen[column]}")
    return new_columns

# Function to process the CSV and calculate story points and completion rate
def process_sprint_data(csv_file):
    df = pd.read_csv(csv_file)
    
    # Deduplicate column names
    df.columns = deduplicate_columns(df.columns)

    # Combine story points from multiple columns into a single column
    story_point_columns = [col for col in df.columns if 'Story point estimate' in col or 'Story points' in col or 'Strategic Pillars' in col]

    # Combine story points into a single column
    df['Story_Points'] = 0
    for col in story_point_columns:
        if col in df.columns:
            df['Story_Points'] += pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Ensure the necessary columns are present
    required_columns = ['Status', 'Issue Type']
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"CSV file must contain the following columns: {required_columns}")

    # Rename columns for easier access (optional, for convenience)
    df = df.rename(columns={'Issue Type': 'Issue_Type'})

    # Calculate the total estimated story points
    total_story_points = df['Story_Points'].sum()

    # Filter the dataframe for Done and Won't Do statuses
    completed_df = df[df['Status'].isin(['Done', "Won't Do"])]

    # Calculate the completed story points
    completed_story_points = completed_df['Story_Points'].sum()

    # Calculate the completion rate
    completion_rate = completed_story_points / total_story_points if total_story_points != 0 else 0

    # Group by status, type, and sum story points
    grouped = df.groupby(['Status', 'Issue_Type'])['Story_Points'].sum().reset_index()

    return grouped, total_story_points, completed_story_points, completion_rate

# Function to calculate defect rate from the second CSV
def calculate_defect_rate(csv_file):
    df = pd.read_csv(csv_file)

    # Deduplicate column names
    df.columns = deduplicate_columns(df.columns)

    # Calculate the total number of defects
    total_defects = len(df)
    
    # Calculate the defect rate
    defect_rate = total_defects / (total_developers * 2)  # As per the instruction to divide by 4

    return total_defects, defect_rate

def calculate_support_percentage(csv_file):
    df = pd.read_csv(csv_file)

    # Deduplicate column names
    df.columns = deduplicate_columns(df.columns)

    # Combine story points from multiple columns into a single column
    story_point_columns = [col for col in df.columns if 'Story point estimate' in col or 'Story points' in col or 'Strategic Pillars' in col]

    # Combine story points into a single column
    df['Story_Points'] = 0
    for col in story_point_columns:
        if col in df.columns:
            df['Story_Points'] += pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Filter the dataframe for Done and Won't Do statuses
    completed_df = df[df['Status'].isin(['Done', "Won't Do"])]

    # Calculate the completed story points
    completed_story_points = completed_df['Story_Points'].sum()

    # Calculate the support percentage
    support_percentage = completed_story_points / total_support_points if total_support_points != 0 else 0

    return support_percentage


# Load configuration
config_path = 'config.json'
if os.path.exists(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
        total_developers = config.get('total_developers')
        total_support_points = config.get('total_support_points')

# Process sprintgoal.txt
with open('sprintgoal.txt', 'r') as f:
    sprint_goal = f.read()

# Process the first CSV
grouped_data, total_story_points, completed_story_points, completion_rate = process_sprint_data('Jira.csv')

# Process the second CSV for defect rate
total_defects, defect_rate = calculate_defect_rate('Jira (1).csv')

# Process the third CSV for support percentage
support_percentage = calculate_support_percentage('Jira (2).csv')

# Display the grouped data and calculations
print(grouped_data)
print(f"Sprint Goal: {sprint_goal}")
print(f"Total Estimated Story Points: {total_story_points}")
print(f"Completed Story Points (Done + Won't Do): {completed_story_points}")
print(f"Completion Rate: {completion_rate:.2%}")
print(f"Total Defects: {total_defects}")
print(f"Defect Rate: {defect_rate:.2f}")
print(f"Support Percentage: {support_percentage:.2%}")

# Save the grouped data, completion rate, and defect rate to a new CSV file
grouped_data.to_csv('SprintHealth.csv', index=False)

# Append the completion rate and defect rate to the CSV
with open('SprintHealth.csv', 'a') as f:
    f.write(f"\nSprint Goal:,{sprint_goal}\n")
    f.write(f"\nTotal Estimated Story Points:,{total_story_points}\n")
    f.write(f"Completed Story Points (Done + Won't Do):,{completed_story_points}\n")
    f.write(f"Completion Rate:,{completion_rate*100:.0f}\n")
    f.write(f"Total Defects:,{total_defects}\n")
    f.write(f"Defect Rate:,{defect_rate:.2f}\n")
    f.write(f"Support Percentage:,{support_percentage*100:.2f}\n")

print("Parsed data, completion rate, and defect rate have been saved to SprintHealth.csv")
