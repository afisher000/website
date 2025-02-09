from django.db import models

class Track(models.Model):
    url = models.URLField(max_length=200)  # URL field for the track
    artist = models.CharField(max_length=255)  # Artist name
    name = models.CharField(max_length=255)  # Track name
    downloaded = models.BooleanField(default=False)  # Field to indicate whether the track was downloaded

    def __str__(self):
        return f"{self.name} by {self.artist}"