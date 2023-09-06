from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from users.models import RFPList, Vendor




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


class RfpListForm(forms.Form):
    class Meta:
        model=RFPList
        fields = ['rfp_title','last_date','min_amount','max_amount'] 

