import pandas as pd
import random

from playlist import Playlist


class BasicPlaylist(Playlist):

    # Create dataframes with users tracks history

    def create_user_history(self, user_id: int) -> pd.DataFrame:
        """
        method creates new dataframe with tracks listened by specific user
        :user_id: id of the user
        :return: dataframe with history of tracks listened by user
        """
        user_session_df = self.sessions_df.loc[
            self.sessions_df['user_id'] == user_id]

        user_history = dict()

        for idx, row in user_session_df.iterrows():
            track = row['track_id']
            if track not in user_history:
                user_history[track] = 0
            if row['event_type'] == 'play':
                user_history[track] += 1

        user_history = pd.DataFrame.from_dict(
            user_history, orient='index')

        return user_history

    def generate_users_histories(self) -> list:
        """
        method generates list of dataframes which contains
        all tracks listened by specified users
        :return: list of track history of every user
        """
        users_histories = []
        for user_id in self.users_id:
            users_histories.append(self.create_user_history(user_id))
        return users_histories

    # Create playlist

    def create_playlist_user_history(self, songs_per_user: int) -> list:
        """
        method creates playlist based on users favourite songs
        and excluding disliked tracks
        :return: list of songs ids
        """
        users_histories = self.generate_users_histories()
        basic_playlist = []
        for user_history in users_histories:
            basic_playlist.extend(list(
                user_history
                .sample(n=songs_per_user, replace=True)
                .index))

        return basic_playlist

    def create_full_basic_playlist(self) -> pd.DataFrame:
        basic_playlist_df = self.create_first_part_playlist()
        basic_playlist = basic_playlist_df['id'].tolist()
        duration = self.count_duration(basic_playlist)

        remaining_time = self.playlist_duration - duration
        remaining_songs_estimate = remaining_time / self.median_song_duration

        basic_playlist.extend(list(
            self.tracks_df
            .sample(n=int(remaining_songs_estimate), replace=True)
            ['id']))

        duration = self.count_duration(basic_playlist)

        while duration > self.playlist_duration + 300 or duration < self.playlist_duration - 300:
            if duration > self.playlist_duration + 300:
                basic_playlist.pop(
                    random.randrange(len(basic_playlist)))
            else:
                basic_playlist.extend(list(
                    self.tracks_df
                    .sample(n=1, replace=True)
                    ['id']))
            duration = self.count_duration(basic_playlist)

        return self.tracks_df.loc[self.tracks_df['id'].isin(basic_playlist)]
