from django.db import models
from decimal import Decimal


class Activity(models.Model):
    id = models.BigIntegerField(primary_key=True)
    created_at = models.DateTimeField(null=True, blank=True)
    athlete_id = models.IntegerField(default=0)
    elapsed_time = models.IntegerField(null=True)
    name = models.CharField(max_length=255)
    sport_type = models.CharField(max_length=255, null=True, blank=True)
    total_elevation_gain = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    start_lat = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    start_lng = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    average_speed = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    average_cadence = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    distance = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    has_stream = models.IntegerField(default=1)

    def mile_dist(self):
        return self.distance * Decimal(0.000621371)  # Meters to miles
    
class Split(models.Model):
    created_at = models.DateTimeField(null=True, blank=True)
    activity_id = models.BigIntegerField()
    athlete_id = models.BigIntegerField()
    split_number = models.IntegerField()
    lat = models.DecimalField(max_digits=10, decimal_places=4)
    lng = models.DecimalField(max_digits=10, decimal_places=4)
    grade = models.DecimalField(max_digits=10, decimal_places=4)
    speed = models.DecimalField(max_digits=10, decimal_places=4)
    altitude = models.DecimalField(max_digits=10, decimal_places=4)
    hr = models.IntegerField()
    cadence = models.IntegerField()