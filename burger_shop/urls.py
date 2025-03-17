from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'burger_shop'


urlpatterns = [
    path('home/', views.index, name='homepage'),
    path('blog/<int:pk>/', views.blog_post, name='blog_post'),
    path('profile/', views.get_user_profile, name='user-profile'),
    path('menu/', views.menu, name='menu'),
    path('start-order/', views.start_order, name='start_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/finalize/', views.finalize_order, name='finalize_order'),
    path('order/success/', views.order_success, name='order_success'),
    path('my-orders/', views.user_orders, name='user_orders'),
    path('create-burger/', views.create_burger, name='create_burger'),
    path('create-burger/success', views.create_burger_success, name='create_burger_success'),
    path('my-burgers/',views.user_burgers,name='user_burgers'),
    path('my-burgers/<int:burger_id>', views.get_user_burger, name='user_burger'),
    path('custom-burgers/', views.all_custom_burgers, name='custom_burgers'),
    path('no-access/', views.pls_login, name='pls_login'),

    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register_user, name='register'),

    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='burger_shop/registration/password_reset_form.html',
             email_template_name='burger_shop/registration/password_reset_email.html',
             subject_template_name='burger_shop/registration/password_reset_subject.txt',
             success_url='done/'  # Redirect to the next URL in this file
         ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='burger_shop/registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='burger_shop/registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='burger_shop/registration/password_reset_complete.html'), name='password_reset_complete'),


]
