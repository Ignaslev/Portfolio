# Generated by Django 4.2.19 on 2025-02-18 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('burger_shop', '0002_alter_ingredient_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics'),
        ),
    ]
