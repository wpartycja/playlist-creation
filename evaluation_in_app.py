from basic_playlist import BasicPlaylist
from favourite_songs import FavouriteSongsPlaylist
from recommendation_model import RecommendationModel


def get_users_history_after(sessions_after_df, users_id):
    users_history_after = []
    for user_id in users_id:
        user_sessions_df = sessions_after_df.loc[
            sessions_after_df['user_id'] == user_id]

        for idx, row in user_sessions_df.iterrows():
            if row['event_type'] == 'play':
                users_history_after.append(row['track_id'])

    return users_history_after


def count_predicted(users_history_after, playlist):
    predicted = 0

    for track in playlist:
        if track in users_history_after:
            predicted += 1

    return predicted


def listenedto_artists_genres(sessions_before_df, tracks_df, artists_df, users_id):
    listened_artists = []
    listened_genres = []
    for user_id in users_id:
        user_artists = {}
        user_genres = {}
        user_sessions_df = sessions_before_df.loc[
            sessions_before_df['user_id'] == user_id]

        for se_idx, row in user_sessions_df.iterrows():
            if row['event_type'] == 'play':
                track_id = row['track_id']
                tracks = tracks_df.loc[
                    tracks_df['id'] == track_id]
                for tr_idx, track in tracks.iterrows():
                    artist_id = track['id_artist']

                    if artist_id not in user_artists:
                        user_artists[artist_id] = 0
                    user_artists[artist_id] += 1

                    artists = artists_df.loc[
                        artists_df['id'] == artist_id]
                    for ar_idx, artist in artists.iterrows():
                        genres = artist['genres']
                        for genre in genres:
                            if genre not in user_genres:
                                user_genres[genre] = 0
                            user_genres[genre] += 1

        for artist in user_artists.keys():
            if user_artists[artist] >= 5:
                listened_artists.append(artist)
        for genre in user_genres.keys():
            if user_genres[genre] >= 5:
                listened_genres.append(genre)

    return listened_artists, listened_genres


def count_artists_genres(listened_artists, listened_genres, tracks_df, artists_df, playlist):
    present_artists = []
    present_listened_artists = 0
    present_genres = []
    present_listened_genres = 0
    for track_id in playlist:
        tracks = tracks_df.loc[
            tracks_df['id'] == track_id]
        for tr_idx, track in tracks.iterrows():
            artist_id = track['id_artist']

            if artist_id not in present_artists:
                present_artists.append(artist_id)
                present_listened_artists += listened_artists.count(artist_id)

            artists = artists_df.loc[
                artists_df['id'] == artist_id]
            for ar_idx, artist in artists.iterrows():
                genres = artist['genres']
                for genre in genres:
                    if genre not in present_genres:
                        present_genres.append(genre)
                        present_listened_genres += listened_genres.count(genre)

    return len(present_artists), present_listened_artists, \
        len(present_genres), present_listened_genres


def evaluate(artists_df, tracks_df, sessions_df, users_df, users_id, playlist_duration):
    middle_date = sessions_df['timestamp'].median()

    sessions_before_df = sessions_df.loc[
        sessions_df['timestamp'] <= middle_date]
    sessions_after_df = sessions_df.loc[
        sessions_df['timestamp'] > middle_date]

    users_history_after = get_users_history_after(sessions_after_df, users_id)
    listened_artists, listened_genres = listenedto_artists_genres(sessions_before_df, tracks_df, artists_df, users_id)

    basic_playlist = BasicPlaylist(artists_df, sessions_before_df, tracks_df, users_df, users_id, playlist_duration)
    created_basic_playlist = basic_playlist.create_full_basic_playlist()
    basic_playlist_list = created_basic_playlist['id'].tolist()

    basic_predicted = count_predicted(users_history_after, basic_playlist_list)
    basic_percent = 100 * basic_predicted/len(basic_playlist_list)
    print(f'Basic: Correct predictions - {basic_predicted}/{len(basic_playlist_list)} -> {basic_percent:.2f}%')

    present_artists, present_listened_artists, \
        present_genres, present_listened_genres = count_artists_genres(listened_artists, listened_genres, tracks_df, artists_df, basic_playlist_list)
    artist_ind = present_listened_artists/present_artists
    genre_ind = present_listened_genres/present_genres
    print(f'Basic: Artist indicator: {present_listened_artists}/{present_artists} -> {artist_ind:.2f}')
    print(f'Basic: Genre indicator: {present_listened_genres}/{present_genres} -> {genre_ind:.2f}')

    fav_songs_playlist = FavouriteSongsPlaylist(artists_df, sessions_before_df ,tracks_df, users_df, users_id, playlist_duration)
    created_first_part_playlist = fav_songs_playlist.create_first_part_playlist()
    first_part_playlist_list = created_first_part_playlist['id'].tolist()

    model_playlist = RecommendationModel(first_part_playlist_list, tracks_df, playlist_duration)
    created_model_playlist = model_playlist.create_playlist()
    model_playlist_list = created_model_playlist['id'].tolist()

    model_predicted = count_predicted(users_history_after, model_playlist_list)
    model_percent = 100 * model_predicted/len(model_playlist_list)

    print(f'\nModel: Correct predictions - {model_predicted}/{len(model_playlist_list)} -> {model_percent:.2f}%')

    present_artists, present_listened_artists, \
        present_genres, present_listened_genres = count_artists_genres(listened_artists, listened_genres, tracks_df, artists_df, model_playlist_list)
    artist_ind = present_listened_artists/present_artists
    genre_ind = present_listened_genres/present_genres
    print(f'Model: Artist indicator: {present_listened_artists}/{present_artists} -> {artist_ind:.2f}')
    print(f'Model: Genre indicator: {present_listened_genres}/{present_genres} -> {genre_ind:.2f}\n\n')
