import requests
import json
SAM_GOV_API_KEY='2er2s8iV1ePixShEdMX6Z3qOQKgFXC1swOymRuRG'

def get_opportunities(api_key, posted_from, posted_to, limit=10, offset=0):
    base_url = "https://api.sam.gov/opportunities/v2/search"
    headers = {'Content-Type': 'application/json'}
    params = {
        'api_key': api_key,
        'postedFrom': posted_from,
        'postedTo': posted_to,
        'limit': limit,
        'offset': offset,
        'ptype': 'o',  # solicitation
        'solnum': 'BAA-0002-19'
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

#formatted print output to console
def print_opportunities(opportunities):
    for item in opportunities['opportunitiesData']:
        print("Opportunity Title:", item['title'])
        print("Solicitation Number:", item['solicitationNumber'])
        print("Department:", item.get('department', 'N/A'))
        print("Posted Date:", item['postedDate'])
        print("Type of Opportunity:", item['type'])
        print("Response Deadline:", item.get('responseDeadLine', 'N/A'))
        print("Link to Opportunity:", item['uiLink'])
        print("---------------------------------------------------")

def main():
    api_key = SAM_GOV_API_KEY
    posted_from = "01/01/2024"
    posted_to = "4/01/2024"
    limit = 10
    offset = 0
    
    data = get_opportunities(api_key, posted_from, posted_to, limit, offset)
    if data:
        print_opportunities(data)
        while data['links'][-1].get('rel') == 'next':
            offset += limit
            data = get_opportunities(api_key, posted_from, posted_to, limit, offset)
            if data:
                print_opportunities(data)

if __name__ == "__main__":
    main()