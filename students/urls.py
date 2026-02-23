from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('students/', views.students_page, name='students'),
    path('add/', views.add_student, name='add_student'),
    path('delete/<int:id>', views.delete_student, name='delete_student'),
    path('edit/<int:id>', views.edit_student, name='edit_student'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-password/success/', views.change_password_success, name='change_password_success')
    ,
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    path('api/students/', views.student_api, name='student_api'),
]
