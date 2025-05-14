import time
import json
import tmdbsimple as tmdb

# Configuration
INPUT_FILE = "2022.txt"
OUTPUT_FILE = "2022_results.json"
PROGRESS_FILE = "2022_progress.json"
DELAY = 0.25  # 4 requests per second

# Setup
tmdb.API_KEY = "your-api-key-here"  

def get_movie_details(movie_id):
    try:
        movie = tmdb.Movies(movie_id)
        data = movie.info(append_to_response="keywords,release_dates,watch/providers")
        return {'id': data['id'], 'title': data['title']}
    except:
        return None

def main():
    # Load progress
    try:
        with open(PROGRESS_FILE) as f:
            progress = json.load(f)
    except:
        progress = {'done': []}

    # Process IDs
    with open(INPUT_FILE) as f:
        ids = [line.strip() for line in f]

    for movie_id in ids:
        if movie_id not in progress['done']:
            result = get_movie_details(movie_id)
            if result:
                with open(OUTPUT_FILE, 'a') as f:
                    json.dump(result, f)
                    f.write('\n')
            progress['done'].append(movie_id)
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress, f)
            time.sleep(DELAY)

if __name__ == "__main__":
    main()
