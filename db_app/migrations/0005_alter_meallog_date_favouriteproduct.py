# Generated by Django 4.2 on 2023-05-08 16:46

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_alter_profile_activity_level_alter_profile_gender'),
        ('db_app', '0004_recipedetail_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meallog',
            name='date',
            field=models.DateField(default=datetime.date(2023, 5, 8)),
        ),
        migrations.CreateModel(
            name='FavouriteProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db_app.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.profile')),
            ],
        ),
    ]
