# Generated by Django 4.2.4 on 2023-09-09 10:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_alter_quotes_options_alter_rfplist_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={},
        ),
        migrations.AlterModelOptions(
            name='quotes',
            options={'ordering': ['vendor_price']},
        ),
        migrations.AlterModelOptions(
            name='rfplist',
            options={},
        ),
        migrations.AlterModelOptions(
            name='vendor',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.RemoveField(
            model_name='category',
            name='created_date',
        ),
        migrations.RemoveField(
            model_name='quotes',
            name='created_date',
        ),
        migrations.RemoveField(
            model_name='rfplist',
            name='created_date',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='category',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='created_date',
        ),
    ]