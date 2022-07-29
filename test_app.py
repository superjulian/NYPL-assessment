import pytest
import requests
import responses
from app import app

@pytest.fixture()
def client():
    return app.test_client()

@responses.activate
def test_if_one_result_then_expected_response(client):
    expected_location_name = "EXPECTED_LOCATION_NAME"
    test_query = "TEST_QUERY"
    mock_api_uri = "http://API_URI"
    mock_items_search_resp = {
        'nyplAPI': {
            'request': {'totalPages': '1'},
                
            'response': {
                'numResults': '1',
                'result': [ {'apiUri': mock_api_uri} ]
                }
            }
        }
    mock_items_mods_resp =  {
            'nyplAPI': {
                'response': {
                    'mods': {
                        'location': {
                            'physicalLocation': {
                                '$': expected_location_name,
                                'type': 'division_short_name'
                                }
                            }
                        }
                    }
                }
            }
    responses.add(responses.GET, f'https://api.repo.nypl.org/api/v2/items/search?q={test_query}&per_page=20',
        json=mock_items_search_resp, status=200)
    responses.add(responses.GET, mock_api_uri, json=mock_items_mods_resp, status=200)
    response = client.get(f"/locations/{test_query}")
    assert response.json['locations']['EXPECTED_LOCATION_NAME'] == 1
