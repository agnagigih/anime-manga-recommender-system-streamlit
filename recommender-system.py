import pandas as pd
import numpy as np
import streamlit as st

# Backend section
manga = pd.read_csv('manga_display.csv')
manga_soup = pd.read_csv('manga_soup_genres_authors_based.csv')

anime = pd.read_csv('anime_clean.csv')
anime_soup = pd.read_csv('anime_soup_genres_based.csv')

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def cosine_similar(soup): 
    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(soup['soup'])
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    return cosine_sim

anime['title (type)'] = anime.title + ' (' + anime.type + ')'
manga['title (type)'] = manga.title + ' (' + manga.type +')'

anime_indicete = pd.Series(anime.index, index=anime['title (type)'])
manga_indicete = pd.Series(manga.index, index=manga['title (type)'])

def content_recommender(title, anime=True):
    if anime==True:
        cosine_sim = cosine_similar(anime_soup)
        idx = anime_indicete[title]
    else:
        cosine_sim = cosine_similar(manga_soup)
        idx = manga_indicete[title]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores,key=lambda x: x[1],reverse=True)

    sim_scores = sim_scores[1:11]
    
    recommend_indices = [i[0] for i in sim_scores]
    
    return recommend_indices

# Top Manga & Anime
top_manga = manga.sort_values(by=['score_'], ascending=False)
top_anime = anime.sort_values(by=['score_'], ascending=False)

# sort by genres
#anime
top_anime['list_genres'] = top_anime.genres.apply(lambda x: x.split(', '))
genres_of_anime = []
for i in top_anime.list_genres:
    for j in i:
        genres_of_anime.append(j)
genres_of_anime = set(genres_of_anime)
genres_of_anime.remove('Unknown')
genres_of_anime = list(genres_of_anime)

#manga
top_manga['list_genres'] = top_manga.genres.apply(lambda x: x.split(', '))
genres_of_manga = []
for i in top_manga.list_genres:
    for j in i:
        genres_of_manga.append(j)
genres_of_manga = set(genres_of_manga)
genres_of_manga.remove('Unknown')
genres_of_manga = list(genres_of_manga)

#filter
def filter_anime(x):
    if len(set(selected_genres_anime)) == len(set(x)&set(selected_genres_anime)):
        return 1
    else: return 0

def filter_manga(x):
    if len(set(selected_genres_manga)) == len(set(x)&set(selected_genres_manga)):
        return 1
    else: return 0

# Frontend section
#st.set_page_config(layout='wide')
st.markdown("<h1 style='text-align: center;'>Anime & Manga Recommender System</h1>", unsafe_allow_html=True)
st.markdown('---')
tab_1, tab_2 = st.tabs(['Anime', 'Manga'])

# Frontend Anime
anime_tab1, anime_tab2, anime_tab3 = tab_1.tabs(['Top Anime', 'Genre', 'Recommendation'])

def anime_frontend(recommendation, show=10):
    for i in range(show):
        with st.container():
            st.header(recommendation.iloc[i]['title'])
            col1, col2 = st.columns([2,6])
            col1.image(recommendation.iloc[i]['main_picture'])
            col2.subheader('Synopsis')
            col2.markdown(recommendation.iloc[i]['synopsis'])

            col3, col4 = st.columns([2,2])
            col3.markdown(
f'''
Type : {recommendation.iloc[i]['type'].upper()}\n
Episodes : {recommendation.iloc[i]['episodes']}\n
Status : {recommendation.iloc[i]['status'].title()}\n
Aired : {recommendation.iloc[i]['start_date']} to {recommendation.iloc[i]['end_date']}\n
Primiered : {recommendation.iloc[i]['start_season'].title()} {recommendation.iloc[i]['start_year']}\n
Producers : {recommendation.iloc[i]['producers']}\n
Source : {recommendation.iloc[i]['source'].title()}\n
Genre : {recommendation.iloc[i]['genres']}\n
Demographic : {recommendation.iloc[i]['demographics']}\n
Duration : {recommendation.iloc[i]['duration']}\n
Rating : {recommendation.iloc[i]['rating']}\n
Score : {recommendation.iloc[i]['score_']}\n
'''
)
            
            if recommendation.iloc[i]['trailer?']: 
                pass
            else:
                col4.video(recommendation.iloc[i]['trailer_url'])
            st.markdown('---')

# Top Anime
with anime_tab1:
    st.header('Top Rated Anime')
    anime_frontend(top_anime)

# Filter by genres - anime
with anime_tab2:
    st.header('Search anime by genre')
    selected_genres_anime = st.multiselect('Select your favorite anime genres', genres_of_anime)
    top_anime['filtered'] = top_anime.list_genres.apply(filter_anime)
    best_by_genres = top_anime.loc[top_anime.filtered==1]
    if st.button('Find anime'):
        if len(best_by_genres) == 0:
            st.markdown('Not Found')
        elif len(best_by_genres) < 10:
            anime_frontend(best_by_genres, show=len(best_by_genres))
        else:
            anime_frontend(best_by_genres)


# Recommendation Anime
with anime_tab3:
    st.header('Recommendation')

    st.markdown('Content-based anime recommendation system from your favorite anime')
    favorite_anime = st.selectbox('Select your favorite anime', anime['title (type)'])
    if st.button('Find anime recommnedation'):
        recommendation = anime.iloc[content_recommender(favorite_anime, anime=True)]
        anime_frontend(recommendation)


# Frontend Manga
manga_tab1, manga_tab2, manga_tab3 = tab_2.tabs(['Top Manga', 'Genre', 'Recommendation'])

def manga_frontend(recommendation):
    for i in range(10):
        with st.container():
            st.header(recommendation.iloc[i]['title'])
            col1, col2 = st.columns([2,6])
            with col1:
                st.image(recommendation.iloc[i]['main_picture'])
            with col2: 
                st.markdown(
f'''
Type : {recommendation.iloc[i]['type'].title()}\n
Volume : {recommendation.iloc[i]['volumes']}\n
Chapters : {recommendation.iloc[i]['chapters']}\n
Status : {recommendation.iloc[i]['status'].title()}\n
Published : {recommendation.iloc[i]['start_date']} to {recommendation.iloc[i]['end_date']} \n
Genre : {recommendation.iloc[i]['genres']}\n
Author : {recommendation.iloc[i]['authors']}\n
Score : {recommendation.iloc[i]['score_']}\n
'''
# Rank : {recommendation.iloc[i]['rank']}

)
            st.subheader('Synopsis')
            st.markdown(recommendation.iloc[i]['synopsis'])

            st.markdown('---')

# Top Manga
with manga_tab1:
    st.header('Top Rated Manga')
    manga_frontend(top_manga)

# Filter by genres - manga
with manga_tab2:
    st.header('Search manga by genre')
    selected_genres_manga = st.multiselect('Select your favorite manga genres', genres_of_manga)
    top_manga['filtered'] = top_manga.list_genres.apply(filter_manga)
    best_by_genres = top_manga.loc[top_manga.filtered==1]
    if st.button('Find manga'):
        if len(best_by_genres) == 0:
            st.markdown('Not Found')
        elif len(best_by_genres) < 10:
            manga_frontend(best_by_genres, show=len(best_by_genres))
        else:
            manga_frontend(best_by_genres)

# Recommendation Manga
with manga_tab3:
    st.header('Recommendation')

    st.markdown('Content-based manga recommendation system from your favorite manga')
    favorite_manga = st.selectbox('Select your favorite manga', manga['title (type)'])
    if st.button('Find manga recommnedation'):
        recommendation = manga.iloc[content_recommender(favorite_manga, anime=False)]
        manga_frontend(recommendation)


