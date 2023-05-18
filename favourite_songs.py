import pandas as pd

from playlist import Playlist


class FavouriteSongsPlaylist(Playlist):

    @staticmethod
    def scale_playings(row: pd.Series) -> int:
        """
        function scales playings (doubles
        or triples it due to nunmber of likes)
        :return: scaled playings
        """
        played = row['played']
        liked = row['liked']
        if not liked:
            return played
        elif liked >= 5:
            return played*3
        else:
            return played*2

    @staticmethod
    def add_dislikes(row: pd.Series) -> int:
        """
        funciton determines if song is disliked by user or not
        :return: 1 if it is disliked, 0 if not
        """
        return 0 if row['skipped'] <= row['played']*0.5 else 1

    # user history methods

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
                # [play, skip, like]
                user_history[track] = [0, 0, 0]
            if row['event_type'] == 'play':
                event = 0
            elif row['event_type'] == 'skip':
                event = 1
            elif row['event_type'] == 'like':
                event = 2

            user_history[track][event] += 1

        user_history = pd.DataFrame.from_dict(
            user_history, orient='index',
            columns=['played', 'skipped', 'liked'])

        user_history['dislike'] = user_history.apply(
            lambda row: self.add_dislikes(row), axis=1)

        user_history['played'] = user_history.apply(
            lambda row: self.scale_playings(row), axis=1)

        user_history.drop(columns=['skipped', 'liked'], inplace=True)

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

    # Methods to create first part playlist

    @staticmethod
    def get_disliked_songs(users_histories: list) -> list:
        """
        method finds disliked songs
        :param users_histories: tracks list of every user
        :return: list of disliked songs for every user
        """
        disliked_songs = set()
        for user_history in users_histories:
            for idx, row in user_history.iterrows():
                if row['dislike']:
                    disliked_songs.add(idx)

        return list(disliked_songs)

    def drop_disliked_songs(self, users_histories: list):
        """
        method drops disliked songs in all tracks
        which users know
        :param user_histories: list of dataframes with
        tracks history for every user
        :disliked_songs: list of all songs that are disliked
        by anyone above these users
        """
        disliked_songs = self.get_disliked_songs(users_histories)
        for user_history in users_histories:
            songs_to_drop = []
            for idx, row in user_history.iterrows():
                if idx in disliked_songs:
                    songs_to_drop.append(idx)

            user_history.drop(songs_to_drop, inplace=True)

    def get_user_favourites(self,
                            user_history: pd.DataFrame,
                            songs_per_user: int) -> list:
        """
        method finds favourite songs of particular user
        :param user_history: dataframe with list of all tracks
        listiened by user
        :return: list of ids of favourite songs
        """
        user_favourites = (
            user_history.sort_values('played', ascending=False)
            .head(songs_per_user)
            .index)
        return list(user_favourites)

    def all_users_favourites(self,
                             users_histories: list,
                             songs_per_user: int) -> set:
        """
        method finds favourite tracks for every user
        :param user_histories: list of dataframes with
        tracks history for every user
        :return: set of all users favourite songs
        """
        all_favourites = []
        for user_history in users_histories:
            user_favourites = self.get_user_favourites(
                user_history, songs_per_user)
            all_favourites.extend(user_favourites)

        return set(all_favourites)

    def create_playlist_user_history(self, songs_per_user: int) -> list:
        """
        method creates playlist based on users favourite songs
        and excluding disliked tracks
        :return: list of songs ids
        """
        users_histories = self.generate_users_histories()
        self.drop_disliked_songs(users_histories)
        basic_playlist = self.all_users_favourites(
            users_histories, songs_per_user)

        return basic_playlist
