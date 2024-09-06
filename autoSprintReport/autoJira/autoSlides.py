from __future__ import print_function
import csv
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import pandas as pd
import datetime

# Setup the Slides and Drive API
SCOPES = (
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/presentations'
)
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
HTTP = creds.authorize(Http())
DRIVE = build('drive', 'v3', http=HTTP)
SLIDES = build('slides', 'v1', http=HTTP)


# Function to parse dates
def parse_date_from_filename(name):
    try:
        return datetime.datetime.strptime(name.split()[-1], "%m-%d-%y")
    except ValueError:
        return None

# Search for the presentation with the closest date in the past
rsp = DRIVE.files().list(
    q="mimeType='application/vnd.google-apps.presentation' and name contains 'Sprint Closing Report'",
    fields="files(id, name)"
).execute()['files']

# Find the file with the closest date in the past or today
closest_file = None
closest_date = None
today = datetime.datetime(2024,8,28)

for file in rsp:
    file_date = parse_date_from_filename(file['name'])
    if file_date and (file_date <= today) and (closest_date is None or file_date >= closest_date):
        closest_date = file_date
        closest_file = file

def read_sprint_health_csv(file_path):
    data = {}
    with open(file_path, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            key = row[0].strip()
            value = row[1].strip()
            data[key] = value
    return data

def find_slide_with_text(presentation_id, search_text):
    presentation = SLIDES.presentations().get(presentationId=presentation_id).execute()
    
    for i, slide in enumerate(presentation.get('slides', [])):
        for element in slide.get('pageElements', []):
            shape = element.get('shape', {})
            text_elements = shape.get('text', {}).get('textElements', [])
            
            for text_element in text_elements:
                text_run = text_element.get('textRun', {})
                if text_run and search_text in text_run.get('content', ''):
                    return i  # Return the index of the slide containing the text
    
    return None  # Return None if the text is not found in any slide


if closest_file:
    presentation_id = closest_file['id']
    print(f"** Found presentation: {closest_file['name']} **")
    # Confirm that we want to use this presentation
    confirm = input("Do you want to use this presentation? (y/n): ")
    if confirm.lower() != 'y':
        print("Exiting...")
        exit()

    # Ask the user to see if there were any misses in this sprint
    misses = input("Were there any misses this sprint? [text]: ")
    # Ask the user to see if there were any challenges this sprint
    challenges = input("Were there any challenges this sprint? [text]: ")
    # Find slide with text "Selene"
    search_text = "Selene"
    slide_index = find_slide_with_text(presentation_id, search_text)
    if slide_index is not None:
        print(f"**Found the target slide at index: {slide_index}**")
        # Now you can use this slide_index in your subsequent operations
        slide_id = SLIDES.presentations().get(presentationId=presentation_id).execute()['slides'][slide_index]['objectId']
        
    else:
        print("**Could not find a slide containing the specified text.**")

    slide = SLIDES.presentations().get(presentationId=presentation_id).execute()
    slide_id = slide['slides'][slide_index]['objectId']

    # Replace text
    print("** Parsing the data...**")
    # Define path to CSV (replace with actual path)
    csv_path = "SprintHealth.csv"
    # Read values from CSV
    data = {}
    with open('SprintHealth.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                key, value = row
                data[key.strip()] = value.strip()

    # Extract required values from the dictionary
    sprint_goal = data.get("Sprint Goal:", "N/A")
    # Parse sprint_goal text where `-` is replaced as `\n`
    sprint_goal = sprint_goal.replace("-", "\n")
    total_estimated_story_points = data.get("Total Estimated Story Points:", "N/A")
    completed_story_points = data.get("Completed Story Points (Done + Won't Do):", "N/A")
    completion_rate = data.get("Completion Rate:", "N/A")
    total_defects = data.get("Total Defects:", "N/A")
    defect_rate = data.get("Defect Rate:", "N/A")
    support_percentage = data.get("Support Percentage:", "N/A")

    # Ask user to see if they want to replace the text
    print(f"Sprint Goal: {sprint_goal}")
    print(f"Completion Rate: {completion_rate}")
    print(f"Defect Rate: {defect_rate}")
    print(f"Support Percentage: {support_percentage}")
    print(f"Challenges: {challenges}") 
    print(f"Misses: {misses}")
    confirm = input("Do you want to replace the text in the presentation? (y/n): ")
    if confirm.lower() != 'y':
        print("Exiting...")
        exit()

    reqs = [
    {'replaceAllText': { 'containsText': {'text': '{{sprint_goal}}'}, 'replaceText': sprint_goal }},
    {'replaceAllText': { 'containsText': {'text': '{{completion_rate}}'}, 'replaceText': f"{completion_rate}%" }},
    {'replaceAllText': { 'containsText': {'text': '{{defect_rate}}'}, 'replaceText': f"{defect_rate}" }},
    {'replaceAllText': { 'containsText': {'text': '{{support_percentage}}'}, 'replaceText': f"{support_percentage}%" }},
    {'replaceAllText': { 'containsText': {'text': '{{challenges}}'}, 'replaceText': challenges if challenges else "N/A" }},
    {'replaceAllText': { 'containsText': {'text': '{{misses}}'}, 'replaceText': misses if misses else "N/A" }}
    ]

    SLIDES.presentations().batchUpdate(body={'requests': reqs}, presentationId=presentation_id).execute()
    print('** Done! **')
else:
    print("** No matching presentation found **")
