import time
import json
import os
import requests
import threading
from pathlib import Path
import tmdbsimple as tmdb

# Configuration
INPUT_FILE = "2000-2011.txt"
OUTPUT_FILE = "2000-2011results.json"
PROGRESS_FILE = "2000-2011progress.json"
DELAY = 0.25  # 4 requests/second
BATCH_SIZE = 100  # Save progress every 100 IDs

# Auto-load API key from Codespaces secret
tmdb.API_KEY = os.getenv('TMDB_KEY')

def keep_alive():
    """Prevent Codespace hibernation"""
    while True:
        requests.get("https://api.github.com")
        time.sleep(300)  # Ping every 5 minutes

def get_movie_details(movie_id):
    """Fetch movie details using tmdbsimple"""
    try:
        movie = tmdb.Movies(movie_id)
        data = movie.info(append_to_response="keywords,release_dates,watch/providers")
        
        # Process release dates
        country_releases = {}
        for country in data.get('release_dates', {}).get('results', []):
            iso = country['iso_3166_1']
            country_releases[iso] = [{'type': rd['type']} for rd in country['release_dates']]
        
        # Process providers
        providers = {}
        watch_data = data.get('watch/providers', {}).get('results', {})
        for country, country_data in watch_data.items():
            all_providers = set()
            for provider_type in ['flatrate', 'rent', 'buy']:
                all_providers.update(p['provider_name'] for p in country_data.get(provider_type, []))
            providers[country] = list(all_providers)
        
        return {
            'id': data['id'],
            'title': data['title'],
            'production_countries': [c['name'] for c in data.get('production_countries', [])],
            'revenue': data.get('revenue'),
            'primary_release_date': data.get('release_date'),
            'released_countries': country_releases,
            'overview': data.get('overview'),
            'tagline': data.get('tagline'),
            'runtime': data.get('runtime'),
            'budget': data.get('budget'),
            'genres': [g['name'] for g in data.get('genres', [])],
            'popularity': data.get('popularity'),
            'original_language': data.get('original_language'),
            'keywords': [kw['name'] for kw in data.get('keywords', {}).get('keywords', [])],
            'watch_providers': providers,
            'imdb_id': data.get('imdb_id')
        }
    except Exception as e:
        print(f"Error processing {movie_id}: {str(e)}")
        return None

def process_movies():
    Path(OUTPUT_FILE).touch()
    
    # Load progress
    try:
        with open(PROGRESS_FILE) as f:
            progress = json.load(f)
    except:
        progress = {'processed': [], 'last_id': 0}
    
    # Process IDs
    with open(INPUT_FILE) as f:
        all_ids = [line.strip() for line in f]
    
    for i, movie_id in enumerate(all_ids[progress['last_id']:], start=progress['last_id']):
        if movie_id in progress['processed']:
            continue
            
        result = get_movie_details(movie_id)
        if result:
            with open(OUTPUT_FILE, 'a') as f:
                f.write(json.dumps(result) + '\n')
        
        # Update progress
        progress['processed'].append(movie_id)
        progress['last_id'] = i + 1
        
        if (i + 1) % BATCH_SIZE == 0:
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress, f)
        
        time.sleep(DELAY)

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    process_movies()
