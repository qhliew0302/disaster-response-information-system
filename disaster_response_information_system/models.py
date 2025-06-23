# Liew Qian Hui 22063182

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    USER_ROLES = [
        ('citizen', 'Citizen'),
        ('volunteer', 'Volunteer'),
        ('authority', 'Authority'),
    ]

    user_role = models.CharField(max_length=10, choices=USER_ROLES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_role_display()})"


class DisasterReport(models.Model):
    DISASTER_TYPES = [
        ('flood', 'Flood'),
        ('landslide', 'Landslide'),
        ('haze', 'Haze'),
        ('other', 'Other'),
    ]

    SEVERITY_LEVELS = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]

    INFRASTRUCTURE_DAMAGE_LEVELS = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('catastrophic', 'Catastrophic'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_disasters')
    disaster_type = models.CharField(max_length=10, choices=DISASTER_TYPES)
    location = models.CharField(max_length=255, help_text="Descriptive location (e.g., street, area, landmark)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    severity = models.IntegerField(choices=SEVERITY_LEVELS)
    description = models.TextField()
    reported_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
    people_affected = models.IntegerField(blank=True, null=True)
    area_affected = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Area affected in square kilometers")
    infrastructure_damage = models.CharField(max_length=15, choices=INFRASTRUCTURE_DAMAGE_LEVELS, blank=True, null=True)

    def __str__(self):
        return f"{self.get_disaster_type_display()} at {self.location} ({self.latitude}, {self.longitude})"


class Shelter(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    capacity = models.IntegerField()
    current_occupancy = models.IntegerField(default=0)
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} at {self.address}"

    @property
    def availability(self):
        return max(0, self.capacity - self.current_occupancy)

    @property
    def is_full(self):
        return self.current_occupancy >= self.capacity

    @property
    def occupancy_percentage(self):
        if self.capacity > 0:
            return (self.current_occupancy / self.capacity) * 100
        return 0

class AidRequest(models.Model):
    AID_TYPES = [
        ('food', 'Food'),
        ('shelter', 'Shelter'),
        ('rescue', 'Rescue'),
        ('medical', 'Medical'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aid_requests')
    aid_type = models.CharField(max_length=10, choices=AID_TYPES)
    description = models.TextField()
    location = models.CharField(max_length=255, help_text="Descriptive location (e.g., street, area, landmark)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    num_people = models.IntegerField(default=1)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(default=timezone.now)
    shelter = models.ForeignKey(Shelter, on_delete=models.SET_NULL, null=True, blank=True, related_name='aid_requests')
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_aid_requests',
        limit_choices_to={'user_role': 'authority'},
        help_text='Authority user who approved or rejected this request.'
    )

    def __str__(self):
        return f"{self.get_aid_type_display()} request at {self.location} by {self.requester.username}"

class Skill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class VolunteerProfile(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile')
    skills = models.ManyToManyField(Skill)
    availability = models.CharField(max_length=15, choices=AVAILABILITY_CHOICES, default='available')

    def __str__(self):
        return f"{self.user.username}'s Volunteer Profile"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.user.user_role != 'volunteer':
            raise ValidationError('Only users with user_role="volunteer" can have a VolunteerProfile.')

class VolunteerAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    aid_request = models.ForeignKey(AidRequest, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='assigned')
    assigned_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Assignment for {self.volunteer.username} to {self.aid_request}"
