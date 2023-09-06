# Generated by Django 4.2.4 on 2023-09-05 08:13

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0013_auto_20230901_2008'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('Category_id', models.AutoField(primary_key=True, serialize=False)),
                ('c_name', models.CharField(max_length=100)),
                ('c_status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], max_length=10)),
                ('c_action', models.CharField(choices=[('approve', 'Approve'), ('reject', 'Reject')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='RFPList',
            fields=[
                ('rfplist_id', models.AutoField(primary_key=True, serialize=False)),
                ('rfp_title', models.CharField(max_length=255)),
                ('last_date', models.DateField()),
                ('min_amount', models.FloatField()),
                ('max_amount', models.FloatField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], max_length=10)),
                ('action', models.CharField(choices=[('approve', 'Approve'), ('reject', 'Reject')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to=settings.AUTH_USER_MODEL)),
                ('vendor_id', models.AutoField(primary_key=True, serialize=False)),
                ('No_of_emp', models.IntegerField()),
                ('gst_no', models.CharField(max_length=100)),
                ('pan_no', models.CharField(max_length=20)),
                ('phone_no', models.CharField(max_length=12)),
                ('revenue', models.CharField(max_length=255)),
                ('v_status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], max_length=10)),
                ('v_action', models.CharField(choices=[('approve', 'Approve'), ('reject', 'Reject')], max_length=10)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Quotes',
            fields=[
                ('quotes_id', models.AutoField(primary_key=True, serialize=False)),
                ('item_name', models.CharField(max_length=120)),
                ('vendor_price', models.FloatField()),
                ('quantity', models.IntegerField()),
                ('total_price', models.FloatField()),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.vendor')),
            ],
            options={
                'ordering': ['vendor_price'],
            },
        ),
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin_vendor', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
