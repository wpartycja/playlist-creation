import pandas as pd
from datetime import datetime

from basic_playlist import BasicPlaylist
from favourite_songs import FavouriteSongsPlaylist
from recommendation_model import RecommendationModel
from evaluation_in_app import evaluate


basic_playlists_path = './generated_playlists/basic_playlists/'
model_playlists_path = './generated_playlists/model_playlists/'


print('Loading data...')

artists_df = pd.read_json('./preprocessed_data/artists.json')
tracks_df = pd.read_json('./preprocessed_data/tracks.json')
users_df = pd.read_json('./preprocessed_data/users.json')
sessions_df = pd.read_json('./preprocessed_data/sessions.json')


def save_playlist_to_file(playlist, filepath):
    playlist.to_csv(filepath)


def get_basic_playlist(users_id, playlist_duration):
    basic_playlist = BasicPlaylist(
        artists_df, sessions_df, tracks_df, users_df,
        users_id, playlist_duration)
    created_basic_playlist = basic_playlist.create_full_basic_playlist()

    return created_basic_playlist


def get_model_playlist(users_id, playlist_duration):
    fav_songs_playlist = FavouriteSongsPlaylist(
        artists_df, sessions_df, tracks_df, users_df,
        users_id, playlist_duration)
    created_first_part_playlist = fav_songs_playlist \
        .create_first_part_playlist()
    first_part_playlist_list = created_first_part_playlist['id'].tolist()

    model_playlist = RecommendationModel(
        first_part_playlist_list, tracks_df, playlist_duration)
    created_model_playlist = model_playlist.create_playlist()

    return created_model_playlist


def eval(users_id, playlist_duration):
    print('\nKalkulowanie...\n')
    evaluate(artists_df, tracks_df, sessions_df, users_df, users_id, playlist_duration)


def choice_screen():
    print('\nCo chciałbyś zrobić?\n \
    1 - Utwórz playlistę\n \
    2 - Porównaj modele\n \
    x - Zakończ pracę')

    action = input('Wybór: ')

    if action in ['1', '2']:
        while (True):
            users = input("\nPodaj skład grupy [ID użytkowników po spacji] (2-9 użytkowników): ")
            users_id = list(map(int, users.split()))
            if len(users_id) >= 2 and len(users_id) <= 9:
                if len(users_df.loc[users_df['user_id'].isin(users_id)]) == len(users_id):
                    break

        while (True):
            dur = input("\nPodaj długość playlisty [liczba_godzin liczba_minut] (minimalnie 1h, maksymalnie 9h): ")
            duration = dur.split()
            if len(duration) == 2:
                if duration[0].isdigit() and duration[1].isdigit():
                    hours = int(duration[0])
                    minutes = int(duration[1])
                    if hours >= 1 and hours <= 9 and minutes >= 0 and minutes < 60:
                        break

        if action == '1':
            print('\nJaka playlista?\n \
    1 - Playlista Basic\n \
    2 - Playlista Plus (ze specjalnymi rekomendacjami dla Was!)\n \
    x - Anuluj')

            playlist_action = input('Wybór: ')

            if playlist_action in ['1', '2']:
                if playlist_action == '1':  # Basic playlist
                    playlist = get_basic_playlist(users_id, (hours, minutes))
                    filepath = basic_playlists_path
                elif playlist_action == '2':  # Playlist from recommendation model
                    playlist = get_model_playlist(users_id, (hours, minutes))
                    filepath = model_playlists_path

                print('\nWasza spersonalizowana playlista:')
                print(playlist['name'])
                filepath += '' + str(datetime.now().timestamp())
                filepath += '-' + users.replace(' ', '_') + '.csv'
                print(f'\nZapisywanie playlisty do {filepath}')
                save_playlist_to_file(playlist, filepath)
                print('Zapisano!\n')

        elif action == '2':
            eval(users_id, (hours, minutes))

        choice_screen()

    elif action == 'x':
        print('\nDo zobaczenia!\n')
        return
    else:
        print('\nNie ma takiej opcji do wyboru. Proszę wybrać coś z listy')
        choice_screen()


if __name__ == '__main__':
    print('\nWitamy w playlistach dla grup Pozytywki!')
    choice_screen()
