from django.utils import timezone

from django import forms
from django.contrib.auth.forms import UserCreationForm
import requests
from users.models import User
import json
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
from django.core.validators import RegexValidator
import re
class RegisterFormVendor(UserCreationForm):
    No_of_emp = forms.IntegerField(required=True)
    pan_no = forms.CharField(max_length=10, required=True)

    # GST Number Field
    gst_no = forms.CharField(max_length=15, required=True)

    # Phone Number Field
    phone_no = forms.CharField(max_length=10, required=True)

    revenue = forms.CharField(max_length=255,required=True)
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(c_status='active'),  # Filter for active categories
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=True
    )
    country = forms.ChoiceField(choices=[], required=True, widget=forms.Select(attrs={'class': 'select2'}))
    state = forms.ChoiceField(choices=[], required=True, widget=forms.Select(attrs={'class': 'select2'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'revenue', 'No_of_emp', 'gst_no', 'pan_no','phone_no', 'category', 'country', 'state']
    
    def clean(self):
        cleaned_data = super().clean()
        
         # PAN Number Validation
        pan_no = cleaned_data.get('pan_no')
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_no):
            raise forms.ValidationError("Enter a valid PAN number.", code="invalid_pan")

        # GST Number Validation
        gst_no = cleaned_data.get('gst_no')
        if not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$', gst_no):
            raise forms.ValidationError("Enter a valid GST number.", code="invalid_gst")

        # Phone Number Validation
        phone_no = cleaned_data.get('phone_no')
        if not re.match(r'^[0-9]{10}$', phone_no):
            raise forms.ValidationError("Phone number must be exactly 10 digits.", code="invalid_phone")
        
        existing_vendor_with_pan = Vendor.objects.filter(pan_no=pan_no).first()
        if existing_vendor_with_pan:
            raise forms.ValidationError("This PAN number is already associated with another user.", code="duplicate_pan")

        # Check uniqueness of GST number
        existing_vendor_with_gst = Vendor.objects.filter(gst_no=gst_no).first()
        if existing_vendor_with_gst:
            raise forms.ValidationError("This GST number is already associated with another user.", code="duplicate_gst")

        return cleaned_data
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate the country choices from the API when initializing the form
        countries_response = requests.get("http://68.183.82.227:1337/api/countries")
        if countries_response.status_code == 200:
            countries_data = countries_response.json().get('data', [])
            country_choices = [(country['id'], country['attributes']['name']) for country in countries_data]
        else:
            country_choices = []

        self.fields['country'].choices = [('', 'Select Country')] + country_choices

        # Check if a selected country is passed in the form data
        selected_country_id = None
        if 'country' in self.data:
            selected_country_id = self.data['country']
        
        # Populate the state choices based on the selected country
        self.populate_state_choices(selected_country_id)

    
    def populate_state_choices(self, selected_country_id):
        if selected_country_id:
            # Fetch the list of states for the selected country from the API
            apiUrl = f"http://68.183.82.227:1337/api/countries/{selected_country_id}?populate=states"
            response = requests.get(apiUrl)
            if response.status_code == 200:
                data = response.json().get('data', {})
                states = data.get('attributes', {}).get('states', {}).get('data', [])
                state_choices = [(state['id'], state['attributes']['name']) for state in states]
            else:
                state_choices = []
        else:
            state_choices = []
        print("Selected Country ID:", selected_country_id)
        print("State Choices:", state_choices)

        self.fields['state'].choices = [('', 'Select State')] + state_choices
        

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
            pan_no = self.cleaned_data['pan_no'],
            phone_no=self.cleaned_data['phone_no'],
            country=self.cleaned_data['country'],  # Set the selected country
            state=self.cleaned_data['state'],
        )

        # Set the many-to-many relationship
        vendor.category.set(self.cleaned_data['category'])
        return user


class RfpListForm(forms.ModelForm):
    rfp_title = forms.CharField(max_length=255,required=True)
    item_desc = forms.CharField(required=True)
    last_date = forms.DateField(required=True)
    min_amount = forms.FloatField(required=True)
    max_amount = forms.FloatField(required=True)
    vendors = forms.ModelMultipleChoiceField(
        queryset=Vendor.objects.all(),  # Queryset to fetch all vendors
        required=True,
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
    )

    class Meta:
        model = RFPList
        fields = ['rfp_title', 'item_desc', 'last_date', 'min_amount', 'max_amount', 'vendors']

    def clean_last_date(self):
        last_date = self.cleaned_data.get('last_date')
        current_date = timezone.now().date()  # Get the current date

        if last_date < current_date:
            raise forms.ValidationError("Last date cannot be in the past.")

        return last_date
    
    

class CategorySelectionForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(c_status='active'),
        empty_label='Select Category',
        required=True
    )

        
   
from .models import Admin, Quotes

class QuotesForm(forms.ModelForm):
    vendor_price = forms.FloatField(required=True)
    quantity = forms.IntegerField(required=True)
    total_price = forms.FloatField(required=True)
    class Meta:
        model = Quotes
        fields = ['vendor_price', 'item_desc','quantity', 'total_price']

class CategoryForm(forms.ModelForm):
    c_name = forms.CharField(
        max_length=100,required=True)
    c_status = forms.CharField(
        max_length=10,
        required=True
    )
    class Meta:
        model = Category
        fields = ['c_name','c_status'] 

class AdminCommentsForm(forms.Form):
    comments = forms.CharField(widget=forms.Textarea,required=True)