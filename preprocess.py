from sklearn.preprocessing import MultiLabelBinarizer

import pandas as pd
import string


class Preprocess:
    def __init__(self, path_to_artists, path_to_sessions,
                 path_to_tracks, path_to_users):
        self.artists_df = pd.read_json(path_to_artists, lines=True)
        self.session_df = pd.read_json(path_to_sessions, lines=True)
        self.tracks_df = pd.read_json(path_to_tracks, lines=True)
        self.users_df = pd.read_json(path_to_users, lines=True)

# Genres preprocessing

    @staticmethod
    def __simplify_genres(row: pd.Series, column_name: string) -> list:
        """
        function simplifies genres by joining the many music styles to one
        like pop dance, canadian pop -> pop
        :param row: row from dataframe
        :column_name: name of the column
        "return: list of simplified genres
        """
        new_genres = set()
        for genre in row[column_name]:
            if genre == 'pop rock' or genre == 'hard rock':
                new_genres.add(genre)
            elif 'alternative' in genre:
                new_genres.add('alternative')
            elif 'bollywood' in genre:
                new_genres.add('bollywood')
            elif 'country' in genre:
                new_genres.add('country')
            elif 'dancehall' in genre:
                new_genres.add('dancehall')
            elif 'disco' in genre:
                new_genres.add('disco')
            elif 'electro' in genre:
                new_genres.add('electro')
            elif 'electropop' in genre:
                new_genres.add('electro')
            elif 'edm' in genre:
                new_genres.add('edm')
            elif 'folk' in genre:
                new_genres.add('folk')
            elif 'hip hop' in genre:
                new_genres.add('hip hop')
            elif 'house' in genre:
                new_genres.add('house')
            elif 'indie' in genre:
                new_genres.add('indie')
            elif 'jazz' in genre:
                new_genres.add('jazz')
            elif 'k-pop' in genre:
                new_genres.add('k-pop')
            elif 'latin' in genre:
                new_genres.add('latin')
            elif 'metal' in genre:
                new_genres.add('metal')
            elif 'orchestra' in genre:
                new_genres.add('orchestra')
            elif 'pop' in genre:
                new_genres.add('pop')
            elif 'rap' in genre:
                new_genres.add('rap')
            elif 'rock' in genre:
                new_genres.add('rock')
            elif 'reggaeton' in genre:
                new_genres.add('reggaeton')
            elif 'r&b' in genre:
                new_genres.add('r&b')
            elif 'soul' in genre:
                new_genres.add('soul')
            elif 'trap' in genre:
                new_genres.add('trap')
            elif 'funk' in genre:
                new_genres.add('funk')
            elif 'dance' in genre:
                new_genres.add('dance')
            else:
                new_genres.add(genre)

        return list(new_genres)

    def preprocess_genres(self) -> None:
        """
        funciton applies simplify genres on dataframes
        """

        self.artists_df['genres'] = self.artists_df.apply(
            lambda row: self.__simplify_genres(row, 'genres'), axis=1)
        self.users_df['favourite_genres'] = self.users_df.apply(
            lambda row: self.__simplify_genres(
                row, 'favourite_genres'), axis=1)

# Session preprocessing

    def preprocess_sessions(self) -> None:
        """
        function performs basic preprocess for sessions
        * drops rows where track_id is null
        * drops sessions where event type is 'advertisment'
        """
        self.session_df.dropna()
        self.session_df.drop(
            self.session_df[self.session_df['event_type'] == 'advertisment']
            .index, inplace=True)

# Tracks preprocessing

    @staticmethod
    def change_time_to_sec(row: pd.Series) -> int:
        """
        function changes time representaiton from miliseconds to seconds
        :param row: row from dataframe
        :return: time represented in seconds
        """
        return row['duration_ms']//1000

    def add_genres(self, row: pd.Series) -> list:
        """
        function finds genres of the songs by genres of an artist
        :param row: row from dataframe
        :return: list of genres of the song
        """
        genres = self.artists_df.loc[self.artists_df['id'] == row['id_artist']]['genres']
        return genres.tolist()[0]

    def one_hot_genres(self) -> None:
        """
        method performs one-hot encoding on genres
        """
        mlb = MultiLabelBinarizer(sparse_output=True)

        self.tracks_df = self.tracks_df.join(
                pd.DataFrame.sparse.from_spmatrix(
                    mlb.fit_transform(self.tracks_df.pop('genres')),
                    index=self.tracks_df.index,
                    columns=mlb.classes_))

    def preprocess_tracks(self) -> None:
        """
        function performs full tracks preproccessing:
        *changes time representation
        *adds genres in one-hot encoding
        *unifies date represenation
        """
        self.tracks_df['duration_ms'] = self.tracks_df.apply(
            lambda row: self.change_time_to_sec(row), axis=1)
        self.tracks_df.rename(
            columns={'duration_ms': 'duration_sec'}, inplace=True)
        self.tracks_df['genres'] = self.tracks_df.apply(
            lambda row: self.add_genres(row), axis=1)
        self.tracks_df['release_date'] = pd.to_datetime(
            self.tracks_df['release_date']).dt.year
        self.one_hot_genres()

# General final methods

    def save_dfs_to_json(self):
        """
        method saves all dataframes to json file
        """
        path = './preprocessed_data/'
        self.tracks_df.to_json(path+'tracks.json')
        self.session_df.to_json(path+'sessions.json')
        self.artists_df.to_json(path+'artists.json')
        self.users_df.to_json(path+'users.json')

    def preprocess(self):
        """
        main method that preprocess all dataframes and 
        saves them to json files
        """
        self.preprocess_genres()
        self.preprocess_sessions()
        self.preprocess_tracks()
        self.save_dfs_to_json()