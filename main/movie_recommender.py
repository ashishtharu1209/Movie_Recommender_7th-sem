import time
import webbrowser
import numpy as np
import streamlit as st
import pandas as pd
import requests
import urllib.parse
import subprocess
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# OMDB API Key (Make sure to replace it with your own API key)
API_KEY = "4fe01f52"  # Replace with your actual OMDB API key

# Load the dataset with st.cache_data
@st.cache_data
def load_data():
    try:
        # Update the path to your dataset; use a relative path or cloud storage for deployment
        data = pd.read_csv(r"C:\xampp\htdocs\clone\Movie_Recommender_7th-sem\main\Data\movie_metadata.csv")
        return data
    except FileNotFoundError:
        st.error("Dataset not found! Please check the file path.")
        return pd.DataFrame()  # Return an empty DataFrame if the file is missing

# Load dataset
movies_df = load_data()

# Check if the dataset has the required columns
required_columns = {"movie_title", "plot_keywords"}
missing_columns = required_columns - set(movies_df.columns)
if missing_columns:
    st.error(f"The dataset is missing the following columns: {', '.join(missing_columns)}.")
    st.stop()

# Function to fetch movie information including the IMDb ID from OMDB API
def fetch_movie_info_from_api(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching data for {movie_title}.")
        return None

# Function to recommend movies
def recommend_movies(movie_name, movies, top_n=5):
    # TF-IDF Vectorization on the "plot_keywords" column
    tfidf = TfidfVectorizer(stop_words="english")
    movies["plot_keywords"] = movies["plot_keywords"].fillna("")  # Fill NaN descriptions with empty strings
    tfidf_matrix = tfidf.fit_transform(movies["plot_keywords"])

    # Compute cosine similarity between all movies
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Get the index of the movie that matches the title
    indices = pd.Series(movies.index, index=movies["movie_title"].str.strip().str.lower())

    if movie_name.lower() not in indices:
        st.write(f"Oops! We couldn’t find movies similar to your recent watch. Let’s find something else you’d love—browse by genre, cast, or director!")
        return []

    idx = indices[movie_name.lower()]

    # Get the pairwise similarity scores of all movies with the input movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: np.mean(x[1]) if isinstance(x[1], np.ndarray) else x[1], reverse=True)

    # Get the indices of the top N most similar movies
    sim_indices = [i[0] for i in sim_scores[1:top_n + 1]]

    # Return the top N most similar movies
    return movies.iloc[sim_indices]

# Retrieve the 'movie' query parameter as a string
movie_param = st.query_params.get("movie", None)

# If the 'movie' parameter exists, decode it
if movie_param:
    movie_name = urllib.parse.unquote_plus(movie_param)  # Directly decode the string


# Check if movie_name exists and is valid
if movie_name:
    st.subheader(f"People who liked {movie_name} also like:")

    recommendations = recommend_movies(movie_name, movies_df)

    if len(recommendations) > 0:
        for idx, row in enumerate(recommendations.iterrows(), start=1):
            movie_title = row[1]["movie_title"]
            
            # Fetch movie details (including IMDb ID) from OMDB API
            movie_info = fetch_movie_info_from_api(movie_title)
            if movie_info and movie_info.get("Response") == "True":
                imdb_id = movie_info.get("imdbID", "")
                imdb_url = f"https://www.imdb.com/title/{imdb_id}" if imdb_id else "#"
                
                # Display recommendation with IMDb link
                st.markdown(f"**{idx}. [ {movie_title}]({imdb_url})**")

                # Display movie poster
                poster_url = movie_info.get("Poster")
                if poster_url and poster_url != "N/A":
                    st.image(poster_url, width=300)
                else:
                    st.error("Poster not found.")

                # Display other movie information
                st.markdown(f"**Director:** {movie_info.get('Director', 'N/A')}")
                st.markdown(f"**Cast:** {movie_info.get('Actors', 'N/A')}")
                st.markdown(f"**Plot:** {movie_info.get('Plot', 'N/A')}")
                st.markdown(f"**IMDb Rating:** {movie_info.get('imdbRating', 'N/A')}⭐")
                st.markdown("---")  # Separator for recommendations
            else:
                st.markdown(f"**{idx}. {movie_title}**")
    else:
        if st.button("Click Here"):
             subprocess.Popen(["streamlit", "run", "app.py", "--server.port", "8501"])
             # Wait a moment to ensure the server has started
             time.sleep(2)
             # Open the app in the default browser
             webbrowser.open("http://localhost:8501")
    
else:
    st.write("No movie selected. Pass a movie name as a query parameter in the URL.")
