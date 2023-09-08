from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse_lazy
from django.views import View
from rfp_project.settings import EMAIL, PSWD
from users.forms import LoginForm, QuotesForm, RegisterForm, RegisterFormVendor, RfpListForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import logging
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin


from users.models import Category, Quotes, RFPList, Vendor

logger = logging.getLogger(__name__)


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


class HomeView(LoginRequiredMixin,View):
    """
    View for the home page.

    Args:
        View (class): The base View class.

    Returns:
        HttpResponse: Renders home page for admin.
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
        
class HomeVendorView(LoginRequiredMixin,View):
    """ View for the home page.

    Args:
        View (class): The base View class.

    Returns:
        HttpResponse: Renders home page for vendor.
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
        Redirects to home page (vendor or admin based on credentials) for valid login.
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
        HttpResponse: Rendered registration form for admin or a redirection to the home page after successful registration.
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
                login(request, user)
                email_sender_view = SendEmailView()
                response = email_sender_view.send_email(request.user.email)
                messages.success(request, 'You have signed up successfully.')
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
        HttpResponse: Rendered registration form for vendor or a redirection to the home page after successful registration.
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
                login(request, user)
                email_sender_view = SendEmailView()
                response = email_sender_view.send_email(request.user.email)
                messages.success(request, 'You have signed up successfully.')
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
        request (HttpRequest):Base View
    Returns:
        HttpResponse: Renderes vendors list.
    """
    
    def get(self, request):
        vendors = Vendor.objects.all()
        return render(request,'Vendor.html',{'vendors':vendors})


class RfpQuotesView(View):
    """View for listing rfp quoted by vendor.

    Args:
        request (HttpRequest): Base View

    Returns:
        HttpResponse: Renders quotes created by vendor, filter them as per admin needs, only approved vendors will be displayed.
    """
    def get(self, request):
        approved_vendors = Vendor.objects.filter(v_status='approve')
        quotes = Quotes.objects.filter(vendor__in=approved_vendors).select_related('rfp', 'vendor').all()
        context = {'quotes': quotes}
        return render(request, 'rfp_quotes.html', context)
    
    
class RfpListView(View):
    """View for Listing RFP created by admin.

    Args:
        request (HttpRequest): Base View.

    Returns:
        HttpResponse: Renders List of RFPs created.
    """
    def get(self, request):
        rfps = RFPList.objects.all()
        return render(request,'rfp_list.html',{'rfps':rfps})
    

class CategoryView(View):
    """View for Categories.

    Args:
        request (HttpRequest): Base View.

    Returns:
        HttpResponse: Renders Catgory List Page."""
    
    def get(self, request):
        category = Category.objects.all()
        return render(request,'category.html',{'category':category})
  

def approve(request, vendor_id):
    """method to Approve the Vendor

    Args:
        request (HttpRequest): The HTTP request object.
        vendor_id (int): The ID of the vendor to be approved.

    Raises:
        Http404: If the vendor with the given ID does not exist.

    Returns:
        HttpResponseRedirect: Redirects to the 'vendor' page after approving the vendor.
    """
    try:
        vendor = Vendor.objects.get(pk=vendor_id)
        vendor.v_status = 'approve'
        vendor.save()
    except Vendor.DoesNotExist:
        raise Http404("Vendor does not exist")
    return redirect('vendor')

def reject(request, vendor_id):
    """Rejects a vendor.

    This method updates the status of the vendor with the given ID to 'reject'.

    Args:
        request (HttpRequest): The HTTP request object.
        vendor_id (int): The ID of the vendor to be rejected.

    Raises:
        Http404: If the vendor with the given ID does not exist.

    Returns:
        HttpResponseRedirect: Redirects to the 'vendor' page after rejecting the vendor.
    """
    try:
        vendor = Vendor.objects.get(pk=vendor_id)
        vendor.v_status = 'reject'
        vendor.save()
    except Vendor.DoesNotExist:
        raise Http404("Vendor does not exist")
    return redirect('vendor')

def rfpopen(request, id):
    """Open an RFP.

    This view opens an RFP by updating its status to 'open'.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the RFPList to be opened.

    Raises:
        Http404: If the RFPList with the given ID does not exist.

    Returns:
        HttpResponseRedirect: Redirects to the 'rfp-list' page after opening the RFP.
    """
    try:
        rfps = RFPList.objects.get(pk=id)
        rfps.status = 'open'
        rfps.save()
    except RFPList.DoesNotExist:
        raise Http404("RFPLIST does not exist")
    return redirect('rfp-list')

def rfpclose(request, id):
    """Close an RFP.

    This view closes an RFP by updating its status to 'close'.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the RFPList to be closed.

    Raises:
        Http404: If the RFPList with the given ID does not exist.

    Returns:
        HttpResponseRedirect: Redirects to the 'rfp-list' page after closing the RFP.
    """
    try:
        rfps = RFPList.objects.get(pk=id)
        rfps.status = 'close'
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
    """Send an email to the specified email address.

        Args:
            email (str): The recipient's email address.

        Returns:
            dict: A dictionary containing the success status of the email sending operation.
                - 'success' (bool): True if the email was sent successfully, False otherwise.
                - 'error' (str): An error message in case of failure.
    """
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
    """View for vendors to quote RFPs.

    Args:
        View (Base Class): Base class view.
    """

    def get(self, request):
        try:
            rfps = RFPList.objects.all()
        except RFPList.DoesNotExist:
            raise Http404("No RFPs found")
        
        return render(request, 'rfp_for_quotes.html', {'rfps': rfps})


def send_emails(subject, body, sender, recipients, password):
    """Send broadcast emails.

    This function sends an email to a list of recipients.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        sender (str): The sender's email address.
        recipients (list): A list of recipient email addresses.
        password (str): The password of the sender's email address.

    Returns:
        None

    Raises:
        Exception: If an error occurs during the email sending process.
    """
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())
        
        print("Message sent!")
    except Exception as e:
        # Handle email sending errors here
        # You can log the error or take appropriate action
        print(f"Error sending email: {str(e)}")


class CreateRfpView(CreateView):
    """Class-based view for creating a new Request for Proposal (RFP).

    This view is called when the 'Create Rfp' button is clicked and is used to create a new RFP.

    Args:
        CreateView (class): The base class for Django class-based views.

    Attributes:
        model (class): The model associated with the view (RFPList in this case).
        fields (list): The fields of the model that should be displayed in the form.
        success_url (str): The URL to redirect to after a successful form submission.
    """
    model = RFPList
    fields = ['rfp_title','item_desc','last_date','min_amount','max_amount','category'] 
    success_url = reverse_lazy('rfp-list')  # Redirect to rfp-list URL after successful form submission

    def get(self, request, *args, **kwargs):
        # Display the form for GET requests
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)  
        return response
    
    def form_valid(self, form):
        form.instance.created_by_id = self.request.user.id
        # Save the form data and then send the email
        response = super().form_valid(form)
        
        # Prepare the email subject and body
        subject = 'New RFP Added'
        body = f"A new RFP titled '{self.object.rfp_title}' has been added. Check it out!"
        
        # Get the list of user emails (assuming you have a `User` model with an `email` field)
        user_emails = Vendor.objects.values_list('email', flat=True)
        
        # Convert the QuerySet to a list
        recipients = list(user_emails)
        
        try:
            # Send the email
            send_emails(subject, body,EMAIL, recipients,PSWD)
            return response
        except Exception as e:
            # Handle email sending errors here
            # You can log the error or take appropriate action
            return JsonResponse({'success': False, 'error': str(e)})
        
class CreateRFpForQuoteView(CreateView):
    """Class-based view for creating a new Request for Proposal (RFP) for quotes.

    Args:
        CreateView (class): The base class for Django class-based views.

    Attributes:
        model (class): The model associated with the view (Quotes in this case).
        fields (list): The fields of the model that should be displayed in the form.
        success_url (str): The URL to redirect to after a successful form submission.
    """
    model = Quotes
    fields = ['vendor_price','item_desc','quantity','total_price'] 
    success_url = reverse_lazy('rfp-for-quotes')  # Redirect to rfp-list URL after successful form submission

    def get(self, request, *args, **kwargs):
        # Display the form for GET requests
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)  
        return response
    
    def form_valid(self, form):
        vendor = self.request.user.vendor

        # Get the rfp_id from the URL
        rfp_id = self.kwargs['rfp_id']

        # Retrieve the RFPList object based on the rfp_id
        rfp = RFPList.objects.get(pk=rfp_id)

        # Set the vendor and RFPList objects for the Quotes object
        form.instance.vendor = vendor
        form.instance.rfp = rfp
        form.instance.item_name = rfp.rfp_title

        response = super().form_valid(form)

         # Prepare the email subject and body
        subject = 'New RFP  Added By Vendor'
        body = f"A new RFP has been added . Check it out!"
        
        created_by_email = rfp.created_by.email
        
        try:
            # Send the email
            send_emails(subject, body,EMAIL,[created_by_email],PSWD)
            return response
        except Exception as e:
            # Handle email sending errors here
            # You can log the error or take appropriate action
            return JsonResponse({'success': False, 'error': str(e)})
