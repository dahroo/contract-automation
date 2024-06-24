import requests
import json
from datetime import datetime

def create_monday_board(board_name, board_kind, api_key):
    url = "https://api.monday.com/v2/"
    headers = {"Authorization": api_key}
    query = '''
    mutation ($boardName: String!, $boardKind: BoardKind!) {
      create_board (board_name: $boardName, board_kind: $boardKind) {
        id
      }
    }
    '''
    variables = {
        "boardName": board_name,
        "boardKind": board_kind
    }
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to create board: " + response.text)
    

def create_monday_item(api_key, board_id, group_id, item_name, posted_date, sol_num, link_value, deadline, naics, position_relative_method=None, relative_to=None):
    url = "https://api.monday.com/v2/"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': api_key
    }
    link_column_value = {
        'url': link_value,  # Ensure this is just the URL string
        'text': 'Source Link'  # You can customize the link text
    }
    stage = {
        'index': '11'
    }

    # Format the column values as a JSON string
    column_values = json.dumps({
        'status': stage, #stage
        'date96': posted_date[:10],     #posted date
        'solicitation____1': sol_num,   #solicitation num
        'link__1': link_column_value,   # URL 
        'date': deadline[:10],  #due date
        'naics': naics
    })

    # GraphQL mutation query
    mutation = '''
    mutation ($boardId: ID!, $groupId: String!, $itemName: String!, $columnValues: JSON!, $positionRelativeMethod: PositionRelative, $relativeTo: ID) {
      create_item (board_id: $boardId, group_id: $groupId, item_name: $itemName, column_values: $columnValues, position_relative_method: $positionRelativeMethod, relative_to: $relativeTo) {
        id
      }
    }
    '''

    # Variables for the GraphQL mutation
    variables = {
        'boardId': board_id,
        'groupId': group_id,
        'itemName': item_name,
        'columnValues': column_values,
        'positionRelativeMethod': position_relative_method,
        'relativeTo': relative_to
    }

    # Make the POST request
    response = requests.post(url, json={'query': mutation, 'variables': variables}, headers=headers)
    try:
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()  # Return the parsed JSON response
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
