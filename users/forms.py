from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from users.models import Category, Quotes, RFPList, Vendor




class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields = ['username','first_name','last_name','email','password1','password2'] 


class RegisterFormVendor(UserCreationForm):

    class Meta:
        model = Vendor
        fields = ['username','first_name','last_name','email','password1','password2','revenue','No_of_emp','gst_no','phone_no']


class RfpListForm(forms.ModelForm):
    class Meta:
        model = RFPList
        fields = ['rfp_title', 'item_desc', 'last_date', 'min_amount', 'max_amount','category']
   
from .models import Quotes

class QuotesForm(forms.ModelForm):
    class Meta:
        model = Quotes
        fields = ['vendor_price', 'item_desc','quantity', 'total_price']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['c_name','c_status'] 