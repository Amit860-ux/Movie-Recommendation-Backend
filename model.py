import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle

# 1. Load CSVs
movies = pd.read_csv("dataset/tmdb_5000_movies.csv")
credits = pd.read_csv("dataset/tmdb_5000_credits.csv").rename(columns={"movie_id": "id"})

# 2. Merge: keep only cast and crew from credits to avoid duplicate title
df = movies.merge(credits[['id', 'cast', 'crew']], on='id')

# 3. Fill NaN values
df['overview'] = df['overview'].fillna('')
df['genres'] = df['genres'].fillna('')
df['keywords'] = df['keywords'].fillna('')
df['cast'] = df['cast'].fillna('')
df['crew'] = df['crew'].fillna('')

# 4. Preprocess columns
def parse_names(text):
    try:
        items = ast.literal_eval(text)
        names = [i['name'].replace(" ", "") for i in items]
        return " ".join(names)
    except:
        return ""

df['genres'] = df['genres'].apply(parse_names)
df['keywords'] = df['keywords'].apply(parse_names)

def get_top_cast(text):
    try:
        items = ast.literal_eval(text)
        names = [i['name'].replace(" ", "") for i in items[:3]]
        return " ".join(names)
    except:
        return ""

df['cast'] = df['cast'].apply(get_top_cast)

def get_director(text):
    try:
        items = ast.literal_eval(text)
        for i in items:
            if i['job'] == 'Director':
                return i['name'].replace(" ", "")
        return ""
    except:
        return ""

df['director'] = df['crew'].apply(get_director)

# 5. Combine features
df['combined_features'] = df['overview'] + " " + df['genres'] + " " + df['keywords'] + " " + df['cast'] + " " + df['director']

# 6. Train TF-IDF
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['combined_features'])

# 7. Save vectorizer and matrix
pickle.dump(tfidf, open("tfidf.pkl", "wb"))
pickle.dump(tfidf_matrix, open("tfidf_matrix.pkl", "wb"))

# 8. Save movies DataFrame with only title and combined_features
df_to_pickle = df[['title', 'combined_features']]
pickle.dump(df_to_pickle, open("movies.pkl", "wb"))

# 9. Recommendation function
def recommend_movies(user_input, top_n=5):
    tfidf = pickle.load(open("tfidf.pkl", "rb"))
    tfidf_matrix = pickle.load(open("tfidf_matrix.pkl", "rb"))
    movies = pickle.load(open("movies.pkl", "rb"))

    # Ensure 'title' exists
    if 'title' not in movies.columns:
        raise ValueError("The movies DataFrame must contain a 'title' column.")

    input_vec = tfidf.transform([user_input])
    cosine_sim = linear_kernel(input_vec, tfidf_matrix).flatten()
    top_indices = cosine_sim.argsort()[-top_n:][::-1]
    recommended = movies.iloc[top_indices]['title'].tolist()
    return recommended