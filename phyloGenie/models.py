from django.db import models
from decimal import Decimal


# Create your models here.
from phyloGenie_backend import settings


class Dataset(models.Model):
    # dataset file
    data = models.FileField()
    size = models.IntegerField(default=0)
    seq_length = models.IntegerField(default=0)
    type = models.CharField(max_length=255, default='unknown')
    sim_score = models.DecimalField(max_digits=7, decimal_places=6, default=Decimal('0.000000'))
    tree = models.FileField(upload_to='trees', default='')

    def __str__(self):
        return self.data.name

    def save(self, *args, **kwargs):
        super(Dataset, self).save(*args, **kwargs)


class Recommendations(models.Model):
    results = models.CharField(max_length=255, default='null')

    def save(self, *args, **kwargs):
        super(Recommendations, self).save(*args, **kwargs)



