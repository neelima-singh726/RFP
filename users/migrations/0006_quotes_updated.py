# Generated by Django 4.2.4 on 2023-09-18 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_quotes_admin_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotes',
            name='updated',
            field=models.BooleanField(default=False),
        ),
    ]