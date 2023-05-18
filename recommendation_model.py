import pandas as pd
import random
import string
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationModel():
    def __init__(self, first_part_playlist: list,
                 tracks_df: pd.DataFrame, playlist_duration: tuple) -> None:
        self.first_part_playlist = first_part_playlist
        self.tracks_df = tracks_df
        self.normalized_df = self.get_normalized_df()
        hours, minutes = playlist_duration
        self.playlist_duration = hours*60*60 + minutes*60
        self.cosine = self.get_cosine()

    def count_duration(self, songs_list: list):
        """
        method counts duration of playlist
        :songs_list: list of the songs to count time
        :return: duration of all these songs
        """
        total_time = 0
        for song in songs_list:
            song_time = int(self.tracks_df.loc[
                self.tracks_df['id'] == song]['duration_sec'])
            total_time += song_time

        return total_time

    def get_feature_columns(self) -> list:
        """
        method get columns which need to be normalized
        :return: list of column names
        """
        col_to_remove = ['id', 'name', 'id_artist']
        feature_cols = self.tracks_df.columns.tolist()
        for col in col_to_remove:
            feature_cols.remove(col)
        return feature_cols

    def get_normalized_df(self) -> list:
        """
        method normalizes data in df
        :return: normalized df as list
        """
        feature_cols = self.get_feature_columns()
        scaler = MinMaxScaler()
        normalized_df = scaler.fit_transform(self.tracks_df[feature_cols])
        return normalized_df

    def get_cosine(self):
        """
        method caluclated cosine similarity
        :return: cosine similarity in given df
        """
        cosine = cosine_similarity(self.normalized_df)
        return cosine

    def song_recommendation(self, song_id: string, song_nr: int,
                            model_type: list) -> list:
        """
        method return recommendations to one given song
        :param song_id: id of the song to which we give recommendations
        :param song_nr: number of best recommmendations we want to obtain
        :param model_type: type of the model (here:cosine_similarity)
        :return: best n matches
        """
        indices = pd.Series(self.tracks_df.index, index=self.tracks_df['id'])
        # Get list of songs for given songs
        score = list(enumerate(model_type[indices[song_id]]))
        # Sort the most similar songs
        similarity_score = sorted(score, key=lambda x: x[1], reverse=True)
        # Select the top-10 recommend songs
        similarity_score = similarity_score[1:song_nr]
        top_songs_index = [i[0] for i in similarity_score]
        # Top 10 recommende songs
        top_songs = self.tracks_df['id'].iloc[top_songs_index]
        return top_songs

    def generate_recommendations(self, song_nr: int, model_type: list):
        """
        method generates recommendations to all given songs
        :param song_nr: number of best recommmendations we want to obtain
        :param model_type: type of the model (here:cosine_similarity)
        :return: list of recommended songs
        """
        recommended_songs = set()
        for song_id in self.first_part_playlist:
            recommended_songs = self.song_recommendation(
                song_id, song_nr, model_type)
            for song in recommended_songs:
                recommended_songs.add(song)
        return list(recommended_songs)

    def create_playlist(self) -> pd.DataFrame:
        """
        super complicated
        try to generate top 10 recommendations for every songs and join them
        if they too short it adds more recommendations
        if too long it subtracts the recommended songs
        :return: list with songs ids
        """
        recommendation_nr = 10

        recommended_songs = self.generate_recommendations(
            recommendation_nr, self.cosine)
        all_playlist = set(self.first_part_playlist + recommended_songs)
        all_playlist_duration = self.count_duration(all_playlist)

        adding = 0
        subtracting = 0

        while all_playlist_duration < self.playlist_duration - 600 or all_playlist_duration > self.playlist_duration + 600:
            if all_playlist_duration < self.playlist_duration:
                recommendation_nr += 1
                adding += 1
                recent_added = True
            else:
                recommendation_nr -= 1
                subtracting += 1
                recent_added = False

            recommended_songs = self.generate_recommendations(
                recommendation_nr, self.cosine)
            all_playlist = set(self.first_part_playlist + recommended_songs)

            all_playlist_duration = self.count_duration(all_playlist)

            if adding != 0 and subtracting != 0:
                if recent_added:

                    while all_playlist_duration > self.playlist_duration + 600:
                        recommended_songs.pop(
                            random.randrange(len(recommended_songs)))
                        all_playlist = set(
                            self.first_part_playlist + recommended_songs)

                        all_playlist_duration = self.count_duration(
                            all_playlist)

                else:
                    extra_recommended_songs = set(
                        self.generate_recommendations(
                            recommendation_nr + 1, self.cosine))

                    while all_playlist_duration < self.playlist_duration - 600:
                        extra_songs = list(extra_recommended_songs.difference(
                            set(self.first_part_playlist + recommended_songs)))

                        set(recommended_songs).add(random.choice(extra_songs))
                        all_playlist = set(
                            self.first_part_playlist + recommended_songs)

                        all_playlist_duration = self.count_duration(
                            all_playlist)

        return self.tracks_df.loc[self.tracks_df['id'].isin(all_playlist)]
