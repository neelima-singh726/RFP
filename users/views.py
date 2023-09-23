import random
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from requests import Response
import requests
from rfp_project.settings import EMAIL, PSWD
from users.forms import LoginForm, QuotesForm, RegisterForm, RegisterFormVendor, RfpListForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import logging
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db import transaction
from .models import  User

from users.models import  Category, Quotes, RFPList, Vendor

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
    """
    A view for handling user sign-in functionality.

    Args:
        View (class): A class provided by Django for creating views.
    """
    def get(self, request):
        try:
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

                if username and password:  # Check if fields are not empty
                     user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)

                    # Check if the user is an admin or a vendor
                    if user.is_admin:
                        return redirect('home-admin')
                    elif user.is_vendor:
                        try:
                            vendor = Vendor.objects.get(user=user)
                            if vendor.v_status == 'approve':
                                return redirect('home-vendor')
                            else:
                                # Vendor is not approved, display a message and log them out
                                messages.error(request, 'Vendor not approved.')
                                logout(request)
                                return redirect('login')
                        except Vendor.DoesNotExist:
                            # Handle the case where there's no associated vendor
                            messages.error(request, 'No associated vendor found.')
                            logout(request)
                            return redirect('login')
                    else:
                        # Handle other user types as needed
                        return redirect('home')
                    
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

class SignUpView(CreateView):
    """View for user sign up.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered registration form for admin or a redirection to the home page after successful registration.
    """
    template_name = 'register.html'
    success_redirect_url = 'home-admin'
    form_class = RegisterForm

    def get(self, request):
        try:
            form = self.form_class()
            return render(request, self.template_name, {'form': form})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)          
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('register')
    def form_valid(self, form):
         # Check for empty fields
        for field_name, field_value in form.cleaned_data.items():
            if not field_value:
                messages.error(self.request, f'{field_name.capitalize()} field cannot be empty.')
                return redirect('register')
        # Check if a user with the same email already exists
        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            messages.error(self.request, 'A user with this email address already exists.')
            return redirect('register')

        user = form.save(commit=False)
        user.is_admin = True  # Set the user as an admin

        # Modify user attributes here if needed
        # user.some_attribute = some_value

        user.save()
        login(self.request, user)

        return redirect(reverse(self.success_redirect_url))

    def post(self, request):
        try:
           form = self.form_class(request.POST)
           if form.is_valid():
                for field_name, field_value in form.cleaned_data.items():
                    if not field_value:
                        messages.error(request, f'{field_name.capitalize()} field cannot be empty.')
                        return render(request, self.template_name, {'form': form})

                # Check if a user with the same email already exists
                email = form.cleaned_data['email']
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'A user with this email address already exists.')
                    return redirect('register')

                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                user.is_superuser = True
                user.is_staff = True
                user.save()
                login(request, user)
                email_sender_view = SendEmailView()
                response = email_sender_view.send_email(user.email)
                return redirect(self.success_redirect_url)
           else:
                return render(request, self.template_name, {'form': form})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('register')


def signup_vendor(request):
    """View for vendor sign up.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered registration form for admin or a redirection to the home page after successful registration.
    """
    if request.method == 'POST':
        form = RegisterFormVendor(request.POST)
        if form.is_valid():
            # Save the user instance created by the form
            user = form.save()
            
            return redirect('login')  # Replace 'success' with the actual success URL
        if not form.is_valid():
            print(form.errors)

    else:
        form = RegisterFormVendor()
        
    countries_response = requests.get("http://68.183.82.227:1337/api/countries")
    if countries_response.status_code == 200:
        countries_data = countries_response.json().get('data', [])
    else:
        countries_data = []

    return render(request, 'registerVendor.html', {'form': form, 'countries_data': countries_data})


class VendorView(LoginRequiredMixin,View):
    """View for Vendor Page.

    Args:
        request (HttpRequest):Base View
    Returns:
        HttpResponse: Renderes vendors list.
    """
    
    def get(self, request):
        vendors = Vendor.objects.all()
        return render(request,'Vendor.html',{'vendors':vendors})


class RfpQuotesView(LoginRequiredMixin,View):
    """View for listing rfp quoted by vendor.

    Args:
        request (HttpRequest): Base View

    Returns:
        HttpResponse: Renders quotes created by vendor, filter them as per admin needs, only approved vendors will be displayed.
    """
    def get(self, request):
        quotes = Quotes.objects.filter(rfp__created_by=request.user).select_related('rfp', 'vendor').all()
        context = {'quotes': quotes}
        return render(request, 'rfp_quotes.html', context)
    
    
class RfpListView(LoginRequiredMixin,View):
    """View for Listing RFP created by admin.

    Args:
        request (HttpRequest): Base View.

    Returns:
        HttpResponse: Renders List of RFPs created.
    """
    def get(self, request):
        rfps = RFPList.objects.filter(created_by=request.user) 
        return render(request,'rfp_list.html',{'rfps':rfps})
    

class CategoryView(LoginRequiredMixin,View):
    """View for Categories.

    Args:
        request (HttpRequest): Base View.

    Returns:
        HttpResponse: Renders Catgory List Page."""
    
    def get(self, request):
        category = Category.objects.all()
        # paginator = Paginator(category, 5)  # 5 vendors per page
        # page = request.GET.get('page')  # Get the current page number from the URL parameter
        # category = paginator.get_page(page) 
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
        # code for approval email
        subject = 'Status Approved'
        body = f"Hi! your status has been approved."
        
        user_emails = Vendor.objects.select_related(
        'user'
        ).values_list(
        'user__email',
        flat = True
         )
        
        # Convert the QuerySet to a list
        recipients = list(user_emails)
        
        try:
            # Send the email
            send_emails(subject, body,EMAIL, recipients,PSWD)
            return redirect('vendor')

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
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

def activate(request,category_id):
    """Activate a category.

    This view is used to set the status of a category to 'active'.

    Args:
        request (HttpRequest): The HTTP request object.
        Category_id (int): The ID of the category to activate.

    Raises:
        Http404: If the category with the given ID does not exist.

    Returns:
        HttpResponseRedirect: Redirects to the 'category' page after activating the category.
    """
    try:
        category = Category.objects.get(pk=category_id)
        category.c_status = 'active'
        category.save()
        
    except Category.DoesNotExist:
        raise Http404("catgory does not exist")
    return redirect('category')

def deactivate(request, category_id):
    """Deactivate a category.

    This view is used to set the status of a category to 'inactive'.

    Args:
        request (HttpRequest): The HTTP request object.
        Category_id (int): The ID of the category to deactivate.

    Raises:
        Http404: If the category with the given ID does not exist.

    Returns:
        HttpResponseRedirect: Redirects to the 'category' page after deactivating the category.
    """
    
    try:
        category = Category.objects.get(pk=category_id)
        category.c_status = 'inactive'
        category.save()
    except Category.DoesNotExist:
        raise Http404("category does not exist")
    return redirect('category')


from django.http import HttpResponse, JsonResponse
import smtplib

import json
import smtplib
from django.http import JsonResponse
from email.mime.text import MIMEText
from users.models import User
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


from django.db.models import Exists, OuterRef


from django.db.models import OuterRef, Subquery

class RfpForQuotesView(LoginRequiredMixin, View):
    """View for vendors to quote RFPs."""

    def get(self, request):
        try:
            # Get the list of RFPs
            logged_in_vendor = request.user.vendor

        # Get the categories associated with the logged-in vendor
            vendor_categories = logged_in_vendor.category.all()

        # Filter the RFPs based on categories
            rfps = RFPList.objects.filter(category__in=vendor_categories).distinct()
            quotes = Quotes.objects.all()
            # Get the list of RFPs where the vendor is the winner
            won_rfps = RFPList.objects.filter(quotes__winner=request.user).distinct()

            # Get the list of RFP IDs for which the vendor has already applied
            applied_rfps = Quotes.objects.filter(
                vendor__user=request.user,
                applied=True
            ).values_list('rfp_id', flat=True)

            # Create a dictionary with RFP IDs as keys and associated quotes with comments as values
           
           
        except Quotes.DoesNotExist:
            raise Http404("No RFPs found")

        return render(
            request,
            'rfp_for_quotes.html',
            {'rfps': rfps, 'applied_rfps': applied_rfps, 'won_rfps': won_rfps,'quotes':quotes}
        )
from django.views.generic.edit import UpdateView

class UpdateRFpForQuoteView(UpdateView):
    """Class-based view for updating an existing Request for Proposal (RFP) for quotes.

    Args:
        UpdateView (class): The base class for Django class-based views.

    Attributes:
        model (class): The model associated with the view (Quotes in this case).
        fields (list): The fields of the model that should be displayed in the form.
        template_name (str): The name of the template to use for the update view.
        success_url (str): The URL to redirect to after a successful form submission.
    """
    model = Quotes
    fields = ['vendor_price', 'item_desc', 'quantity', 'total_price'] 
    # template_name = 'quotes_form.html'  # Create an HTML template for the update form
    success_url = reverse_lazy('rfp-for-quotes')  # Redirect to rfp-list URL after successful form submission

    def get_object(self, queryset=None):
        # Retrieve the existing quote based on quote_id
        quote_id = self.kwargs.get('quotes_id')
        return get_object_or_404(Quotes, quotes_id=quote_id)

    def form_valid(self, form):
        # Get the existing quote object
        quote = self.get_object()
       

        # Perform any additional logic when the form is valid
        # For example, you can update additional fields or perform other actions
        # In this case, you can update the fields based on the form data
        quote.vendor_price = form.cleaned_data['vendor_price']
        quote.item_desc = form.cleaned_data['item_desc']
        quote.quantity = form.cleaned_data['quantity']
        quote.total_price = form.cleaned_data['total_price']
        quote.updated = True

    # Save the updated quote with commit=False
       
        quote.save()

    # Redirect to the success URL
        super().form_valid(form)

    # Explicitly save the changes to the database
        quote.updated = True
        quote.save()
        messages.success(self.request, 'Quote updated successfully.')

        # Prepare the email subject and body
        subject = 'New RFP Quote Added considering your commnet'
        body = f"A new RFP has been added. Check it out!"
        
        # Get the list of user emails (assuming you have a `User` model with an `email` field)
        
        
        # user_emails = Vendor.objects.values_list('email', flat=True)
        
        rfp = quote.rfp

# Get the user associated with the created_by_id of the RFP
        user = rfp.created_by

# Get the email address of the user
        user_email = user.email
        recipients = [user_email]
        
        try:
            # Send the email
            send_emails(subject, body,EMAIL, recipients,PSWD)
            
        except Exception as e:
            # Handle email sending errors here
            # You can log the error or take appropriate action
            return JsonResponse({'success': False, 'error': str(e)})
        
        return HttpResponseRedirect(self.success_url)




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

from django import forms
from django.utils import timezone

def create_rfp(request, category=None):
    """
    Create a Request for Proposal (RFP) based on user input.

    This function handles the creation of an RFP when the HTTP request method is POST.
    It validates the form data, associates the RFP with the logged-in user, and stores it in the database.

    Args:
        request (HttpRequest): The HTTP request object.
        category (Category, optional): The category to associate with the RFP (default is None).

    Returns:
        HttpResponse: A response indicating the success or failure of the RFP creation process.
    """
    if request.method == 'POST':
        form = RfpListForm(request.POST)
        if form.is_valid():
            # Save the user instance created by the form
           
            user = request.user
            category = get_object_or_404(Category, pk=category)
            # Create the RFP instance related to the user
            rfp = RFPList(
                created_by=user,
                rfp_title=form.cleaned_data['rfp_title'],
                item_desc=form.cleaned_data['item_desc'],
                last_date=form.cleaned_data['last_date'],
                min_amount=form.cleaned_data['min_amount'],
                max_amount=form.cleaned_data['max_amount'],
                category=category
            )
            rfp.save()

            # Set the many-to-many relationship with vendors
            rfp.vendors.set(form.cleaned_data['vendors'])

            # Send emails to selected vendors
            recipients = form.cleaned_data['vendors'].values_list('user__email', flat=True)
            subject = 'New RFP Added'
            body = f"A new RFP has been added. Check it out!"
        

            try:
                send_emails(subject, body,EMAIL, recipients,PSWD)
            except Exception as e:
                # Handle email sending errors here
                print(f"Email sending failed: {str(e)}")

            # Redirect to a success page or another appropriate view
            return redirect('rfp-list')  # Replace 'rfp-list' with your success URL

    else:
        form = RfpListForm()

        # If a category is selected, filter vendors based on the category
        if category:
            form.fields['vendors'].queryset = Vendor.objects.filter(category__category_id=category)

    return render(request, 'users/rfplist_form.html', {'form': form})


        
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
        try:
             vendor = Vendor.objects.get(user_id=self.request.user.id)
        except Vendor.DoesNotExist:
             return JsonResponse({'success': False, 'error': 'Vendor not found for this user.'})

        # Get the rfp_id from the URL
        rfp_id = self.kwargs['rfp_id']

        # Retrieve the RFPList object based on the rfp_id
        rfp = RFPList.objects.get(pk=rfp_id)


        # Set the vendor and RFPList objects for the Quotes object
        form.instance.vendor = vendor
        form.instance.rfp = rfp
        form.instance.item_name = rfp.rfp_title

        response = super().form_valid(form)
       
        quotes = Quotes.objects.select_related('vendor', 'rfp').filter(vendor=vendor, rfp=rfp)

        if quotes.exists():
             for quote in quotes:
                 quote.applied = True
                 quote.save()

         # Prepare the email subject and body
        subject = 'New RFP  Added By Vendor'
        body = f"A new RFP has been added . Check it out!"
        
        created_by_email = rfp.created_by.email
        
        try:
            # Send the email
            send_emails(subject, body,EMAIL,[created_by_email],PSWD)
            # return response
        except Exception as e:
            # Handle email sending errors here
            # You can log the error or take appropriate action
            return JsonResponse({'success': False, 'error': str(e)})
        
        
        # Prepare the context with a flag indicating whether the user has already applied
        context = {
            'rfp': rfp,
            'quotes': quotes,
            'user_has_applied': True,
        }

        # Render the template with the context and return the response
        return render(self.request, 'rfp_for_quotes.html', context)
        
import time

def reset_password(request, uidb64, token, timestamp):
    """View for resetting a user's password.

    Args:
        request (HttpRequest): The HTTP request object.
        uidb64 (str): The base64-encoded user ID.
        token (str): The password reset token.
        timestamp (str): The timestamp when the reset link was generated.

    Returns:
        HttpResponse: The HTTP response object.
    """
        # Convert the timestamp to an integer
    timestamp = int(timestamp)
        
        # Calculate the elapsed time since the link was generated
    current_time = int(time.time())
    elapsed_time = current_time - timestamp
        
        # Check if the link has expired (e.g., 60 seconds)
    expiration_time = 60  # Adjust as needed
    if elapsed_time > expiration_time:
        return render(request, 'password_reset_timeout.html')
        
    if request.method == 'POST':
        new_password = request.POST.get('newPassword')
            
        try:
            uid = urlsafe_b64decode(uidb64).decode('utf-8')
            user = User.objects.get(pk=uid)
                
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                # Add a success message
                messages.success(request, 'Password reset successful. You can now log in with your new password.')
                
                # Redirect to the login page
                return redirect('login') 
            else:
                return JsonResponse({'success': False, 'error': 'Invalid token'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})



def forgot_password(request):
    """View for displaying the forgot password page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    """
    return render(request, 'forgot_password.html')


def send_reset_email(request):
    """View for sending a password reset email.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_b64encode(force_bytes(user.pk))
                timestamp = int(time.time())  # Get the current timestamp
                reset_link = f"http://127.0.0.1:8000/reset/{uidb64.decode()}/{token}/{timestamp}/"      
                subject = "Reset Password"
                body = f"Click the following link to reset your password: {reset_link}"
                sender = EMAIL
                recipients = [email]
                password = PSWD
                
                send_emails(subject, body, sender, recipients, password)
                
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})





class CreateCategoryView(CreateView):
    """Class-based view for creating a new Category

    This view is called when the 'Create Category' button is clicked and is used to create a new category.

    Args:
        CreateView (class): The base class for Django class-based views.

    Attributes:
        model (class): The model associated with the view .
        fields (list): The fields of the model that should be displayed in the form.
        success_url (str): The URL to redirect to after a successful form submission.
    """
    model = Category
    fields = ['c_name','c_status'] 
    success_url = reverse_lazy('category')  # Redirect to rfp-list URL after successful form submission

    def get(self, request, *args, **kwargs):
        # Display the form for GET requests
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Save the category and set a success message
        category_name = form.cleaned_data['c_name']
        if Category.objects.filter(c_name=category_name).exists():
            # Display an error message and prevent form submission
            form.add_error('c_name', 'Category with this name already exists.')
            return self.form_invalid(form)
        category = form.save()
        messages.success(self.request, f'Category "{category.c_name}" has been created successfully!')
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)  
        return response

import csv
from django.http import HttpResponse
from .models import Quotes  

def export_quotations(request, rfp_id):
    """Export quotations for a specified Request for Proposal (RFP) as a CSV file.

    This function retrieves quotations associated with a specific RFP, generates a CSV file containing
    the relevant quotation data, and returns it as an HTTP response with the appropriate content type
    for CSV files.

    Args:
        request (HttpRequest): The HTTP request object.
        rfp_id (int): The unique identifier of the RFP for which quotations should be exported.

    Returns:
        HttpResponse: An HTTP response containing the CSV file with quotation data as an attachment.
    
    """
    # Fetch quotations for the specified RFP
    quotations = Quotes.objects.filter(rfp_id=rfp_id)

    # Create a response object with the appropriate content type for CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="quotations_{rfp_id}.csv"'

    # Create a CSV writer and write the header row
    writer = csv.writer(response)
    writer.writerow(['Vendor', 'Vendor Price', 'Item Description', 'Quantity', 'Total Price'])

    # Write the quotation data
    for quote in quotations:
        writer.writerow([quote.vendor.user.username, quote.vendor_price, quote.item_desc, quote.quantity, quote.total_price])

    return response

from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

@login_required
def select_winner(request, id, quotes_id):
    """Select a winning quotation for a specified Request for Proposal (RFP).

    This function retrieves the quotation and RFP based on their respective IDs, and it checks if
    the quotation belongs to the specified RFP. If the quote does not belong to the RFP, it returns
    a JSON response indicating the error.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The unique identifier of the RFP for which a winner is being selected.
        quotes_id (int): The unique identifier of the quotation to be selected as the winner.

    Returns:
        JsonResponse: A JSON response indicating success or an error message if the quote does not
                      belong to the specified RFP.
    """
    # Fetch the quote and RFP based on IDs
    quote = get_object_or_404(Quotes, pk=quotes_id)
    rfp = get_object_or_404(RFPList, pk=id)

    # Check if the quote belongs to the specified RFP
    if quote.rfp != rfp:
        # Quote does not belong to the specified RFP, handle the error as needed
        return JsonResponse({'error': 'Quote does not belong to the specified RFP'})

    # Check if any other quote associated with this RFP already has a winner
    quotes_to_update = Quotes.objects.filter(rfp=rfp, winner__isnull=True)

    if quotes_to_update:
        # Update the winner field for all quotes associated with this RFP
        winner_user = quote.vendor.user
        quotes_to_update.update(winner=winner_user)

        # Return the winner's name
        return redirect('rfp-quotes')
    else:
        # All quotes associated with this RFP already have winners, handle the error as needed
        return JsonResponse({'error': 'All quotes from this RFP already have winners'})
    
from django.http import JsonResponse

@login_required
def remove_winner(request, id, quotes_id):
    """Remove the winner designation from a quotation for a specified Request for Proposal (RFP).

    This function retrieves the quotation and RFP based on their respective IDs, and it checks if
    the quotation belongs to the specified RFP. If the quote does not belong to the RFP, it returns
    a JSON response indicating the error. It also checks if the quote currently has a winner and,
    if so, removes the winner designation from all quotations with the same RFP number.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The unique identifier of the RFP for which a winner designation is being removed.
        quotes_id (int): The unique identifier of the quotation from which the winner is being removed.

    Returns:
        HttpResponse or JsonResponse: An HTTP response indicating success or an error message if
                                       the quote does not belong to the specified RFP or if the
                                       quote does not have a winner to remove.
    
    """
    # Fetch the quote and RFP based on IDs
    quote = get_object_or_404(Quotes, pk=quotes_id)
    rfp = get_object_or_404(RFPList, pk=id)

    # Check if the quote belongs to the specified RFP
    if quote.rfp != rfp:
        # Quote does not belong to the specified RFP, handle the error as needed
        return JsonResponse({'error': 'Quote does not belong to the specified RFP'})

    # Check if the quote currently has a winner
    if quote.winner is not None:
        # Get the RFP number of the current quote
        rfp_number = quote.rfp.id

        # Remove the winner from all quotes with the same RFP number
        related_quotes = Quotes.objects.filter(rfp__id=rfp_number)
        related_quotes.update(winner=None)

        # Return a success response or any other information you need
        return redirect('rfp-quotes')
    else:
        # The quote does not have a winner, handle the error as needed
        return JsonResponse({'error': 'The quote does not have a winner to remove'})


from .forms import AdminCommentsForm, CategorySelectionForm

@login_required
def request_quote(request, id, quotes_id):
    """Handle requests for adding admin comments to a quotation and sending notification emails.

    This function fetches the quotation and RFP based on their respective IDs and handles the process
    of adding admin comments to a quotation. If the HTTP request method is POST and the form data is valid,
    it saves the admin comments in the Quotes model, sends a notification email to the vendor, and redirects
    to the 'rfp-quotes' page.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The unique identifier of the RFP associated with the quotation.
        quotes_id (int): The unique identifier of the quotation for which admin comments are being added.

    Returns:
        HttpResponse or JsonResponse: An HTTP response indicating success or an error message if there was
                                       an issue with saving comments or sending emails.
  
    """
    # Fetch the quote and RFP based on IDs
    quote = get_object_or_404(Quotes, pk=quotes_id)
    rfp = get_object_or_404(RFPList, pk=id)

    if request.method == 'POST':
        form = AdminCommentsForm(request.POST)
        if form.is_valid():
            comments = form.cleaned_data['comments']
            # Save the comments in the Quotes model
            quote.admin_comments = comments
            quote.updated = 0
            quote.save()
            vendor = quote.vendor
            user = vendor.user
            user_email = user.email   
            recipients = [user_email]
            subject = "Comments Added by admin on your quote"
            body = "recreate the rfp quote, addressing the comments "
            try:
            # Send the email
               send_emails(subject, body,EMAIL, recipients,PSWD)
            
            except Exception as e:
            
                return JsonResponse({'success': False, 'error': str(e)})
            return redirect('rfp-quotes')
    else:
        form = AdminCommentsForm()

    return render(request, 'request_quote.html', {'form': form, 'quote': quote})
  
from django.views.generic.edit import FormView
   
class CategorySelectionView(FormView):
    """View for selecting a category when creating a new Request for Proposal (RFP).

    This class-based view inherits from Django's FormView and is used to display a form for selecting a category
    when creating a new RFP. When the form is submitted and valid, it redirects the user to the 'create-rfp' view
    with the selected category.

    Args:
        FormView (class): A class provided by Django for creating views that handle forms.

    Returns:
        HttpResponse: An HTTP response that renders the category selection form.
    
    """
    form_class = CategorySelectionForm
    template_name = 'category_selection.html'  # Create a template for category selection

    def form_valid(self, form):
        selected_category = form.cleaned_data['category'].category_id
        return redirect('create-rfp', category=selected_category)
        