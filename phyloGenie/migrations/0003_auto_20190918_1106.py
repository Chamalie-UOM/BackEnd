# Generated by Django 2.2.4 on 2019-09-18 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phyloGenie', '0002_auto_20190911_1112'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PreprocessModel',
        ),
        migrations.AlterField(
            model_name='dataset',
            name='data',
            field=models.FileField(upload_to='media'),
        ),
    ]