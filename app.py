from flask import Flask, render_template, request, jsonify, make_response, session
import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'
load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
POSTER_BASE_URL = 'https://image.tmdb.org/t/p/w500'
BACKDROP_BASE_URL = 'https://image.tmdb.org/t/p/original'

def get_saved_posters():
    posters = request.cookies.get('saved_posters')
    if posters:
        try:
            return json.loads(posters)
        except:
            return []
    return []

@app.route('/')
def index():
    saved_posters = get_saved_posters()
    return render_template('index.html', posters=saved_posters)

@app.route('/movie/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    # Fetch detailed movie information
    movie_url = f'{TMDB_BASE_URL}/movie/{movie_id}'
    response = requests.get(movie_url, params={
        'api_key': TMDB_API_KEY,
        'append_to_response': 'credits,videos,similar'
    })

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch movie details'}), 500

    movie_data = response.json()
    
    # Format the data
    formatted_data = {
        'id': movie_data['id'],
        'title': movie_data['title'],
        'overview': movie_data['overview'],
        'release_date': datetime.strptime(movie_data['release_date'], '%Y-%m-%d').strftime('%B %d, %Y') if movie_data.get('release_date') else 'N/A',
        'runtime': f"{movie_data['runtime']} minutes" if movie_data.get('runtime') else 'N/A',
        'vote_average': round(movie_data['vote_average'], 1),
        'poster_url': f"{POSTER_BASE_URL}{movie_data['poster_path']}" if movie_data.get('poster_path') else None,
        'backdrop_url': f"{BACKDROP_BASE_URL}{movie_data['backdrop_path']}" if movie_data.get('backdrop_path') else None,
        'genres': [genre['name'] for genre in movie_data.get('genres', [])],
        'director': next((crew['name'] for crew in movie_data['credits']['crew'] if crew['job'] == 'Director'), 'N/A'),
        'cast': [{'name': cast['name'], 'character': cast['character']} 
                for cast in movie_data['credits'].get('cast', [])[:5]],
        'trailer_key': next((video['key'] for video in movie_data['videos']['results'] 
                           if video['type'] == 'Trailer' and video['site'] == 'YouTube'), None),
        'similar_movies': [{
            'id': movie['id'],
            'title': movie['title'],
            'poster_url': f"{POSTER_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None
        } for movie in movie_data['similar']['results'][:4]]
    }

    return jsonify(formatted_data)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400

    try:
        # Search for movies
        movie_url = f"https://api.themoviedb.org/3/search/movie"
        movie_params = {
            'api_key': TMDB_API_KEY,
            'query': query,
        }
        movie_response = requests.get(movie_url, params=movie_params)
        movie_data = movie_response.json()

        # Search for directors
        person_url = f"https://api.themoviedb.org/3/search/person"
        person_params = {
            'api_key': TMDB_API_KEY,
            'query': query,
        }
        person_response = requests.get(person_url, params=person_params)
        person_data = person_response.json()

        # Process directors and their movies
        directors = []
        for person in person_data['results'][:2]:
            person_details = requests.get(
                f"https://api.themoviedb.org/3/person/{person['id']}",
                params={'api_key': TMDB_API_KEY}
            ).json()
            
            if 'known_for_department' in person_details and person_details['known_for_department'] == 'Directing':
                movies_url = f"https://api.themoviedb.org/3/discover/movie"
                movies_params = {
                    'api_key': TMDB_API_KEY,
                    'with_crew': person['id'],
                    'sort_by': 'vote_average.desc',
                    'vote_count.gte': 100
                }
                
                movies_response = requests.get(movies_url, params=movies_params)
                movies_data = movies_response.json()

                director_info = {
                    'name': person['name'],
                    'id': person['id'],
                    'profile_path': person.get('profile_path'),
                    'movies': []
                }

                for movie in movies_data['results'][:6]:
                    if movie['poster_path']:
                        director_info['movies'].append({
                            'id': movie['id'],
                            'title': movie['title'],
                            'poster_path': movie['poster_path'],
                            'vote_average': movie['vote_average'],
                            'release_date': movie['release_date']
                        })
                
                if director_info['movies']:
                    directors.append(director_info)

        # Format the response
        response_data = {
            'movies': [movie for movie in movie_data['results'][:5] if movie.get('poster_path')],
            'directors': directors
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add-movie', methods=['POST'])
def add_movie():
    movie_data = request.json
    if not movie_data:
        return jsonify({'error': 'No movie data provided'}), 400

    try:
        # Get existing posters
        saved_posters = get_saved_posters()
        
        # Create new poster data
        new_poster = {
            'id': movie_data['id'],
            'title': movie_data['title'],
            'poster_url': f'{POSTER_BASE_URL}{movie_data["poster_path"]}'
        }
        
        # Add to saved posters if not already present
        if new_poster not in saved_posters:
            saved_posters.append(new_poster)
        
        # Create response with the movie data
        response = jsonify({'message': 'Movie added successfully', 'movie': new_poster})
        
        # Set cookie with updated posters
        response.set_cookie('saved_posters', json.dumps(saved_posters), max_age=31536000)  # 1 year expiry
        
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete-poster', methods=['POST'])
def delete_poster():
    poster_id = request.form.get('poster_id')
    if not poster_id:
        return jsonify({'error': 'Poster ID is required'}), 400

    # Get existing posters
    saved_posters = get_saved_posters()
    
    # Remove the poster with matching ID
    saved_posters = [p for p in saved_posters if str(p['id']) != str(poster_id)]
    
    # Create response
    response = make_response(jsonify({'message': 'Poster deleted'}))
    
    # Update cookie with remaining posters
    response.set_cookie('saved_posters', json.dumps(saved_posters), max_age=31536000)
    
    return response

@app.route('/clear-posters', methods=['POST'])
def clear_posters():
    response = make_response(jsonify({'message': 'Posters cleared'}))
    response.delete_cookie('saved_posters')
    return response

@app.route('/search_director', methods=['GET'])
def search_director():
    director_name = request.args.get('name')
    if not director_name:
        return jsonify({'error': 'No director name provided'}), 400

    try:
        # First, search for the director
        search_url = f"https://api.themoviedb.org/3/search/person"
        params = {
            'api_key': TMDB_API_KEY,
            'query': director_name,
        }
        response = requests.get(search_url, params=params)
        data = response.json()

        if not data['results']:
            return jsonify({'error': 'Director not found'}), 404

        # Find the first person who is known for directing
        director = None
        for person in data['results']:
            # Get person details to check if they're a director
            person_details = requests.get(
                f"https://api.themoviedb.org/3/person/{person['id']}",
                params={'api_key': TMDB_API_KEY}
            ).json()
            
            if 'known_for_department' in person_details and person_details['known_for_department'] == 'Directing':
                director = person
                break

        if not director:
            return jsonify({'error': 'No director found with that name'}), 404

        # Get director's movies
        movies_url = f"https://api.themoviedb.org/3/discover/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'with_crew': director['id'],
            'sort_by': 'vote_average.desc',
            'vote_count.gte': 100  # Only movies with at least 100 votes
        }
        
        movies_response = requests.get(movies_url, params=params)
        movies_data = movies_response.json()

        # Format the response
        director_info = {
            'name': director['name'],
            'id': director['id'],
            'profile_path': director['profile_path'],
            'movies': []
        }

        for movie in movies_data['results'][:8]:  # Limit to top 8 movies
            if movie['poster_path']:
                director_info['movies'].append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'poster_path': movie['poster_path'],
                    'vote_average': movie['vote_average'],
                    'release_date': movie['release_date']
                })

        return jsonify(director_info)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
