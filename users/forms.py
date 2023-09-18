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
    category = forms.ModelChoiceField(queryset=Category.objects.filter(c_status='active'))  # Filter for active categories

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
            revenue=self.cleaned_data.get('revenue'),
            No_of_emp=self.cleaned_data.get('No_of_emp'),
            gst_no=self.cleaned_data.get('gst_no'),
            phone_no=self.cleaned_data.get('phone_no'),
            category=self.cleaned_data.get('category'),
        )

        return user

class RfpListForm(forms.ModelForm):
    class Meta:
        model = RFPList
        fields = ['rfp_title', 'item_desc', 'last_date', 'min_amount', 'max_amount','category']
   
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