import spotipy
import spotipy.util as util
import argparse
import pandas as pd
import numpy as np

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from spotipy.oauth2 import SpotifyClientCredentials

#%%

client_id = '' #insert your AP client ID

client_secret = '' #insert your AP client Secret

username = '' #insert your user unique ID

playlist_new = 'New Releases ' #playlist name

redirect_uri = 'https://www.google.com.br/' # redirection URI

client_credentials_manager = SpotifyClientCredentials(client_id= client_id, client_secret = client_secret)

scope = 'playlist-read-private playlist-modify-private playlist-modify-public user-top-read'

try:
    
    token = util.prompt_for_user_token(username,scope,client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
    
    sp = spotipy.Spotify(auth = token)
    
except:

    print('Token not acessible for ' + username)

#%%

def get_playlist_id(username,playlist_name,sp):
    lists = get_user_playlist(username,sp)
    for playlist in lists:
        if playlist['name'] == playlist_name:
            p_id = playlist['id']
    return p_id

def get_playlists_audio_features(username, playlists, sp, playlist_new):
    
    delete = []
    for i in range(len( playlists)):
        name = playlists[i]['name']
        if name ==  playlist_new:    
            delete.append(i)
    
    delete.sort(reverse = True)
    
    for d in delete:
        del playlists[d]
    
    
    df = pd.DataFrame( columns=['energy', 'liveness',
                                              'tempo', 'speechiness',
                                              'acousticness', 'instrumentalness',
                                              'time_signature', 'danceability',
                                              'key', 'duration_ms', 'loudness',
                                              'valence', 'popularity', 'mode','id'])
    
    for p in playlists:
         dt = get_playlist_audio_features(username, p['id'], sp)
         df = pd.concat([df,dt])
         print(len(df))
     
    name = sp.user(username)
    name= name['display_name']   
    df.to_csv('{}-Playlists_Audio_Features.csv'.format(name), index=False)
    return df

def get_playlist_audio_features(username, playlist_name, sp):
    offset = 0
    songs = []
    ids = []
    playlist_id = playlist_name
    while True:
        content = sp.user_playlist_tracks(username, playlist_id, fields=None, limit=100, offset=offset, market=None)
        songs += content['items']
        if content['next'] is not None:
            offset += 100
        else:
            break

    for i in songs:
        if i['track'] is not None:
            if i['track']['id'] is not None:
                ids.append(i['track']['id'])

    index = 0
    audio_features = []
    while index < len(ids):
        audio_features += sp.audio_features(ids[index:index + 50])
        index += 50

    features_list = []
    for features in audio_features:
        if features is not None:
            popularity = sp.track(features['id'])['popularity']
            features_list.append([features['energy'], features['liveness'],
                                  features['tempo'], features['speechiness'],
                                  features['acousticness'], features['instrumentalness'],
                                  features['time_signature'], features['danceability'],
                                  features['key'], features['duration_ms'],
                                  features['loudness'], features['valence'],popularity,
                                  features['mode'],
                                  features['id']])

    df = pd.DataFrame(features_list, columns=['energy', 'liveness',
                                              'tempo', 'speechiness',
                                              'acousticness', 'instrumentalness',
                                              'time_signature', 'danceability',
                                              'key', 'duration_ms', 'loudness',
                                              'valence', 'popularity', 'mode','id'])
    
    return df

def get_user_playlist(username, sp):
    playlists = sp.user_playlists(username,limit=None)
    plist = playlists['items']
    #'''
    # In case you want to get the playlist created by the user himself
    delete = []
    for i in range(len( plist)):
        owner = plist[i]['owner']['id']
        if owner != username:   
            delete.append(i)
    
    delete.sort(reverse = True)
    
    for d in delete:
        del plist[d]
    #'''
    for playlist in plist:
        print("Name: {}, Number of songs: {}, Playlist ID: {} \n".
                  format(playlist['name'],
                         playlist['tracks']['total'],
                         playlist['id']))        
    return plist

def get_new_releases_audio_features(country, sp):
    offset = 0
    albums = []
    albums_id = []
    songs = []
    ids = []
    while True:
        content = sp.new_releases(country = country, offset = offset)
        albums += content['albums']['items']
        if content['albums']['next'] is not None:
            offset += 20
        else:
            break

    for i in albums:
        albums_id.append( i['id'])
        
    offset = 0    
    for j in albums_id:
        
        while True:
            song = sp.album_tracks(album_id = j, offset = offset)
            songs += song['items']
            if song['next'] is not None:
                offset += 50
            else:
                    break
    for k in songs:
        ids.append(k['id'])

    index = 0
    audio_features = []
    while index < len(ids):
        audio_features += sp.audio_features(ids[index:index + 50])
        index += 50

    features_list = []
    for features in audio_features:
        if features is not None:
            popularity = sp.track(features['id'])['popularity']
            features_list.append([features['energy'], features['liveness'],
                                  features['tempo'], features['speechiness'],
                                  features['acousticness'], features['instrumentalness'],
                                  features['time_signature'], features['danceability'],
                                  features['key'], features['duration_ms'],
                                  features['loudness'], features['valence'],popularity,
                                  features['mode'],
                                  features['id']])

    df = pd.DataFrame(features_list, columns=['energy', 'liveness',
                                              'tempo', 'speechiness',
                                              'acousticness', 'instrumentalness',
                                              'time_signature', 'danceability',
                                              'key', 'duration_ms', 'loudness',
                                              'valence','popularity', 'mode', 'id'])
    df.to_csv('Spotify_New_Releases.csv', index=False)
    return df

def get_elected_tracks(X, Releases):
    
    Y = X.drop(columns = ['id'])
    Y = StandardScaler().fit_transform(Y)
    
    # Compute DBSCAN
    b_point = len(X)/3
    l_noise = {}
    e = 0.01
    while e<=5:    
        db = DBSCAN(eps=e, min_samples=5).fit(Y)
        label = db.labels_
        #n_clusters_ = len(set(label)) - (1 if -1 in labels else 0)
        n_noise_ = list(label).count(-1)
        l_noise[n_noise_] = e 
        if b_point == n_noise_:
            break
        e +=0.01
        
    ep = min(l_noise, key=lambda x:abs(x-b_point))
    ep = l_noise[ep]
    db = DBSCAN(eps=ep, min_samples=5).fit(Y)
    
    
    X['labels'] = db.labels_
    
    X.to_csv('Labeled.csv', index=False)
    
    X_f = X.drop(columns = ['id','labels'])
    X_t = X['labels']
    
    
    Releases_f = Releases.drop(columns = ['id'])
    
    sing = DecisionTreeClassifier(random_state=1)
    sing.fit(X_f,X_t)
    prediction = sing.predict(Releases_f)
    
    releases_ids = Releases['id']
    releases_pop = Releases['popularity']
    music_ids_possibles = []
    
    
    for songs in range(len(releases_ids )):
        if prediction[songs] != -1:
            music_ids_possibles.append([releases_ids[songs],releases_pop[songs]])
            
    df = pd.DataFrame(music_ids_possibles, columns=['id','popularity' ])
    df = df.sort_values(by=['popularity'],ascending= False)
    df.to_csv('Spotify_New_Releases_Favs.csv', index=False)
    return df

def add_tracks_new_release(username,play_list, playlist_name, sp,new_releases,popularity_cut):
    
    playlist_id = 0
    
    for playlist in play_list:
        if playlist['name'] == playlist_name:
            playlist_id = playlist['id']
            
    if playlist_id == 0 : 
        sp.user_playlist_create(username, playlist_name, public=True, description='Playlist de descobertas feita pelo Mega')
        playlist_id =  get_playlist_id(username,playlist_name,sp)

    print(playlist_id)        
    new_releases =  new_releases.loc[new_releases['popularity'] >= popularity_cut]   
    new_tracks = new_releases['id']
    index =0
    sp.user_playlist_replace_tracks(username, playlist_id, tracks=new_tracks[index:index + 100])
    index += 100
    while index < len(new_tracks):
        sp.user_playlist_add_tracks(username,playlist_id,tracks=new_tracks[index:index + 100])
        index += 100

def main(username):
    print( "Getting user playlist \n")
    lista = get_user_playlist(username, sp)
    lista2 = get_user_playlist(username, sp)
    print( "Getting playlist audio features \n")
    Audio_fp  = get_playlists_audio_features(username, lista, sp, playlist_new)
    print( "Getting new releases audio features \n")
    Audio_fn  =get_new_releases_audio_features('BR', sp)
    print( "Building new playlist")
    elected_songs = get_elected_tracks(Audio_fp,Audio_fn)
    popularity = 28  # popularity pass value
    add_tracks_new_release(username,lista2,playlist_new,sp, elected_songs, popularity)

if __name__ == '__main__':
    print( 'Starting... \n')
    parser = argparse.ArgumentParser(description='description')
    main(username)
