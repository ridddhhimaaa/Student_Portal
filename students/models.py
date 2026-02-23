from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    marks = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    age = models.IntegerField(default=18)

    def __str__(self):
        return self.name

