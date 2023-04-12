from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

app_name = 'New_Shop'

urlpatterns = [
    path('', home_page, name='home_page'),
    path('product/<slug:category_slug>/', product, name='product'),
    path('detail/<int:id_product>/<slug:product_slug>/', detail, name='detail'),
    path('create/', create, name='create'),
    path('update/<int:id_product>/', update, name='update'),
    path('delete/<int:id_product>/', delete, name='delete'),
    path('search/', product, name='search'),
    
    path('register/', register_request, name='register'),
    path('login/', login_request, name='login'),
    path('logout/', logout_request, name='logout'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
         name='password_reset_complete'),
    path("password_reset/", password_reset_request, name="password_reset"),
    path('subscribe/', subscribe, name='subscribe'),

    path('cart/', cart, name='cart'),
    path('add_to_cart/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:pk>/', remove_from_cart, name='remove_from_cart'),
    # path('payment-success', views.payment_success_view,name='payment-success'),
]
