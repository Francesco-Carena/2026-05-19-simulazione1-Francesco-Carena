from dataclasses import dataclass


@dataclass
class Artist:
    ArtistId: int
    Name: str
    popularity: int =0

    def __hash__(self):
        return hash(self.ArtistId)
    def __str__(self):
        return self.Name