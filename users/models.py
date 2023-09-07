from django import forms
from django.db import models
from django.contrib.auth.models import User

class Quotes(models.Model):
    quotes_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=120)
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE)  
    vendor_price = models.FloatField()
    quantity = models.IntegerField()
    total_price = models.FloatField()

    class Meta:
        ordering = ['vendor_price']

    def __str__(self):
        return self.item_name

class Vendor(User):
    vendor_id = models.AutoField(primary_key=True)
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

class Category(models.Model):
    Category_id = models.AutoField(primary_key=True)
    c_name = models.CharField(max_length=100)
    c_status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')])  
    c_action = models.CharField(max_length=10, choices=[('approve', 'Approve'), ('reject', 'Reject')])  

class RFPList(models.Model):
    id = models.AutoField(primary_key=True)
    rfp_title = models.CharField(max_length=255)
    item_desc = models.TextField()
    last_date = models.DateField()
    min_amount = models.FloatField()
    max_amount = models.FloatField()
    vendors = models.ManyToManyField(Vendor)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, 
        choices=[('open', 'Open'), ('close', 'Close')],
        default='open'
        )  
    action = models.CharField(max_length=10, 
                              choices=[('open', 'Open'), ('close', 'Close')])  # Action field
