from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse_lazy
from django.views import View
from rfp_project.settings import EMAIL, PSWD
from users.forms import LoginForm, RegisterForm, RegisterFormVendor, RfpListForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import logging
from django.views.generic.edit import CreateView


from users.models import RFPList, Vendor

logger = logging.getLogger(__name__)
class HomeView(View):
    """View for the home page.

    Args:
        View (class): The base View class.

    Returns:
        HttpResponse: Renders home page with the list of posts.
    """
    def get(self, request):
        try:
            return render(request, 'homeAdmin.html')
        except Exception as e:
            # Log the exception details
            logger.error(f"An error occurred: {str(e)}")

            # Handle the exception here, you can customize the response
            error_message = str(e)  # Convert the exception to a string
            return HttpResponse(f"An error occurred: {error_message}", status=500)
        
class HomeVendorView(View):
    """View for the home page.

    Args:
        View (class): The base View class.

    Returns:
        HttpResponse: Renders home page with the list of posts.
    """
    def get(self, request):
        try:
            return render(request, 'homeVendor.html')
        except Exception as e:
            # Log the exception details
            logger.error(f"An error occurred: {str(e)}")

            # Handle the exception here, you can customize the response
            error_message = str(e)  # Convert the exception to a string
            return HttpResponse(f"An error occurred: {error_message}", status=500)
        
class SignInView(View):
    """View for user sign in/login

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Renders login form in case of invalid login 
        Redirects to home page for valid login.
    """
    def get(self, request):
        try:
            # if request.user.is_authenticated:
            #     return redirect('home')
            form = LoginForm()
            return render(request, 'login.html', {'form': form})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e) 
            return redirect('login')

    def post(self, request):
        try:
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f'Hi {username.title()}, welcome back!')
                    if user.is_superuser:
                        return redirect('home-admin')
                    else:
                        return redirect('home-vendor')
                    
            messages.error(request, 'Invalid username or password')
            return render(request, 'login.html', {'form': form})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)            
            return redirect('login')

class SignOutView(View):
    """View for user sign out.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Redirection to the login page after logging out.
    """
    # @method_decorator(login_required)
    def get(self, request):
        try:
            logout(request)
            messages.success(request, 'You have been logged out.')
            return redirect('login')
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)
            return redirect('login')

class SignUpView(View):
    """View for user sign up.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered registration form or a redirection to the home page after successful registration.
    """
    def get(self, request):
        try:
            form = RegisterForm()
            return render(request, 'register.html', {'form': form})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)          
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('register')

    def post(self, request):
        try:
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                user.is_superuser = True
                user.is_staff = True
                user.save()
                email_sender_view = SendEmailView()
                response = email_sender_view.send_email(request.user.email)
                messages.success(request, 'You have signed up successfully.')
                login(request, user)
                return redirect('home-admin')
            else:
                return render(request, 'register.html', {'form': form})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('register')

class SignUpVendorView(View):
    """View for user sign up.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered registration form or a redirection to the home page after successful registration.
    """
    def get(self, request):
        try:
            form = RegisterFormVendor()
            return render(request, 'registerVendor.html', {'form': form})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)          
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('register-vendor')

    def post(self, request):
        try:
            form = RegisterFormVendor(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                email_sender_view = SendEmailView()
                response = email_sender_view.send_email(request.user.email)
                messages.success(request, 'You have signed up successfully.')
                login(request, user)
                return redirect('home-vendor')
            else:
                return render(request, 'registerVendor.html', {'form': form})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('register-vendor')

class VendorView(View):
    """View for Vendor Page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Renderes vendors list.
    """
    
    def get(self, request):
        vendors = Vendor.objects.all()
        return render(request,'Vendor.html',{'vendors':vendors})


class RfpQuotesView(View):
    """View for user sign up.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered registration form or a redirection to the home page after successful registration.
    """
    def get(self, request):
        return render(request,'rfp_quotes.html')
    def post(self, request):
        return render(request,'rfp_quotes.html')

class RfpListView(View):
    """View for user sign up.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered registration form or a redirection to the home page after successful registration.
    """
    def get(self, request):
        rfps = RFPList.objects.all()
        return render(request,'rfp_list.html',{'rfps':rfps})
    

class CategoryView(View):
    """View for user sign up.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered registration form or a redirection to the home page after successful registration.
    """
    def get(self, request):
        pass
    def post(self, request):
        pass


def approve(request, vendor_id):
    try:
        vendor = Vendor.objects.get(pk=vendor_id)
        vendor.v_status = 'approve'
        vendor.save()
    except Vendor.DoesNotExist:
        raise Http404("Vendor does not exist")
    return redirect('vendor')

def reject(request, vendor_id):
    try:
        vendor = Vendor.objects.get(pk=vendor_id)
        vendor.v_status = 'reject'
        vendor.save()
    except Vendor.DoesNotExist:
        raise Http404("Vendor does not exist")
    return redirect('vendor')

def rfpopen(request, id):
    try:
        rfps = RFPList.objects.get(pk=id)
        rfps.v_status = 'open'
        rfps.save()
    except RFPList.DoesNotExist:
        raise Http404("RFPLIST does not exist")
    return redirect('rfp-list')

def rfpclose(request, id):
    try:
        rfps = RFPList.objects.get(pk=id)
        rfps.v_status = 'close'
        rfps.save()
    except RFPList.DoesNotExist:
        raise Http404("RFPLIST does not exist")
    return redirect('rfp-list')


from django.http import HttpResponse, JsonResponse
import smtplib

import json
import smtplib
from django.http import JsonResponse
from email.mime.text import MIMEText
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from base64 import urlsafe_b64decode, urlsafe_b64encode


class SendEmailView(View):
    def send_email(self, email):
        try:
            subject = "Account Created"
            body = "User Registered successfully"
            sender = EMAIL
            recipients = [email]
            password = PSWD

            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(sender, password)
                smtp_server.sendmail(sender, recipients, msg.as_string())

            return {'success': True}
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)
            return {'success': False, 'error': str(e)}



class RfpForQuotesView(View):
    """View for user sign up.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered registration form or a redirection to the home page after successful registration.
    """
    def get(self, request):
        return render(request,'rfp_for_quotes.html')
    def post(self, request):
        return render(request,'rfp_for_quotes.html')
   
class CreateRfpView(CreateView):
    model = RFPList
    fields = ['rfp_title','last_date','min_amount','max_amount'] 
    success_url = reverse_lazy('rfp-list')  # Redirect to rfp-list URL after successful form submission

    def get(self, request, *args, **kwargs):
        # Display the form for GET requests
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Handle form submission for POST requests
        return super().post(request, *args, **kwargs)
