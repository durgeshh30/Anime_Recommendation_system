import streamlit as st
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import requests


movies = pickle.load(open('movies.pkl', 'rb'))
vectors = pickle.load(open('vector.pkl', 'rb'))

API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    data = requests.get(url).json()

    if 'poster_path' in data and data['poster_path']:
        return "https://image.tmdb.org/t/p/w500" + data['poster_path']
    else:
        return None


def recommend(movie, top_n=5):
    movie = movie.lower()

    if movie not in movies['title'].str.lower().values:
        return [], []

    index = movies[movies['title'].str.lower() == movie].index[0]

    sim_scores = cosine_similarity(
        vectors[index:index+1],
        vectors
    )[0]

    movie_indices = sim_scores.argsort()[::-1][1:top_n+1]

    recommended_titles = []
    recommended_posters = []

    for i in movie_indices:
        movie_id = movies.iloc[i]['id']   # TMDB movie id
        recommended_titles.append(movies.iloc[i]['title'])
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters


st.title("🎬 Anime Recommendation System")

option = st.selectbox(
    "Select your favourite anime",
    [""] + movies['title'].tolist(),
    index=0
)

if st.button("Recommend"):
    names, posters = recommend(option, top_n=10)

    st.subheader("Top 10 Recommended Anime")

    num_cols = 5
    for i in range(0, len(names), num_cols):
        cols = st.columns(num_cols)

        for j in range(num_cols):
            idx = i + j
            if idx >= len(names):
                break

            with cols[j]:
                if posters[idx]:
                    st.image(posters[idx], use_container_width=True)
                st.caption(names[idx])


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8501))
