import pandas as pd
import random

from abc import ABC, abstractmethod


class Playlist(ABC):
    def __init__(self, artists_df: pd.DataFrame, sesisons_df: pd.DataFrame,
                 tracks_df: pd.DataFrame, users_df: pd.DataFrame,
                 users_id: list, playlist_duration: tuple):
        self.artists_df = artists_df
        self.sessions_df = sesisons_df
        self.tracks_df = tracks_df
        self.users_df = users_df
        self.users_id = users_id
        hours, minutes = playlist_duration
        self.playlist_duration = hours*60*60 + minutes*60
        self.median_song_duration = tracks_df['duration_sec'].median()
        self.time_per_user = self.calculate_time_per_user()

# Time methods

    def calculate_time_per_user(self) -> int:
        """
        method calculates durations of songs per user
        :return: time of songs of every user
        """
        fav_songs_duration = self.playlist_duration * 0.6
        time_per_user = fav_songs_duration/len(self.users_id)
        return time_per_user

    def calculate_songs_per_user(self, correction) -> int:
        """
        method calculates number of songs for every user
        :return: number of songs for every user
        """
        return int(
            self.time_per_user//self.median_song_duration + 4 + correction)

# Create dataframes with users tracks history

    @abstractmethod
    def create_playlist_user_history(self, songs_per_user: int) -> list:
        """
        method creates playlist based on users history
        :return: list of songs ids
        """
        pass

# Checking time and adding more songs if that's needed or dropping

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

    def create_first_part_playlist(self) -> pd.DataFrame:
        """
        super complicated
        at first: tries to by add the same amount of song fore very user and
        checks if the time is between 50%-70% of all playlist time
        if it cannot be done: pops random songs from too long playlist
        or adds random songs most liked by all users
        """
        songs_per_user = self.calculate_songs_per_user(0)
        basic_playlist = self.create_playlist_user_history(songs_per_user)

        perfect_duration = self.playlist_duration * 0.6
        basic_playlist_duration = self.count_duration(basic_playlist)

        correction = 0
        adding = 0
        subtracting = 0

        while basic_playlist_duration > perfect_duration * 1.1 or basic_playlist_duration < perfect_duration * 0.9:
            if basic_playlist_duration < perfect_duration:
                correction += 1
                adding += 1
                recent_added = True
            else:
                correction -= 1
                subtracting += 1
                recent_added = False

            songs_per_user = self.calculate_songs_per_user(correction)
            basic_playlist = self.create_playlist_user_history(songs_per_user)

            basic_playlist_duration = self.count_duration(basic_playlist)

            if adding != 0 and subtracting != 0:
                if recent_added:

                    while basic_playlist_duration > perfect_duration * 1.1:
                        basic_playlist.pop()
                        basic_playlist_duration = self.count_duration(
                            basic_playlist)
                else:
                    extra_playlist = []

                    while basic_playlist_duration < perfect_duration * 0.9:
                        while (len(extra_playlist) == 0):
                            extra_playlist = set(
                                self.create_playlist_user_history(
                                    songs_per_user+1))
                            basic_playlist = set(basic_playlist)
                            extra_songs = list(extra_playlist.difference(
                                basic_playlist))

                        basic_playlist.add(random.choice(extra_songs))

                        basic_playlist_duration = self.count_duration(
                            basic_playlist)

        return self.tracks_df.loc[self.tracks_df['id'].isin(basic_playlist)]
