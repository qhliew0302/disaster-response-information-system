# Liew Qian Hui, 22063182

from django import forms
from .models import DisasterReport, AidRequest, VolunteerProfile, Skill, User, Shelter

class DisasterReportFilterForm(forms.Form):
    """Form for filtering disaster reports"""

    # Filter by disaster type
    disaster_type = forms.ChoiceField(
        choices=[('', 'All Types')] + DisasterReport.DISASTER_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Filter by severity
    severity = forms.ChoiceField(
        choices=[('', 'All Levels')] + DisasterReport.SEVERITY_LEVELS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Filter by time period
    DATE_RANGES = [
        ('', 'All Time'),
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month')
    ]
    date_range = forms.ChoiceField(
        choices=DATE_RANGES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Filter by location
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter location'
        })
    )

    # Sorting options
    SORT_OPTIONS = [
        ('date_desc', 'Date (Newest First)'),
        ('date_asc', 'Date (Oldest First)'),
        ('severity_desc', 'Severity (Highest First)'),
        ('severity_asc', 'Severity (Lowest First)')
    ]
    sort_by = forms.ChoiceField(
        choices=SORT_OPTIONS,
        required=False,
        initial='date_desc',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class AidRequestForm(forms.ModelForm):
    """Form for submitting aid requests"""
    class Meta:
        model = AidRequest
        fields = ['aid_type', 'description', 'location', 'latitude', 'longitude', 'num_people']
        widgets = {
            'aid_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe what kind of aid you need...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your location'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Latitude (e.g., 3.1390)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Longitude (e.g., 101.6869)'}),
            'num_people': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        labels = {
            'num_people': 'Number of People Requiring Aid'
        }

class VolunteerProfileForm(forms.ModelForm):
    """Form for volunteers to register their availability and skills"""
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = VolunteerProfile
        fields = ['availability', 'skills']
        widgets = {
            'availability': forms.Select(attrs={'class': 'form-select'})
        }

class UserRegistrationForm(forms.ModelForm):
    """Form for user registration"""
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    # Override user_role field to exclude 'authority' option
    user_role = forms.ChoiceField(
        choices=[
            ('citizen', 'Citizen'),
            ('volunteer', 'Volunteer'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_role', 'phone', 'address')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class DisasterReportForm(forms.ModelForm):
    """Form for reporting disasters"""
    class Meta:
        model = DisasterReport
        fields = ['disaster_type', 'severity', 'location', 'latitude', 'longitude', 'description']
        widgets = {
            'disaster_type': forms.Select(attrs={'class': 'form-select'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the location of the disaster'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Latitude (e.g., 3.1390)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Longitude (e.g., 101.6869)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the disaster in detail...'}),
        }

class ShelterForm(forms.ModelForm):
    """Form for creating and editing shelter information"""
    class Meta:
        model = Shelter
        fields = ['name', 'address', 'latitude', 'longitude', 'capacity',
                  'current_occupancy', 'contact_info', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Shelter name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Latitude (e.g., 3.1390)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Longitude (e.g., 101.6869)'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'current_occupancy': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact information for shelter'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_active': 'Active Shelter'
        }

    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get('capacity')
        current_occupancy = cleaned_data.get('current_occupancy')

        if capacity and current_occupancy and current_occupancy > capacity:
            raise forms.ValidationError("Current occupancy cannot exceed capacity")

        return cleaned_data
