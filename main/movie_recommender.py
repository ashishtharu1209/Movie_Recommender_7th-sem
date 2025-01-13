import streamlit as st
import pandas as pd
import requests
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

# Function to fetch movie information including the poster from OMDB API
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
        st.write(f"No matching movie found for: {movie_name}. Please try a different movie.")
        return []

    idx = indices[movie_name.lower()]

    # Get the pairwise similarity scores of all movies with the input movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the indices of the top N most similar movies
    sim_indices = [i[0] for i in sim_scores[1:top_n + 1]]

    # Return the top N most similar movies
    return movies.iloc[sim_indices]

# Get the movie name from the query parameter
movie_name = st.experimental_get_query_params().get("movie", [""])[0]

# Check if movie_name exists and is valid
if movie_name:
    st.subheader(f"Recommendations after watching: {movie_name}")

    recommendations = recommend_movies(movie_name, movies_df)

    if len(recommendations) > 0:
        for _, row in recommendations.iterrows():
            st.markdown(f"**{row['movie_title']}**")
            
            # Fetch movie details (including poster) from OMDB API
            movie_info = fetch_movie_info_from_api(row['movie_title'])
            if movie_info and movie_info.get('Response') == 'True':
                # Display IMDb link, Director, Cast, Plot, and Rating
                st.markdown(f"Director: {movie_info.get('Director', 'N/A')}")
                st.markdown(f"Cast: {movie_info.get('Actors', 'N/A')}")
                st.markdown(f"Plot: {movie_info.get('Plot', 'N/A')}")
                st.markdown(f"IMDB Rating: {movie_info.get('imdbRating', 'N/A')}⭐")

                # Display movie poster
                poster_url = movie_info.get('Poster')
                if poster_url and poster_url != 'N/A':
                    st.image(poster_url, use_column_width=True)
                else:
                    st.error("Poster not found.")
            else:
                st.error(f"Details for {row['movie_title']} could not be fetched.")

    else:
        st.write("No recommendations found for this movie. Please try again.")
else:
    st.write("No movie selected. Pass a movie name as a query parameter in the URL. Example: ?movie=Inception")
