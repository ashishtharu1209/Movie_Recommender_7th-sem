import subprocess
import time
import webbrowser
import streamlit as st
import pandas as pd
import numpy as np
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import urllib.parse

# OMDB API Key (Replace with your own key)
API_KEY = "4fe01f52"  # Replace this with your actual OMDB API key

# Load the dataset with caching
@st.cache_data
def load_data():
    try:
        data = pd.read_csv(r"C:\xampp\htdocs\clone\Movie_Recommender_7th-sem\main\Data\movie_metadata.csv")
        return data
    except FileNotFoundError:
        st.error("Dataset not found! Please check the file path.")
        return pd.DataFrame()

# Load dataset
movies_df = load_data()

# Check dataset columns
required_columns = {"movie_title", "plot_keywords", "genres", "director_name", "actor_1_name", "actor_2_name"}
missing_columns = required_columns - set(movies_df.columns)
if missing_columns:
    st.error(f"The dataset is missing the following columns: {', '.join(missing_columns)}.")
    st.stop()

# Fill missing values
movies_df = movies_df.fillna("")

# Function to fetch movie information from OMDB API
def fetch_movie_info_from_api(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to recommend movies using multiple features
def recommend_movies(movie_name, movies, top_n=10):
    # Preprocess the dataset
    movies['combined_features'] = (
        movies['plot_keywords'] + " " +
        movies['genres'] + " " +
        movies['director_name'] + " " +
        movies['actor_1_name'] + " " +
        movies['actor_2_name']
    )

    # TF-IDF vectorization
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies['combined_features'])

    # Compute cosine similarity
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Index mapping for movie titles
    indices = pd.Series(movies.index, index=movies['movie_title'].str.strip().str.lower())

    # Check if the movie exists in the dataset
    if movie_name.lower() not in indices:
        st.write(f"Oops! We couldn’t find movies similar to your recent watch. Let’s find something else you’d love—browse by genre or movie name!")
        return []

    idx = indices[movie_name.lower()]

    # Get similarity scores for the movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort movies based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: np.mean(x[1]) if isinstance(x[1], np.ndarray) else x[1], reverse=True)

    # Get the indices of the top N most similar movies, skipping the movie itself
    sim_indices = [i[0] for i in sim_scores[1:top_n + 1]]

    # Ensure the recommendations are unique
    unique_recommendations = movies.iloc[sim_indices].drop_duplicates(subset=['movie_title'])

    # Return the top N unique similar movies
    return unique_recommendations

# Fetch movie name from URL query parameter
movie_param = st.query_params.get("movie", None)

# If the 'movie' parameter exists, decode it
if movie_param:
    movie_name = urllib.parse.unquote_plus(movie_param)  # Decode the movie name

    # Slider for selecting the number of recommendations
    num_recommendations = st.slider("Select number of recommendations:", min_value=5, max_value=20, step=1)

    st.subheader(f"People who liked '{movie_name}' also like:")
    recommendations = recommend_movies(movie_name, movies_df, top_n=num_recommendations)

    if len(recommendations) > 0:
        for idx, row in enumerate(recommendations.iterrows(), start=1):
            movie_title = row[1]["movie_title"]

            # Fetch movie details from OMDB API
            movie_info = fetch_movie_info_from_api(movie_title)
            if movie_info and movie_info.get("Response") == "True":
                imdb_id = movie_info.get("imdbID", "")
                imdb_url = f"https://www.imdb.com/title/{imdb_id}" if imdb_id else "#"

                # Display recommendation with IMDb link and numbering
                st.markdown(f"**{idx}. [{movie_title}]({imdb_url})**")

                # Display movie poster
                poster_url = movie_info.get("Poster", "")
                if poster_url and poster_url != "N/A":
                    st.image(poster_url, width=200)

                # Display additional details
                st.markdown(f"**Director:** {movie_info.get('Director', 'N/A')}")
                st.markdown(f"**Cast:** {movie_info.get('Actors', 'N/A')}")
                st.markdown(f"**Plot:** {movie_info.get('Plot', 'N/A')}")
                st.markdown(f"**IMDb Rating:** {movie_info.get('imdbRating', 'N/A')}⭐")
                st.markdown("---")
            else:
                st.write(f"**{idx}. {movie_title}** (Details not available)")
    else:
        if st.button("Click Here"):
            subprocess.Popen(["streamlit", "run", "app.py", "--server.port", "8501"])
            # Wait a moment to ensure the server has started
            time.sleep(2)
            # Open the app in the default browser
            webbrowser.open("http://localhost:8501")

else:
    st.write("No movie selected. Please pass a movie name as a query parameter in the URL.")
