# Generated by Django 2.0.2 on 2018-03-07 10:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('okr', '0007_auto_20180306_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalkeyresult',
            name='complete_percentage',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='globalkeyresult',
            name='incomplete_percentage',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='globalkeyresult',
            name='null_percentage',
            field=models.FloatField(default=0),
        ),
    ]
