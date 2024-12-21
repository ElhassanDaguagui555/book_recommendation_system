
#utils/recommander

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def load_data(conn):
    query = "SELECT id, title, image, description FROM books"
    df = pd.read_sql_query(query, conn)
    if df.empty:
        print("No books found in the database.")
    return df

def train_model(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['description'].fillna(''))
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def recommend_books(conn, user_id, num_recommendations=5, based_on_search=None):
    df = load_data(conn)
    if df.empty:
        return []
    
    cosine_sim = train_model(df)
    
    if based_on_search:
        # Recommandations basées sur la recherche
        idx = df[df['title'].str.contains(based_on_search, case=False) |
                 df['author'].str.contains(based_on_search, case=False) |
                 df['genre'].str.contains(based_on_search, case=False)].index
    else:
        # Recommandations basées sur le dernier livre emprunté
        last_book_id = get_last_borrowed_book_id(conn, user_id)
        if last_book_id is None:
            return []
        idx = df[df['id'] == last_book_id].index
    
    if len(idx) == 0:
        return []
    idx = idx[0]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num_recommendations+1]
    
    book_indices = [i[0] for i in sim_scores]
    return df.iloc[book_indices].to_dict('records')

def get_last_borrowed_book_id(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT book_id FROM loans WHERE user_id = ? ORDER BY loan_date DESC LIMIT 1", (user_id,))
    last_book = c.fetchone()
    if last_book:
        return last_book[0]
    else:
        return None