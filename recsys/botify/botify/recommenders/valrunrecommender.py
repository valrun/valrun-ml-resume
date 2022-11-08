import random
from typing import List

from .recommender import Recommender
from .random import Random


class ValRunRecommender(Recommender):
    def __init__(self, tracks_redis, artists_redis, catalog, recommendations_redis_for_artist, recommendations_redis_for_users, top_tracks: List[int]):
        self.random = Random(tracks_redis)
        self.tracks_redis = tracks_redis
        self.artists_redis = artists_redis
        self.catalog = catalog
        self.recommendations_redis_for_artist = recommendations_redis_for_artist
        self.recommendations_redis_for_users = recommendations_redis_for_users
        self.top_tracks = top_tracks

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if prev_track_time >= 0.8:
            track_data = self.tracks_redis.get(prev_track)
            if track_data is not None:
                track = self.catalog.from_bytes(track_data)
            else:
                raise ValueError(f"Track not found: {prev_track}")

            artist_data = self.artists_redis.get(track.artist)
            if artist_data is not None:
                recommendations = self.recommendations_redis_for_artist.get(artist_data)
                if recommendations is not None:
                    shuffled = list(self.catalog.from_bytes(recommendations))
                    random.shuffle(shuffled)
                    return shuffled[0]
            else:
                raise ValueError(f"Artist not found: {prev_track}")

        recommendations = self.recommendations_redis_for_users.get(user)
        if recommendations is not None:
            shuffled = list(self.catalog.from_bytes(recommendations))
            random.shuffle(shuffled)
            return shuffled[0]
        if self.top_tracks:
            shuffled = list(self.top_tracks)[0:50]
            random.shuffle(shuffled)
            return shuffled[0]

        return self.random.recommend_next(user, prev_track, prev_track_time)


