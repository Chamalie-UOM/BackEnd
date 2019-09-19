# Generated by Django 2.2.4 on 2019-09-11 11:12

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phyloGenie', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreprocessModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_clean_time', models.CharField(max_length=100)),
                ('alignment_time', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Recommendations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('results', models.CharField(default='null', max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='dataset',
            name='seq_length',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dataset',
            name='sim_score',
            field=models.DecimalField(decimal_places=3, default=Decimal('0.000'), max_digits=5),
        ),
        migrations.AddField(
            model_name='dataset',
            name='size',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dataset',
            name='type',
            field=models.CharField(default='unknown', max_length=255),
        ),
    ]
