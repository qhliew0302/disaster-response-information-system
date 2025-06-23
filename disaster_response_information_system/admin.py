# Liew Qian Hui 22063182
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DisasterReport, AidRequest, Shelter, Skill, VolunteerProfile, VolunteerAssignment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_role', 'is_staff')
    list_filter = ('user_role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('User Role Information', {'fields': ('user_role', 'phone', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Role Information', {'fields': ('user_role', 'phone', 'address')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'address')

# Register User with custom admin
admin.site.register(User, CustomUserAdmin)

# Disaster Report admin
@admin.register(DisasterReport)
class DisasterReportAdmin(admin.ModelAdmin):
    list_display = ('disaster_type', 'location', 'severity', 'reporter', 'reported_at', 'is_active')
    list_filter = ('disaster_type', 'severity', 'is_active', 'reported_at')
    search_fields = ('location', 'description', 'reporter__username')
    date_hierarchy = 'reported_at'
    ordering = ('-reported_at',)

# Aid Request admin
@admin.register(AidRequest)
class AidRequestAdmin(admin.ModelAdmin):
    list_display = ('aid_type', 'requester', 'location', 'status', 'requested_at')
    list_filter = ('aid_type', 'status', 'requested_at')
    search_fields = ('location', 'description', 'requester__username')
    date_hierarchy = 'requested_at'
    raw_id_fields = ('requester', 'shelter', 'approved_by')
    ordering = ('-requested_at',)

# Shelter admin
@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'capacity', 'current_occupancy', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'contact_info')
    ordering = ('name',)

# Skill admin
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)

# VolunteerProfile admin
@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'availability')
    list_filter = ('availability', 'skills')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    filter_horizontal = ('skills',)
    raw_id_fields = ('user',)

# VolunteerAssignment admin
@admin.register(VolunteerAssignment)
class VolunteerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'aid_request', 'status', 'assigned_at', 'completed_at')
    list_filter = ('status', 'assigned_at', 'completed_at')
    search_fields = ('volunteer__username', 'aid_request__location', 'notes')
    raw_id_fields = ('volunteer', 'aid_request', 'assigned_by')
    date_hierarchy = 'assigned_at'
    ordering = ('-assigned_at',)
