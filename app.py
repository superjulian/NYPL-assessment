from flask import Flask
from markupsafe import escape
import requests
from requests.structures import CaseInsensitiveDict
import json


app = Flask(__name__)

@app.get('/full/<topic>')
def full(topic):
    url = f"https://api.repo.nypl.org/api/v2/items/search?q={topic}"
    session = requests.session()
    session.headers.update(nypl_auth_header())
    response = session.get(url)
    return response.json()

@app.get('/locations/<query>')
def nypl(query):
    max_results = 60
    nypl_page_size = 20
    url = f"https://api.repo.nypl.org/api/v2/items/search?q={query}&per_page={nypl_page_size}"
    session = requests.session()
    session.headers.update(nypl_auth_header())

    first_page_content = next(get_search_results(url, session, 1))['nyplAPI']['response']
    total_results = int(first_page_content['numResults'])
    #If we get no results, just return nypl response
    if int(first_page_content['numResults']) < 1:
        return first_page_content
    
    all_locations = dict() 
    for response in get_search_results(url, session, max_results // nypl_page_size):
        response_content = response['nyplAPI']['response']

        #Extract the uri for mod info of each item 
        mods = [item["apiUri"] for item in response_content['result']]

        for uri in mods:
            found_locations = extract_physical_locations(uri, session)
            for location in found_locations:
                all_locations[location] = all_locations.get(location, 0) + 1
        
    return {'locations': all_locations, 'num_results': total_results, 'results_excluded': max(0, total_results - max_results)}

# Takes uri to item MODS data and extracts all unique physical locations
#TODO: run this asynchronously
def extract_physical_locations(uri, session):
    mod_response = session.get(uri)
    locations_data = mod_response.json()['nyplAPI']['response']['mods'].get("location",[])
    # location field can be JSON list or object. Encapsulate in a list if it's not already
    if isinstance(locations_data, dict):
        locations_data = [locations_data]

    # I think each item should only be at 1 physical location.
    # But I couldn't confirm this in the mods docs.
    # So we will collect all unique locations rather than returning the first we find.
    found_locations = set() 
    for location in locations_data:
        physical_locations = location.get('physicalLocation', [])
        
        if isinstance(physical_locations, dict):
            physical_locations = [physical_locations]

        for sub_location in physical_locations:
            if sub_location['type'] == 'division_short_name':
                found_locations.add(sub_location['$'])
    return found_locations

#generator function to handle pagenation
def get_search_results(url, session, max_pages):
    first_page = session.get(url).json()
    yield first_page
    last_page = int(first_page['nyplAPI']['request']['totalPages'])
    #go to max or final page, whichever comes first
    for i in range(2, min(max_pages, last_page) + 1):
        next_page = session.get(f'{url}&page={i}').json()
        yield next_page

def nypl_auth_header():
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Token token=\"55kyp8iux7zjpbbh\""
    return headers
