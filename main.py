import requests

# Your Client ID
CLIENT_ID = '0f547300'

# Base URL for the Jamendo API
BASE_URL = 'https://api.jamendo.com/v3.0/'

def search_tracks(query, limit=5):
    # Endpoint for searching tracks
    url = f"{BASE_URL}tracks/"
    
    # Parameters for the API call
    params = {
        'client_id': CLIENT_ID,  # Your Client ID
        'format': 'json',        # Response format
        'limit': limit,          # Limit the number of results
        'search': query          # Search term
    }
    
    # Make the GET request
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        tracks = response.json()
        # Loop through and display the track information
        for track in tracks['results']:
            print(f"Track Name: {track['name']}")
            print(f"Artist Name: {track['artist_name']}")
            print(f"Album Name: {track['album_name']}")
            print(f"Stream URL: {track['audiodownload']}")
            print('-' * 40)
    else:
        print(f"Failed to fetch tracks. Status code: {response.status_code}")

# Example usage: search for tracks with the query "rock"
search_tracks('Travis')
