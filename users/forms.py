from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from users.models import Quotes, RFPList, Vendor




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
        fields = ['rfp_title', 'item_desc', 'last_date', 'min_amount', 'max_amount', 'vendors']

    # Use DateInput with format attribute for date field
    last_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'format': 'yyyy-MM-dd'}))

    # Use SelectMultiple widget for vendors field
    vendors = forms.ModelMultipleChoiceField(
        queryset=Vendor.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select-multiple'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendors'].widget.attrs['class'] = 'select-multiple'