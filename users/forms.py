from datetime import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User

from users.models import Category, Quotes, RFPList, Vendor
from django.db import transaction


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
     is_admin = forms.BooleanField(initial=True, widget=forms.HiddenInput, required=False)

     class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

     def save(self, commit=True):
        # Save the user instance created by UserCreationForm
        user = super().save(commit=False)
        user.is_admin = True  # Set the user as an admin

        if commit:
            user.save()

        return user








class RegisterFormVendor(UserCreationForm):
    No_of_emp = forms.IntegerField()
    gst_no = forms.CharField(max_length=100)
    phone_no = forms.CharField(max_length=12)
    revenue = forms.CharField(max_length=255)
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(c_status='active'),  # Filter for active categories
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
    )
    class Meta(UserCreationForm.Meta):
        model = User  # Set the model to User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'revenue', 'No_of_emp', 'gst_no', 'phone_no', 'category']

    @transaction.atomic
    def save(self, commit=True):
        # Save the user instance created by UserCreationForm
        user = super().save(commit=commit)
        user.username = user.username.lower()
        user.is_vendor = True  # Set the user as a vendor

        if commit:
            user.save()

        # Create a Vendor instance related to the user
        vendor = Vendor.objects.create(
            user=user,
            revenue=self.cleaned_data['revenue'],
            No_of_emp=self.cleaned_data['No_of_emp'],
            gst_no=self.cleaned_data['gst_no'],
            phone_no=self.cleaned_data['phone_no'],
        )

        # Set the many-to-many relationship
        vendor.category.set(self.cleaned_data['category'])
        return user


class RfpListForm(forms.ModelForm):
    rfp_title = forms.CharField(max_length=255)
    item_desc = forms.CharField()
    last_date = forms.DateField()
    min_amount = forms.FloatField()
    max_amount = forms.FloatField()
    vendors = forms.ModelMultipleChoiceField(
        queryset=Vendor.objects.all(),  # Queryset to fetch all vendors
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
    )

    class Meta:
        model = RFPList
        fields = ['rfp_title', 'item_desc', 'last_date', 'min_amount', 'max_amount', 'vendors']

class CategorySelectionForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(c_status='active'),
        label='Select Category'
    )

        
   
from .models import Admin, Quotes

class QuotesForm(forms.ModelForm):
    class Meta:
        model = Quotes
        fields = ['vendor_price', 'item_desc','quantity', 'total_price']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['c_name','c_status'] 

class AdminCommentsForm(forms.Form):
    comments = forms.CharField(widget=forms.Textarea)