# Liew Qian Hui 22063182
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DisasterReport, AidRequest, Shelter, Skill, VolunteerProfile

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

# Volunteer Profile admin
@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'availability', 'display_skills')
    list_filter = ('availability',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('skills',)

    def display_skills(self, obj):
        return ", ".join([skill.name for skill in obj.skills.all()])
    display_skills.short_description = 'Skills'
