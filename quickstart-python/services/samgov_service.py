import requests

def get_opportunities(api_key, solicitation_number, posted_from, posted_to, limit=1):
    base_url = "https://api.sam.gov/opportunities/v2/search"
    headers = {'Content-Type': 'application/json'}
    params = {
        'api_key': api_key,
        'postedFrom': posted_from,
        'postedTo': posted_to,
        'limit': limit,
        'solnum': solicitation_number
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None