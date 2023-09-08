from django.urls import path
from . import views



urlpatterns = [
    path('login/', views.SignInView.as_view(), name='login'),
    path('logout/', views.SignOutView.as_view(), name='logout'),
    path('register/', views.SignUpView.as_view(), name='register'),
    path('register-vendor/', views.SignUpVendorView.as_view(), name='register-vendor'),
    path('home-admin', views.HomeView.as_view(), name='home-admin'),
    path('home-vendor', views.HomeVendorView.as_view(), name='home-vendor'),
    path('vendor/', views.VendorView.as_view(), name='vendor'),
    path('rfp-list/', views.RfpListView.as_view(), name='rfp-list'),
    path('rfp-quotes/', views.RfpQuotesView.as_view(), name='rfp-quotes'),
    path('rfp-for-quotes/', views.RfpForQuotesView.as_view(), name='rfp-for-quotes'),
    path('category/', views.CategoryView.as_view(), name='category'),
    path('vendor-approve/<int:vendor_id>/', views.approve, name='vendor-approve'),
    path('vendor-reject/<int:vendor_id>/', views.reject, name='vendor-reject'),
    path('rfp-open/<int:id>/', views.rfpopen, name='rfp-open'),
    path('rfp-close/<int:id>/', views.rfpclose, name='rfp-close'),
    path('create-rfp/', views.CreateRfpView.as_view(), name='create-rfp'),
    path('apply/<int:rfp_id>/', views.CreateRFpForQuoteView.as_view(), name='apply-for-quote'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path("reset/<uidb64>/<token>/", views.reset_password, name = 'reset'),
    path('send-email/', views.send_reset_email, name='send-email'),
    path('activate/<int:category_id>/', views.activate, name='activate'),
    path('deactivate/<int:category_id>/', views.deactivate, name='deactivate'),
    path('create-category/', views.CreateCategoryView.as_view(), name='create-category'),

]
