import random
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from requests import Response
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
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)

                    # Check if the user is an admin or a vendor
                    if user.is_admin:
                        return redirect('home-admin')
                    elif user.is_vendor:
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

        messages.success(self.request, 'Admin registration successful!')

        return redirect(reverse(self.success_redirect_url))

    def post(self, request):
        try:
           form = self.form_class(request.POST)
           if form.is_valid():
                messages.success(self.request, 'Admin registration successful!')
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

class SignUpVendorView(CreateView):
    template_name = 'registerVendor.html'
    success_url = reverse_lazy('home-vendor')
    form_class = RegisterFormVendor

    def get(self, request):
        try:
            form = self.form_class()
            return render(request, self.template_name, {'form': form})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('register-vendor')

    @transaction.atomic
    def form_valid(self, form):
        # Check if a user with the same email already exists
        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
              messages.error(self.request, 'A user with this email address already exists.')
              return redirect('register')

    # Create a user object
        user = form.save(commit=False)
        user.is_vendor = True  # Set the user as a vendor
        user.save()  # Save the user object

    # Get the selected category from the form
        category_id = form.cleaned_data['category'].id
        user = User.objects.get(email=email)
    
    # Create a Vendor instance related to the user with a valid category
        vendor = Vendor(
        user=user,
        No_of_emp=form.cleaned_data['No_of_emp'],
        gst_no=form.cleaned_data['gst_no'],
        phone_no=form.cleaned_data['phone_no'],
        revenue=form.cleaned_data['revenue'],
        category_id=category_id,  # Assign the valid category ID
        )
        vendor.save()

        login(self.request, user)
    # Send email or perform other actions if needed

        return super().form_valid(form)

    def post(self, request):
        try:
            form = self.form_class(request.POST)
            if form.is_valid():
                # Check if a user with the same email already exists
                email = form.cleaned_data['email']
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'A user with this email address already exists.')
                    return redirect('register-vendor')
                user = form.save()
                # user.username = user.username.lower()
                # user.save()
                # user.is_superuser = False
                # user.save()
                login(request, user)
                email_sender_view = SendEmailView()
                response = email_sender_view.send_email(user.email)
                return redirect(self.success_url)
            else:
                return render(request, self.template_name, {'form': form})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            error_message = str(e)
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('register-vendor')

class SignUp_View(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'register.html'

class SignUp_VendorView(View):
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
                email = form.cleaned_data['email']  # Get the email from the form
                # Check if a user with this email already exists
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'This email is already registered.')
                    return redirect('register-vendor')
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

from django.core.paginator import Paginator
class VendorView(LoginRequiredMixin,View):
    """View for Vendor Page.

    Args:
        request (HttpRequest):Base View
    Returns:
        HttpResponse: Renderes vendors list.
    """
    
    def get(self, request):
        vendors = Vendor.objects.all()
        paginator = Paginator(vendors, 5)  # 5 vendors per page
        page = request.GET.get('page')  # Get the current page number from the URL parameter
        vendors = paginator.get_page(page)  # Get the vendors for the current page

        return render(request,'Vendor.html',{'vendors':vendors})


class RfpQuotesView(LoginRequiredMixin,View):
    """View for listing rfp quoted by vendor.

    Args:
        request (HttpRequest): Base View

    Returns:
        HttpResponse: Renders quotes created by vendor, filter them as per admin needs, only approved vendors will be displayed.
    """
    def get(self, request):
        approved_vendors = Vendor.objects.filter(v_status='approve')
        quotes = Quotes.objects.filter(vendor__in=approved_vendors).select_related('rfp', 'vendor').all()
        paginator = Paginator(quotes, 5)  # 5 vendors per page
        page = request.GET.get('page')  # Get the current page number from the URL parameter
        quotes = paginator.get_page(page) 
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
        paginator = Paginator(rfps, 5)  # 5 vendors per page
        page = request.GET.get('page')  # Get the current page number from the URL parameter
        rfps = paginator.get_page(page) 
        return render(request,'rfp_list.html',{'rfps':rfps})
    

class CategoryView(LoginRequiredMixin,View):
    """View for Categories.

    Args:
        request (HttpRequest): Base View.

    Returns:
        HttpResponse: Renders Catgory List Page."""
    
    def get(self, request):
        category = Category.objects.all()
        paginator = Paginator(category, 5)  # 5 vendors per page
        page = request.GET.get('page')  # Get the current page number from the URL parameter
        category = paginator.get_page(page) 
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
            quotes = Quotes.objects.filter(vendor_id=request.user.id)

            # Get the list of RFPs where the vendor is the winner
            won_rfps = RFPList.objects.filter(quotes__winner=request.user).distinct()

            # Get the list of RFP IDs for which the vendor has already applied
            applied_rfps = Quotes.objects.filter(
                vendor__user=request.user,
                applied=True
            ).values_list('rfp_id', flat=True)

            # Create a dictionary with RFP IDs as keys and associated quotes with comments as values
           
            paginator = Paginator(quotes, 5)  # 5 RFPs per page
            page = request.GET.get('page')  # Get the current page number from the URL parameter
            quotes = paginator.get_page(page)
        except Quotes.DoesNotExist:
            raise Http404("No RFPs found")

        return render(
            request,
            'rfp_for_quotes.html',
            {'quotes': quotes, 'applied_rfps': applied_rfps, 'won_rfps': won_rfps}
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
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter the queryset for the 'category' field to show only active categories
        form.fields['category'].queryset = Category.objects.filter(c_status='active')
        return form
        
    def form_valid(self, form):
        form.instance.created_by_id = self.request.user.id
        # Save the form data and then send the email
        response = super().form_valid(form)
        
        # Prepare the email subject and body
        subject = 'New RFP Added'
        body = f"A new RFP titled '{self.object.rfp_title}' has been added. Check it out!"
        
        # Get the list of user emails (assuming you have a `User` model with an `email` field)
        
        user_emails = Vendor.objects.select_related(
        'user'
        ).values_list(
        'user__email',
        flat = True
         )
        # user_emails = Vendor.objects.values_list('email', flat=True)
        
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
        

def reset_password(request, uidb64, token):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_password = data.get('new_password')
        
        try:
            uid = urlsafe_b64decode(uidb64).decode('utf-8')
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid token'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})

def forgot_password(request):
    return render(request, 'forgot_password.html')

def send_reset_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_b64encode(force_bytes(user.pk))
                reset_link = f"http://127.0.0.1:8000/reset/{uidb64.decode()}/{token}/"      
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
        return JsonResponse({'winner_name': winner_user.username})
    else:
        # All quotes associated with this RFP already have winners, handle the error as needed
        return JsonResponse({'error': 'All quotes from this RFP already have winners'})

from .forms import AdminCommentsForm

@login_required
def request_quote(request, id, quotes_id):
    # Fetch the quote and RFP based on IDs
    quote = get_object_or_404(Quotes, pk=quotes_id)
    rfp = get_object_or_404(RFPList, pk=id)

    if request.method == 'POST':
        form = AdminCommentsForm(request.POST)
        if form.is_valid():
            comments = form.cleaned_data['comments']
            # Save the comments in the Quotes model
            quote.admin_comments = comments
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
  
    
