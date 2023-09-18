import random
from django import forms
from django.db import models
from django.utils import timezone

from rfp_project import settings  

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    c_name = models.CharField(
        max_length=100)
    c_status = models.CharField(
        max_length=10,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        default='active',  # Set a default status here if needed
    )
    created_date = models.DateTimeField(default=timezone.now)  # Add created_date field and set to the current date and time

    def __str__(self):
        return self.c_name

    class Meta:
        ordering = ['-created_date']

from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default = False)
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField( max_length=150, blank=True)

class Vendor(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    No_of_emp = models.IntegerField()
    gst_no = models.CharField(max_length=100)
    pan_no = models.CharField(max_length=20)
    phone_no = models.CharField(max_length=12)
    revenue = models.CharField(max_length=255)
    v_status = models.CharField(
        max_length=10, 
        choices=[('approve', 'Approve'), ('reject', 'Reject'),('pending','Pending')],
        default='pending' 
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_date']

class Admin(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_date']



class RFPList(models.Model):
    id = models.AutoField(primary_key=True)
    rfp_title = models.CharField(max_length=255)
    item_desc = models.TextField()
    last_date = models.DateField()
    min_amount = models.FloatField()
    max_amount = models.FloatField()
    vendors = models.ManyToManyField(Vendor, related_name='rfp_lists')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, 
        choices=[('open', 'Open'), ('close', 'Close')],
        default='open'
    )
    action = models.CharField(max_length=10, choices=[('open', 'Open'), ('close', 'Close')])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_rfps')
    created_date = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['-created_date']



class Quotes(models.Model):
    quotes_id = models.AutoField(primary_key=True)
    admin_comments = models.TextField(blank=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=120)
    item_desc = models.TextField()
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='quotes')
    vendor_price = models.FloatField()
    quantity = models.IntegerField()
    total_price = models.FloatField()
    rfp = models.ForeignKey(RFPList, on_delete=models.CASCADE, related_name='quotes')
    applied = models.BooleanField(default=False)
    updated = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.item_name