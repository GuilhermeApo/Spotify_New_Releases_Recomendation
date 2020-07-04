# Spotify_New_Releases_Selection


## Overview
This repo contains the scripts used in my latest experiment titled New releases Selection ( Recomendation).  A data analysis involving music, data, and machine learning. 
This experiment, which used Spotify's audio features API ( Spotipy), creates a New Releases playlist with recently released tracks on spotify that you may like based on your 
playlists. It first get audio features from your followed+owned ( or just owned) playlist and audio features from new album releases featured in Spotify for your region ( or a region of interest). Later your playlist gathered data is used to train a DBSCAN clustering algorithm that will group your music into music clusters. However the eps feature will be searched to let at least ( or the closets possible to it) one third of your tracks to be labeled as noise in the DBSCAN clustreing algorithm. This is done so you now have clusters of music that you like and are similar and a region of musics you may not like. Then the labeled audio features playlist is used to train Decision Tree Classifier. The Decision Tree Classifier is then used to predict the possible labels of the new algum releases gathered data. Tracks that were not predicted as noise are selected to a Favorite new releases list. This favorite new releases list is then narrowed by a popularity filter ( only musics with a popularity grather or equal than the desires popularity pass value) are selected and then added to your New Releases ( name as you wish) playlist.

## Tools used

* Python
* [Spotify API](https://developer.spotify.com)
* [Spotipy Python library](https://spotipy.readthedocs.io/en/2.13.0/)
* [Scikit-learn] (https://scikit-learn.org/stable/)

## Spotify API - Getting CLIENT_ID and CLIENT_SECRET
To get access to the Spotify API you are going to Sign up on [Spotify Developers site](https://developer.spotify.com/dashboard/) . Afeter that you have to select the option “Create an App”, fill the fields required and after that you are going to have a CLIENT_ID and CLIENT_SECRET for your application. Do not forget to after creating your APP insert the website e Redirect URIs. I´ve used google (https://www.google.com.br/).
