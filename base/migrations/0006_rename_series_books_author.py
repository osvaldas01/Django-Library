# Generated by Django 5.1.5 on 2025-01-21 21:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0005_alter_books_options_books_description_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="books",
            old_name="series",
            new_name="author",
        ),
    ]
