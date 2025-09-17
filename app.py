import pickle
import streamlit as st
import requests

# ================== Page Config ==================
st.set_page_config(
    page_title="CineMatch 🎬",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================== Custom CSS ==================
st.markdown("""
    <style>
        body { background-color: #0E1117; color: #FAFAFA; }
        .title { font-size:45px; font-weight:bold; color:#E50914; text-align:center; margin-bottom:10px; }
        .tagline { text-align:center; color:#bbb; margin-bottom:25px; }

        .movie-card {
            background-color:#1c1c1c;
            border-radius:12px;
            padding:10px;
            margin:8px;
            text-align:center;
            color:white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.4);
            height: 460px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }

        .movie-card img {
            width:100%;
            height:260px;
            object-fit:cover;
            border-radius:8px;
        }

        .movie-title {
            font-size:16px;
            font-weight:600;
            margin-top:8px;
            min-height:40px;
            overflow:hidden;
            text-overflow:ellipsis;
        }

        .movie-rating {
            color:#FFD700;
            font-size:14px;
            margin:6px 0;
        }

        .full-overview {
            font-size:14px;
            color:#e0e0e0;
            text-align:justify;
        }

        /* Sidebar active link */
        .sidebar-item {
            font-size:16px;
            padding:8px 12px;
            border-radius:8px;
            margin:6px 0;
            display:block;
        }
        .sidebar-active {
            background-color:#E50914;
            color:white !important;
            font-weight:bold;
        }
        .sidebar-inactive {
            color:#ccc;
        }
    </style>
""", unsafe_allow_html=True)

# ================== API Key ==================
API_KEY = st.secrets["API_KEY"]

# ================== Fetch Functions ==================
@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    data = requests.get(url).json()
    poster = "https://via.placeholder.com/500x750?text=No+Image"
    if data.get('poster_path'):
        poster = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    title = data.get('title', 'Unknown Title')
    rating = data.get('vote_average', 'N/A')
    overview = data.get('overview', 'No description available.')
    release_date = data.get('release_date', 'Unknown')
    genres = ", ".join([g['name'] for g in data.get('genres', [])]) if data.get('genres') else "Unknown"
    return poster, title, rating, overview, release_date, genres

@st.cache_data(show_spinner=False)
def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}&language=en-US"
    data = requests.get(url).json()
    for video in data.get("results", []):
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

@st.cache_data(show_spinner=False)
def fetch_trending():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
    data = requests.get(url).json()
    movies_list = []
    for m in data.get("results", [])[:10]:
        movie_id = m["id"]
        poster, title, rating, overview, release_date, genres = fetch_movie_details(movie_id)
        movies_list.append((movie_id, poster, title, rating, overview, release_date, genres))
    return movies_list

@st.cache_data(show_spinner=False)
def fetch_top_rated():
    url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&language=en-US&page=1"
    data = requests.get(url).json()
    movies_list = []
    for m in data.get("results", [])[:10]:
        movie_id = m["id"]
        poster, title, rating, overview, release_date, genres = fetch_movie_details(movie_id)
        movies_list.append((movie_id, poster, title, rating, overview, release_date, genres))
    return movies_list

@st.cache_data(show_spinner=False)
def fetch_by_genre(genre_id):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={genre_id}&language=en-US&page=1"
    data = requests.get(url).json()
    movies_list = []
    for m in data.get("results", [])[:10]:
        movie_id = m["id"]
        poster, title, rating, overview, release_date, genres = fetch_movie_details(movie_id)
        movies_list.append((movie_id, poster, title, rating, overview, release_date, genres))
    return movies_list

# ================== Card Renderer ==================
def render_movie_card(poster, title, rating, overview, release_date, genres, trailer):
    st.markdown(
        f"""
        <div class="movie-card">
            <img src="{poster}">
            <div class="movie-title">{title}</div>
            <div class="movie-rating">⭐ {rating}/10</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    with st.expander("ℹ️ More Info"):
        st.markdown(
            f"<div class='full-overview'><b>Release Date:</b> {release_date}<br>"
            f"<b>Genres:</b> {genres}<br><br>{overview}</div>",
            unsafe_allow_html=True
        )
        if trailer:
            st.markdown(f"[▶ Watch Trailer]({trailer})")

# ================== Recommendation Engine ==================
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    details = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        details.append((movie_id,) + fetch_movie_details(movie_id))
    return details

# ================== Load Pickles ==================
movies = pickle.load(open('model/movie_list.pkl','rb'))
similarity = pickle.load(open('model/similarity.pkl','rb'))

# ================== Header ==================
st.markdown("<h1 class='title'>🍿 CineMatch 🎬</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>Find your perfect movie match!</p>", unsafe_allow_html=True)

# ================== Sidebar ==================
st.sidebar.markdown("## 🍿 CineMatch 🎬")
st.sidebar.markdown("Find your perfect movie match!")
st.sidebar.markdown("---")

menu_options = {
    "🔥 Trending": "trending",
    "🎥 Recommendations": "recommendations",
    "⭐ Top Rated": "top_rated",
    "🎭 Browse by Genre": "genre",
    "ℹ️ About": "about"
}

params = st.query_params
page_param = params.get("page", None)

if "page" not in st.session_state:
    st.session_state.page = page_param if page_param in menu_options.values() else "trending"
else:
    if page_param and page_param in menu_options.values() and st.session_state.page != page_param:
        st.session_state.page = page_param

for label, key in menu_options.items():
    is_active = (st.session_state.page == key)
    if is_active:
        st.sidebar.markdown(f"<div class='sidebar-item sidebar-active'>{label}</div>", unsafe_allow_html=True)
    else:
        if st.sidebar.button(label, key=f"sidebar_{key}"):
            st.session_state.page = key
            st.query_params["page"] = key
            st.rerun()

# ================== Pages ==================
if st.session_state.page == "trending":
    st.subheader("Trending Movies This Week")
    trending = fetch_trending()
    cols = st.columns(5)
    for i, movie in enumerate(trending):
        movie_id, poster, title, rating, overview, release_date, genres = movie
        trailer = fetch_trailer(movie_id)
        with cols[i % 5]:
            render_movie_card(poster, title, rating, overview, release_date, genres, trailer)

elif st.session_state.page == "recommendations":
    st.subheader("Get Similar Movie Recommendations")
    movie_list = movies['title'].values
    selected_movie = st.selectbox("Search or select a movie:", movie_list, key="select_movie")

    if st.button('🔎 Show Recommendations', key="recs_button"):
        st.session_state.selected_movie = selected_movie
        st.session_state.show_recs_flag = True  # <-- different name
        st.session_state.page = "recommendations"
        st.query_params["page"] = "recommendations"
        st.rerun()

    if st.session_state.get("show_recs_flag", False) and "selected_movie" in st.session_state:
        recommendations = recommend(st.session_state.selected_movie)
        cols = st.columns(5)
        for i, col in enumerate(cols):
            movie_id, poster, title, rating, overview, release_date, genres = recommendations[i]
            trailer = fetch_trailer(movie_id)
            with col:
                render_movie_card(poster, title, rating, overview, release_date, genres, trailer)

elif st.session_state.page == "top_rated":
    st.subheader("Top Rated Movies")
    top_rated = fetch_top_rated()
    cols = st.columns(5)
    for i, movie in enumerate(top_rated):
        movie_id, poster, title, rating, overview, release_date, genres = movie
        trailer = fetch_trailer(movie_id)
        with cols[i % 5]:
            render_movie_card(poster, title, rating, overview, release_date, genres, trailer)

elif st.session_state.page == "genre":
    st.subheader("Browse by Genre")
    genre_map = {
        "Action": 28, "Comedy": 35, "Drama": 18, "Horror": 27,
        "Romance": 10749, "Science Fiction": 878, "Thriller": 53, "Animation": 16
    }
    genre_name = st.selectbox("Select Genre:", list(genre_map.keys()), key="select_genre")
    
    if genre_name:
        genre_id = genre_map[genre_name]
        st.session_state.selected_genre = genre_name
        st.session_state.page = "genre"
        st.query_params["page"] = "genre"

        # ✅ Now fetch movies without rerunning endlessly
        genre_movies = fetch_by_genre(genre_id)
        cols = st.columns(5)
        for i, movie in enumerate(genre_movies):
            movie_id, poster, title, rating, overview, release_date, genres = movie
            trailer = fetch_trailer(movie_id)
            with cols[i % 5]:
                render_movie_card(poster, title, rating, overview, release_date, genres, trailer)

elif st.session_state.page == "about":
    st.subheader("About CineMatch")
    st.markdown("""
        **CineMatch** is a smart movie recommender system built with TMDB API 🎬  
        - 🔥 Discover **trending movies** this week  
        - 🎥 Get **recommendations** based on your favorite movies  
        - ⭐ Explore **top rated classics**  
        - 🎭 Browse **movies by genre**  
        - ▶ Watch **trailers** instantly  

        Built with ❤️ using **Streamlit** + **TMDB API**.
    """)
