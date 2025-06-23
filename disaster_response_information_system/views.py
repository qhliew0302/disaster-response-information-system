# Liew Qian Hui 22063182
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, F
from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse

from .models import User, DisasterReport, AidRequest, VolunteerProfile, Skill, Shelter, VolunteerAssignment
from .forms import DisasterReportFilterForm, UserRegistrationForm, AidRequestForm, VolunteerProfileForm, DisasterReportForm, ShelterForm

# Helper functions
def is_authority(user):
    return user.is_authenticated and user.user_role == 'authority'

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def disaster_reports(request):
    """Disaster reports listing page with filtering"""
    # Initialize the filter form with GET parameters
    filter_form = DisasterReportFilterForm(request.GET or None)

    if request.user.is_authenticated and request.user.user_role == 'authority':
        reports = DisasterReport.objects.all()
    else:
        reports = DisasterReport.objects.filter(is_active=True)

    # Apply filters if form is valid
    if filter_form.is_valid():
        # Filter by disaster type
        if filter_form.cleaned_data['disaster_type']:
            reports = reports.filter(disaster_type=filter_form.cleaned_data['disaster_type'])

        # Filter by severity
        if filter_form.cleaned_data['severity']:
            reports = reports.filter(severity=filter_form.cleaned_data['severity'])

        # Filter by date range
        date_range = filter_form.cleaned_data['date_range']
        if date_range == 'today':
            today = timezone.now().date()
            reports = reports.filter(reported_at__date=today)
        elif date_range == 'week':
            one_week_ago = timezone.now() - timedelta(days=7)
            reports = reports.filter(reported_at__gte=one_week_ago)
        elif date_range == 'month':
            one_month_ago = timezone.now() - timedelta(days=30)
            reports = reports.filter(reported_at__gte=one_month_ago)

        # Filter by location (case-insensitive partial match)
        if filter_form.cleaned_data['location']:
            location_query = filter_form.cleaned_data['location']
            reports = reports.filter(location__icontains=location_query)

        # Sort results
        sort_by = filter_form.cleaned_data['sort_by']
        if sort_by == 'newest':
            reports = reports.order_by('-reported_at')
        elif sort_by == 'oldest':
            reports = reports.order_by('reported_at')
        elif sort_by == 'severity_high':
            reports = reports.order_by('-severity')
        elif sort_by == 'severity_low':
            reports = reports.order_by('severity')

    # Default sort by newest
    else:
        reports = reports.order_by('-reported_at')

    # Pagination
    paginator = Paginator(reports, 6)  # Show 6 reports per page
    page_number = request.GET.get('page', 1)
    reports = paginator.get_page(page_number)

    context = {
        'filter_form': filter_form,
        'reports': reports,
    }
    return render(request, 'disaster_reports.html', context)

def disaster_report_detail(request, report_id):
    """Detailed view of a specific disaster report"""
    # Authorities can view all reports, others only active reports
    if request.user.is_authenticated and request.user.user_role == 'authority':
        report = get_object_or_404(DisasterReport, pk=report_id)
    else:
        report = get_object_or_404(DisasterReport, pk=report_id, is_active=True)

    context = {
        'report': report
    }
    return render(request, 'disaster_report_details.html', context)

@login_required
@user_passes_test(is_authority)
def update_disaster_status(request, report_id):
    """Allow authorities to activate or deactivate a disaster report"""
    report = get_object_or_404(DisasterReport, pk=report_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'activate':
            report.is_active = True
            messages.success(request, f"The disaster report for {report.location} has been activated and is now publicly visible.")
        elif action == 'deactivate':
            report.is_active = False
            messages.success(request, f"The disaster report for {report.location} has been deactivated and is no longer publicly visible.")

        report.save()

    # Redirect back to the detail page
    return redirect('disaster_report_detail', report_id=report.id)

def shelters(request):
    """Shelters listing page with filtering"""
    # Start with all active shelters
    shelters_query = Shelter.objects.filter(is_active=True)

    # Handle filtering
    location_filter = request.GET.get('location', '')
    capacity_filter = request.GET.get('capacity', 'all')
    availability_filter = request.GET.get('availability', 'all')

    # Apply location filter (case-insensitive partial match)
    if location_filter:
        shelters_query = shelters_query.filter(
            Q(name__icontains=location_filter) |
            Q(address__icontains=location_filter)
        )

    # Apply capacity filter
    if capacity_filter == 'small':
        shelters_query = shelters_query.filter(capacity__lt=50)
    elif capacity_filter == 'medium':
        shelters_query = shelters_query.filter(capacity__gte=50, capacity__lte=100)
    elif capacity_filter == 'large':
        shelters_query = shelters_query.filter(capacity__gt=100)

    # Apply availability filter
    if availability_filter == 'available':
        shelters_query = shelters_query.exclude(current_occupancy__gte=F('capacity'))
    elif availability_filter == 'full':
        shelters_query = shelters_query.filter(current_occupancy__gte=F('capacity'))

    # Calculate shelter statistics
    total_shelters = shelters_query.count()
    available_shelters = shelters_query.exclude(current_occupancy__gte=F('capacity')).count()
    available_capacity = sum(
        max(0, shelter.capacity - shelter.current_occupancy)
        for shelter in shelters_query
    )

    context = {
        'shelters': shelters_query,
        'total_shelters': total_shelters,
        'available_shelters': available_shelters,
        'available_capacity': available_capacity,
        'location_filter': location_filter,
        'capacity_filter': capacity_filter,
        'availability_filter': availability_filter
    }

    return render(request, 'shelters.html', context)

def register(request):
    """User registration view"""
    initial_data = {}

    # Pre-select volunteer role if volunteer parameter is present
    if request.GET.get('volunteer') == 'true':
        initial_data['user_role'] = 'volunteer'

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)

            # Show different success message based on role
            if user.user_role == 'volunteer':
                messages.success(request, 'Registration successful! Please complete your volunteer profile.')
                return redirect('volunteer_profile')
            else:
                messages.success(request, 'Registration successful!')
                return redirect('home')
    else:
        form = UserRegistrationForm(initial=initial_data)

    return render(request, 'auth/register.html', {'form': form})

@login_required
def aid_request_create(request):
    """View for citizens to create aid requests"""
    # Check if user has citizen role
    if request.user.user_role != 'citizen':
        messages.error(request, 'Only citizens can submit aid requests.')
        return redirect('home')

    if request.method == 'POST':
        form = AidRequestForm(request.POST)
        if form.is_valid():
            aid_request = form.save(commit=False)
            aid_request.requester = request.user
            aid_request.save()
            messages.success(request, 'Aid request submitted successfully.')
            return redirect('my_aid_requests')
    else:
        form = AidRequestForm()

    return render(request, 'aid_request_create.html', {'form': form})

@login_required
def my_aid_requests(request):
    """View for citizens to see their aid requests"""
    if request.user.user_role != 'citizen':
        messages.error(request, 'Only citizens can access this page.')
        return redirect('home')

    aid_requests = AidRequest.objects.filter(requester=request.user).order_by('-requested_at')

    return render(request, 'my_aid_requests.html', {'aid_requests': aid_requests})

@login_required
def volunteer_profile(request):
    """View for volunteers to manage their profile and availability"""
    if request.user.user_role != 'volunteer':
        messages.error(request, 'Only volunteers can access this page.')
        return redirect('home')

    # Get or create volunteer profile
    profile, created = VolunteerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = VolunteerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Volunteer profile updated successfully.')
            return redirect('volunteer_profile')
    else:
        form = VolunteerProfileForm(instance=profile)

    return render(request, 'volunteer_profile.html', {'form': form})

@login_required
def my_assignments(request):
    """View for volunteers to see their assignments"""
    if request.user.user_role != 'volunteer':
        messages.error(request, 'Only volunteers can access this page.')
        return redirect('home')

    assignments = request.user.assignments.all().order_by('-assigned_at')

    return render(request, 'my_assignments.html', {'assignments': assignments})

@login_required
@user_passes_test(is_authority)
def admin_dashboard(request):
    """Admin dashboard for authority users"""
    # Count statistics
    total_reports = DisasterReport.objects.count()
    active_reports = DisasterReport.objects.filter(is_active=True).count()
    inactive_reports = total_reports - active_reports

    total_aid_requests = AidRequest.objects.count()
    pending_aid_requests = AidRequest.objects.filter(status='pending').count()
    volunteers_count = User.objects.filter(user_role='volunteer').count()
    available_volunteers = VolunteerProfile.objects.filter(availability='available').count()

    # Filter disaster reports
    filter_type = request.GET.get('filter_type', '')
    filter_severity = request.GET.get('filter_severity', '')
    filter_status = request.GET.get('filter_status', '')

    disaster_reports = DisasterReport.objects.all().order_by('-reported_at')

    if filter_type:
        disaster_reports = disaster_reports.filter(disaster_type=filter_type)
    if filter_severity:
        disaster_reports = disaster_reports.filter(severity=filter_severity)
    if filter_status == 'active':
        disaster_reports = disaster_reports.filter(is_active=True)
    elif filter_status == 'inactive':
        disaster_reports = disaster_reports.filter(is_active=False)

    # Filter aid requests
    aid_filter_type = request.GET.get('aid_filter_type', '')
    aid_filter_status = request.GET.get('aid_filter_status', '')

    aid_requests = AidRequest.objects.all().order_by('-requested_at')

    if aid_filter_type:
        aid_requests = aid_requests.filter(aid_type=aid_filter_type)
    if aid_filter_status:
        aid_requests = aid_requests.filter(status=aid_filter_status)

    # Filter shelters
    shelter_filter_status = request.GET.get('shelter_filter_status', '')
    shelter_filter_occupancy = request.GET.get('shelter_filter_occupancy', '')

    shelters = Shelter.objects.all()

    if shelter_filter_status == 'active':
        shelters = shelters.filter(is_active=True)
    elif shelter_filter_status == 'inactive':
        shelters = shelters.filter(is_active=False)

    if shelter_filter_occupancy == 'available':
        shelters = shelters.filter(current_occupancy__lt=F('capacity'))
    elif shelter_filter_occupancy == 'full':
        shelters = shelters.filter(current_occupancy__gte=F('capacity'))

    # Filter volunteers
    volunteer_filter_status = request.GET.get('volunteer_filter_status', '')
    volunteer_filter_skill = request.GET.get('volunteer_filter_skill', '')

    volunteers = VolunteerProfile.objects.select_related('user').all()

    if volunteer_filter_status == 'available':
        volunteers = volunteers.filter(availability='available')
    elif volunteer_filter_status == 'unavailable':
        volunteers = volunteers.filter(availability='unavailable')

    if volunteer_filter_skill:
        volunteers = volunteers.filter(skills__id=volunteer_filter_skill).distinct()

    # Get all skills for filter dropdown
    skills = Skill.objects.all()

    # Add disaster types and severity levels for filter dropdowns
    disaster_types = DisasterReport.DISASTER_TYPES
    severity_levels = DisasterReport.SEVERITY_LEVELS
    aid_status_choices = AidRequest.STATUS_CHOICES
    aid_types = AidRequest.AID_TYPES

    context = {
        'total_reports': total_reports,
        'active_reports': active_reports,
        'inactive_reports': inactive_reports,
        'total_aid_requests': total_aid_requests,
        'pending_aid_requests': pending_aid_requests,
        'volunteers_count': volunteers_count,
        'available_volunteers': available_volunteers,
        'disaster_reports': disaster_reports[:10],  # Limit to 10 for dashboard
        'aid_requests': aid_requests[:10],  # Limit to 10 for dashboard
        'shelters': shelters[:10],  # Limit to 10 for dashboard
        'volunteers': volunteers[:10],  # Limit to 10 for dashboard
        'skills': skills,
        # Filter values for maintaining state
        'filter_type': filter_type,
        'filter_severity': filter_severity,
        'filter_status': filter_status,
        'aid_filter_type': aid_filter_type,
        'aid_filter_status': aid_filter_status,
        'shelter_filter_status': shelter_filter_status,
        'shelter_filter_occupancy': shelter_filter_occupancy,
        'volunteer_filter_status': volunteer_filter_status,
        'volunteer_filter_skill': volunteer_filter_skill,
        # Add choices for dropdowns
        'disaster_types': disaster_types,
        'severity_levels': severity_levels,
        'aid_status_choices': aid_status_choices,
        'aid_types': aid_types,
    }

    return render(request, 'admin_dashboard.html', context)

def disaster_report_create(request):
    """View for citizens to create disaster reports"""
    # Check if user has citizen role
    if request.user.user_role != 'citizen':
        messages.error(request, 'Only citizens can submit disaster reports.')
        return redirect('home')

    if request.method == 'POST':
        form = DisasterReportForm(request.POST)
        if form.is_valid():
            disaster_report = form.save(commit=False)
            disaster_report.reporter = request.user
            disaster_report.save()
            messages.success(request, 'Disaster report submitted successfully.')
            return redirect('disaster_reports')
    else:
        form = DisasterReportForm()

    return render(request, 'disaster_report_create.html', {'form': form})

@login_required
def toggle_disaster_report_status(request, report_id):
    """Toggle a disaster report's active status"""
    if request.user.user_role != 'authority':
        messages.error(request, 'Only authorities can manage disaster reports.')
        return redirect('home')

    report = get_object_or_404(DisasterReport, pk=report_id)
    report.is_active = not report.is_active
    report.save()

    status = "activated" if report.is_active else "deactivated"
    messages.success(request, f'Disaster report has been {status}.')

    # Return to the previous page or admin dashboard
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

@login_required
def update_aid_request_status(request, request_id, new_status):
    """Update an aid request's status"""
    if request.user.user_role != 'authority':
        messages.error(request, 'Only authorities can manage aid requests.')
        return redirect('home')

    aid_request = get_object_or_404(AidRequest, pk=request_id)

    # Validate the status
    valid_statuses = [status[0] for status in AidRequest.STATUS_CHOICES]
    if new_status not in valid_statuses:
        messages.error(request, 'Invalid status update requested.')
        return redirect('admin_dashboard')

    aid_request.status = new_status

    # If approving or rejecting, set the authority
    if new_status in ['approved', 'rejected']:
        aid_request.approved_by = request.user

    aid_request.save()

    messages.success(request, f'Aid request has been updated to {new_status}.')

    # Return to the previous page or admin dashboard
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

@login_required
def shelter_create(request):
    """Create a new shelter (authority only)"""
    if request.user.user_role != 'authority':
        messages.error(request, 'Only authorities can create shelters.')
        return redirect('home')

    if request.method == 'POST':
        form = ShelterForm(request.POST)
        if form.is_valid():
            shelter = form.save()
            messages.success(request, f'Shelter "{shelter.name}" created successfully!')
            return redirect('admin_dashboard')
    else:
        form = ShelterForm()

    context = {
        'form': form,
        'title': 'Add New Shelter',
        'action': 'Create'
    }
    return render(request, 'shelter_form.html', context)

@login_required
def shelter_edit(request, shelter_id):
    """Edit an existing shelter (authority only)"""
    if request.user.user_role != 'authority':
        messages.error(request, 'Only authorities can edit shelters.')
        return redirect('home')

    shelter = get_object_or_404(Shelter, id=shelter_id)

    if request.method == 'POST':
        form = ShelterForm(request.POST, instance=shelter)
        if form.is_valid():
            form.save()
            messages.success(request, f'Shelter "{shelter.name}" updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = ShelterForm(instance=shelter)

    context = {
        'form': form,
        'title': f'Edit Shelter: {shelter.name}',
        'action': 'Update',
        'shelter': shelter
    }
    return render(request, 'shelter_form.html', context)

@login_required
def toggle_shelter_status(request, shelter_id):
    """Toggle a shelter's active status (authority only)"""
    if request.user.user_role != 'authority':
        messages.error(request, 'Only authorities can manage shelters.')
        return redirect('home')

    shelter = get_object_or_404(Shelter, id=shelter_id)
    shelter.is_active = not shelter.is_active
    shelter.save()

    status = "activated" if shelter.is_active else "deactivated"
    messages.success(request, f'Shelter "{shelter.name}" has been {status}.')

    return redirect('admin_dashboard')

@login_required
def assign_volunteer(request, volunteer_id):
    """Go to form to assign a volunteer to tasks"""
    if request.user.user_role != 'authority':
        messages.error(request, 'Only authorities can assign volunteers.')
        return redirect('home')

    try:
        # Get the volunteer profile
        volunteer = get_object_or_404(VolunteerProfile, user__id=volunteer_id)

        # Get approved aid requests that don't have assignments yet
        approved_requests = AidRequest.objects.filter(
            status='approved'
        ).exclude(
            assignments__isnull=False  # Exclude requests that already have assignments
        )

        if request.method == 'POST':
            aid_request_id = request.POST.get('aid_request_id')
            notes = request.POST.get('notes', '')

            try:
                # Get the aid request
                aid_request = AidRequest.objects.get(pk=aid_request_id)

                # Check if aid request is approved
                if aid_request.status != 'approved':
                    messages.error(request, 'Aid request must be approved before assigning volunteers.')
                    return redirect('assign_volunteer', volunteer_id=volunteer_id)

                # Create the assignment
                assignment = VolunteerAssignment(
                    volunteer=volunteer.user,
                    aid_request=aid_request,
                    assigned_by=request.user,
                    status='assigned',
                    notes=notes
                )
                assignment.save()

                # Update aid request status to in-progress
                aid_request.status = 'in_progress'
                aid_request.save()

                # Update volunteer availability
                volunteer.availability = 'unavailable'
                volunteer.save()

                messages.success(request, f'Task successfully assigned to {volunteer.user.get_full_name() or volunteer.user.username}.')
                return redirect('admin_dashboard')

            except AidRequest.DoesNotExist:
                messages.error(request, 'The selected aid request does not exist.')

        # Render the form
        context = {
            'volunteer': volunteer,
            'approved_requests': approved_requests,
        }
        return render(request, 'assign_volunteer.html', context)

    except VolunteerProfile.DoesNotExist:
        messages.error(request, 'Volunteer profile not found.')
        return redirect('admin_dashboard')

@login_required
@user_passes_test(is_authority)
def assign_volunteer_to_request(request):
    """Process the volunteer assignment form submission"""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('admin_dashboard')

    aid_request_id = request.POST.get('aid_request_id')
    volunteer_id = request.POST.get('volunteer_id')
    notes = request.POST.get('notes', '')

    # Validate input
    if not aid_request_id or not volunteer_id:
        messages.error(request, 'Missing required parameters.')
        return redirect('admin_dashboard')

    try:
        # Get objects
        aid_request = AidRequest.objects.get(pk=aid_request_id)
        volunteer = User.objects.get(pk=volunteer_id)

        # Check if volunteer has a volunteer profile
        if not hasattr(volunteer, 'volunteer_profile') or volunteer.user_role != 'volunteer':
            messages.error(request, 'Selected user is not a volunteer.')
            return redirect('admin_dashboard')

        # Check if aid request is approved
        if aid_request.status != 'approved':
            messages.error(request, 'Aid request must be approved before assigning volunteers.')
            return redirect('admin_dashboard')

        # Create the assignment
        assignment = VolunteerAssignment(
            volunteer=volunteer,
            aid_request=aid_request,
            assigned_by=request.user,
            status='assigned',
            notes=notes
        )
        assignment.save()

        # Update aid request status to in-progress
        aid_request.status = 'in_progress'
        aid_request.save()

        # Update volunteer availability
        volunteer_profile = volunteer.volunteer_profile
        volunteer_profile.availability = 'unavailable'
        volunteer_profile.save()

        messages.success(request, f'Volunteer {volunteer.get_full_name() or volunteer.username} has been assigned to the aid request.')
        return redirect('admin_dashboard')

    except AidRequest.DoesNotExist:
        messages.error(request, 'Aid request not found.')
    except User.DoesNotExist:
        messages.error(request, 'Volunteer not found.')
    except Exception as e:
        messages.error(request, f'Error assigning volunteer: {str(e)}')

    return redirect('admin_dashboard')

@login_required
def logout_view(request):
    """Custom logout view that supports both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def aid_request_detail(request, request_id):
    """Detailed view of a specific aid request"""
    # Check if user is authorized (authority or the requester)
    aid_request = get_object_or_404(AidRequest, pk=request_id)

    if not (request.user.user_role == 'authority' or request.user == aid_request.requester):
        messages.error(request, 'You do not have permission to view this aid request.')
        return redirect('home')

    context = {
        'aid_request': aid_request
    }
    return render(request, 'aid_request_detail.html', context)

# API Endpoints
@login_required
@user_passes_test(is_authority)
def api_aid_request_detail(request, request_id):
    """API endpoint to get aid request details in JSON format"""
    aid_request = get_object_or_404(AidRequest, pk=request_id)

    data = {
        'id': aid_request.id,
        'aid_type': aid_request.aid_type,
        'get_aid_type_display': aid_request.get_aid_type_display(),
        'status': aid_request.status,
        'get_status_display': aid_request.get_status_display(),
        'location': aid_request.location,
        'num_people': aid_request.num_people,
        'description': aid_request.description,
        'contact_info': aid_request.contact_info if hasattr(aid_request, 'contact_info') else '',
        'requested_at': aid_request.requested_at.strftime('%b %d, %Y %H:%M'),
        'requester_name': aid_request.requester.get_full_name() or aid_request.requester.username
    }

    return JsonResponse(data)

@login_required
@user_passes_test(is_authority)
def api_available_volunteers(request, request_id):
    """API endpoint to get available volunteers suitable for an aid request"""
    aid_request = get_object_or_404(AidRequest, pk=request_id)

    # Get volunteers that are available
    available_volunteers = VolunteerProfile.objects.filter(
        availability='available'
    ).select_related('user')

    volunteers_data = []
    for volunteer in available_volunteers:
        skills = [skill.name for skill in volunteer.skills.all()]
        volunteers_data.append({
            'id': volunteer.user.id,  # Use user ID for the assignment
            'name': volunteer.user.get_full_name() or volunteer.user.username,
            'skills': skills,
            'rating': getattr(volunteer, 'rating', None),
            'assignments_count': VolunteerAssignment.objects.filter(volunteer=volunteer.user).count()
        })

    return JsonResponse(volunteers_data, safe=False)

@login_required
@user_passes_test(is_authority)
def api_volunteer_profile(request, volunteer_id):
    """API endpoint to get volunteer profile details in JSON format"""
    volunteer_profile = get_object_or_404(VolunteerProfile, pk=volunteer_id)
    user = volunteer_profile.user

    # Get assignments for this volunteer
    assignments = VolunteerAssignment.objects.filter(volunteer=user).select_related('aid_request')

    assignments_data = []
    for assignment in assignments:
        assignments_data.append({
            'id': assignment.id,
            'aid_type': assignment.aid_request.get_aid_type_display(),
            'location': assignment.aid_request.location,
            'status': assignment.status,
            'status_display': dict(VolunteerAssignment.STATUS_CHOICES)[assignment.status],
            'assigned_at': assignment.assigned_at.strftime('%b %d, %Y %H:%M'),
            'completed_at': assignment.completed_at.strftime('%b %d, %Y %H:%M') if assignment.completed_at else None,
        })

    data = {
        'id': volunteer_profile.id,
        'username': user.username,
        'full_name': user.get_full_name(),
        'email': user.email,
        'phone': user.phone,
        'address': user.address,
        'date_joined': user.date_joined.strftime('%b %d, %Y'),
        'availability': volunteer_profile.availability,
        'availability_display': dict(VolunteerProfile.AVAILABILITY_CHOICES)[volunteer_profile.availability],
        'skills': [skill.name for skill in volunteer_profile.skills.all()],
        'assignment_count': assignments.count(),
        'assignments': assignments_data,
    }

    return JsonResponse(data)

@login_required
def update_assignment_status(request, assignment_id, new_status):
    """Update a volunteer assignment's status"""
    # Only volunteers can update their own assignments
    if request.user.user_role != 'volunteer':
        messages.error(request, 'Only volunteers can update assignment status.')
        return redirect('home')

    # Get the assignment
    assignment = get_object_or_404(VolunteerAssignment, pk=assignment_id)

    # Check if the assignment belongs to this volunteer
    if assignment.volunteer != request.user:
        messages.error(request, 'You can only update your own assignments.')
        return redirect('my_assignments')

    # Validate the new status
    valid_statuses = [status[0] for status in VolunteerAssignment.STATUS_CHOICES]
    if new_status not in valid_statuses:
        messages.error(request, 'Invalid status update requested.')
        return redirect('my_assignments')

    # Only allow progression: assigned -> in_progress -> completed
    current_status = assignment.status
    if (current_status == 'assigned' and new_status != 'in_progress') or \
       (current_status == 'in_progress' and new_status != 'completed'):
        messages.error(request, 'Invalid status change requested.')
        return redirect('my_assignments')

    # Update the assignment
    assignment.status = new_status

    # If marking as completed, set the completed date
    if new_status == 'completed':
        assignment.completed_at = timezone.now()

        # Also mark the aid request as completed
        if assignment.aid_request.status == 'in_progress':
            assignment.aid_request.status = 'completed'
            assignment.aid_request.save()

        # Update volunteer availability back to available
        volunteer_profile = request.user.volunteer_profile
        volunteer_profile.availability = 'available'
        volunteer_profile.save()

    assignment.save()

    # Send success message
    if new_status == 'in_progress':
        messages.success(request, 'Assignment has been marked as in progress.')
    elif new_status == 'completed':
        messages.success(request, 'Assignment has been marked as completed. Thank you for your service!')

    return redirect('my_assignments')


