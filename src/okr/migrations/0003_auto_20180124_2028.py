# Generated by Django 2.0.1 on 2018-01-24 20:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('okr', '0002_auto_20180117_1255'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                (
                    'manager',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='okr.Team')),
            ],
        ),
        migrations.AlterField(
            model_name='globalkeyresult',
            name='key_result',
            field=models.TextField(verbose_name='Key Result'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='coin_value',
            field=models.IntegerField(default=0, verbose_name='Reward'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='story_points',
            field=models.IntegerField(default=0, verbose_name='Story Points'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='tmp_status',
            field=models.BooleanField(default=True, verbose_name='Temporary'),
        ),
        migrations.AlterField(
            model_name='objective',
            name='global_key_result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='okr',
                                    to='okr.GlobalKeyResult', verbose_name='Global Key Result'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='rights',
            field=models.IntegerField(default=0, verbose_name='Character Rights'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='xp',
            field=models.IntegerField(default=0, verbose_name='Experience'),
        ),
        migrations.AlterField(
            model_name='quarter',
            name='end_date',
            field=models.DateField(verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='quarter',
            name='start_date',
            field=models.DateField(verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='result',
            name='jira_issues',
            field=models.ManyToManyField(blank=True, to='okr.Issue', verbose_name='JIRA Issues'),
        ),
        migrations.AlterField(
            model_name='result',
            name='manual_bar',
            field=models.BooleanField(default=False, verbose_name='Manual Bar'),
        ),
    ]
