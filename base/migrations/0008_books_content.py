# Generated by Django 5.1.5 on 2025-01-21 22:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0007_books_image_books_image_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="books",
            name="content",
            field=models.TextField(blank=True, null=True),
        ),
    ]
