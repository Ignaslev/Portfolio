# Generated by Django 4.2.19 on 2025-02-25 07:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('burger_shop', '0014_nutrition_ingredient_nutrition_menuitem_nutrition'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='nutrition',
        ),
        migrations.RemoveField(
            model_name='menuitem',
            name='nutrition',
        ),
        migrations.AddField(
            model_name='nutrition',
            name='ingredient',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nutrition', to='burger_shop.ingredient'),
        ),
        migrations.AddField(
            model_name='nutrition',
            name='menu_item',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nutrition', to='burger_shop.menuitem'),
        ),
    ]
