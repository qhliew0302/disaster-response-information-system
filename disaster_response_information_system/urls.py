# Liew Qian Hui 22063182
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('disaster_reports/', views.disaster_reports, name='disaster_reports'),
    path('disaster_reports/create/', views.disaster_report_create, name='disaster_report_create'),
    path('disaster_reports/<int:report_id>/', views.disaster_report_detail, name='disaster_report_detail'),
    path('disaster_reports/<int:report_id>/update_status/', views.update_disaster_status, name='update_disaster_status'),
    path('shelters/', views.shelters, name='shelters'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),  # Changed to use custom logout view
    path('register/', views.register, name='register'),

    # Aid request URLs
    path('aid-request/create/', views.aid_request_create, name='aid_request_create'),
    path('aid-requests/', views.my_aid_requests, name='my_aid_requests'),
    path('aid-request/<int:request_id>/', views.aid_request_detail, name='aid_request_detail'),
    path('aid-request/<int:request_id>/status/<str:new_status>/', views.update_aid_request_status, name='update_aid_request_status'),

    # Volunteer URLs
    path('volunteer/profile/', views.volunteer_profile, name='volunteer_profile'),
    path('volunteer/assignments/', views.my_assignments, name='my_assignments'),
    path('volunteer/assignment/<int:assignment_id>/status/<str:new_status>/', views.update_assignment_status, name='update_assignment_status'),

    # Authority URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Authority management actions
    path('toggle-disaster-report-status/<int:report_id>/', views.toggle_disaster_report_status, name='toggle_disaster_report_status'),
    path('update-aid-request-status/<int:request_id>/<str:new_status>/', views.update_aid_request_status, name='update_aid_request_status'),
    path('shelter/create/', views.shelter_create, name='shelter_create'),
    path('shelter/edit/<int:shelter_id>/', views.shelter_edit, name='shelter_edit'),
    path('toggle-shelter-status/<int:shelter_id>/', views.toggle_shelter_status, name='toggle_shelter_status'),
    path('assign-volunteer/<int:volunteer_id>/', views.assign_volunteer, name='assign_volunteer'),
    path('assign-volunteer-to-request/', views.assign_volunteer_to_request, name='assign_volunteer_to_request'),

    # API Endpoints
    path('api/aid-request/<int:request_id>/', views.api_aid_request_detail, name='api_aid_request_detail'),
    path('api/available-volunteers-for-aid/<int:request_id>/', views.api_available_volunteers, name='api_available_volunteers'),
    path('api/volunteer-profile/<int:volunteer_id>/', views.api_volunteer_profile, name='api_volunteer_profile'),

    # User management
    path('toggle-user-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('api/user-profile/<int:user_id>/', views.api_user_profile, name='api_user_profile'),
]
