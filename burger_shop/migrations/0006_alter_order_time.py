# Generated by Django 4.2.19 on 2025-02-18 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('burger_shop', '0005_remove_orderitem_image_menuitem_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
