from django.db import models



# Create your models here.
class Dataset(models.Model):
    data = models.FileField(blank=False,null=False)
    def __str__(self):
        return self.data.name

class Recommendations(models.Model):
    algorithms = models.CharField(max_length=100000)

    def __str__(self):
        return self.algorithms.name

class PreprocessModel(models.Model):
    data_clean_time = models.CharField(max_length=100000)
    alignment_time = models.CharField(max_length=100000)

    def __str__(self):
        return self.data_clean_time.name
