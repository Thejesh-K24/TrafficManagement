from django.db import models

# Create your models here.
from django.db import models

class UserData(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Consider hashing the password

    def __str__(self):
        return self.name


class TrafficData(models.Model):
    junction_id = models.CharField(max_length=100, unique=True)
    number_of_vehicles = models.IntegerField()

    def get_green_light_duration(self):
        """Returns green light duration based on the number of vehicles."""
        if self.number_of_vehicles < 10:
            return 10
        elif 10 <= self.number_of_vehicles <= 30:
            return 30
        else:
            return 60


    def __str__(self):
        return f"Junction {self.junction_id}: {self.number_of_vehicles} vehicles"
