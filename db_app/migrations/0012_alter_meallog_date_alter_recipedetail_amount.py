# Generated by Django 4.2 on 2023-06-18 13:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db_app', '0011_alter_meallog_date_alter_recipedetail_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meallog',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 6, 18, 13, 35, 11, 621027, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='recipedetail',
            name='amount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
