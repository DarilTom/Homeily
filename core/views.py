# Add this to your imports at the top
from django.contrib.admin.views.decorators import staff_member_required
from .forms import UserUpdateForm, ProfileUpdateForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Service, Worker, Booking, UserProfile # Ensure UserProfile is imported!
from django.core.exceptions import ObjectDoesNotExist

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Grab the new additional details
        email = request.POST.get('email', '')
        first_name = request.POST.get('first_name', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        # 1. Create the core Django User (handles pass, email, name)
        user = User.objects.create_user(
            username=username, 
            password=password, 
            email=email, 
            first_name=first_name
        )
        
        # 2. Create the linked UserProfile (handles phone, address)
        UserProfile.objects.create(user=user, phone=phone, address=address)

        # Log them in automatically
        login(request, user)
        return redirect('home')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ==========================================
# 2. PUBLIC CORE VIEWS (Your Original Code)
# ==========================================

def home(request):
    # --- ADD THIS NEW TRAFFIC COP BLOCK ---
    if request.user.is_authenticated:
        # 1. If they are an Admin, detour to Command Center
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
        
        # 2. If they are a Worker, detour to Provider Portal
        if hasattr(request.user, 'worker'):
            return redirect('worker_dashboard')
    services = Service.objects.all()
    return render(request, 'home.html', {'services': services})

def workers(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    workers = Worker.objects.filter(service=service)
    return render(request, 'workers.html', {'workers': workers, 'service': service})

# ==========================================
# 3. PROTECTED USER VIEWS
# ==========================================

@login_required(login_url='login')
def book_worker(request, worker_id):
    worker = get_object_or_404(Worker, id=worker_id)
    
    if request.method == 'POST':
        # Retrieve the datetime string from the HTML form
        booking_date = request.POST.get('booking_date')
        
        if booking_date:
            # Create the record in the MySQL database
            Booking.objects.create(
                user=request.user,
                worker=worker,
                booking_date=booking_date,
                status='Pending'
            )
            return redirect('dashboard')
            
    return render(request, 'booking.html', {'worker': worker})

@login_required(login_url='login')
def dashboard(request):
    # 1. NEW: Check if this user is an Administrator
    if request.user.is_superuser or request.user.is_staff:
        return redirect('admin_dashboard')

    # 2. Check if this user is linked to a Worker profile
    if hasattr(request.user, 'worker'):
        return redirect('worker_dashboard')

    # 3. Otherwise, they are a regular Customer
    try:
        profile = request.user.userprofile
    except ObjectDoesNotExist:
        profile = None

    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'dashboard.html', {'profile': profile, 'bookings': bookings})


# ==========================================
# NEW ADMIN DASHBOARD VIEW
# ==========================================
@staff_member_required(login_url='login')
def admin_dashboard(request):
    # Gather analytics for the platform
    total_customers = User.objects.filter(is_superuser=False, worker__isnull=True).count()
    total_workers = Worker.objects.count()
    total_bookings = Booking.objects.count()
    
    # Get the 5 most recent bookings to display
    recent_bookings = Booking.objects.all().order_by('-booking_date')[:5]
    
    context = {
        'total_customers': total_customers,
        'total_workers': total_workers,
        'total_bookings': total_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required(login_url='login')
def cancel_booking(request, booking_id):
    # Allow a user to cancel their own booking
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.status = 'Cancelled'
    booking.save()
    return redirect('dashboard')

@login_required(login_url='login')
def edit_profile(request):
    # Safely get the user's profile, or create a blank one if it doesn't exist yet
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Load the forms with the new POST data AND the existing user instance
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('dashboard') # Send them back to the dashboard when done
    else:
        # If it's a GET request, just load the forms with their current data
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    return render(request, 'edit_profile.html', {'u_form': u_form, 'p_form': p_form})

@login_required(login_url='login')
def worker_dashboard(request):
    # Check if the logged-in user is linked to a Worker profile
    if hasattr(request.user, 'worker'):
        worker_profile = request.user.worker
        # Get all bookings assigned to this specific worker
        bookings = Booking.objects.filter(worker=worker_profile).order_by('-booking_date')
        return render(request, 'worker_dashboard.html', {'bookings': bookings, 'worker': worker_profile})
    else:
        # If they are just a regular customer, send them away to the normal dashboard
        return redirect('dashboard')

@login_required(login_url='login')
def update_booking_status(request, booking_id, new_status):
    # Only allow linked workers to update statuses
    if hasattr(request.user, 'worker'):
        worker_profile = request.user.worker
        # Securely grab the booking (ensuring it actually belongs to this worker)
        booking = get_object_or_404(Booking, id=booking_id, worker=worker_profile)
        
        valid_statuses = ['Accepted', 'Completed', 'Cancelled']
        if new_status in valid_statuses:
            booking.status = new_status
            booking.save()
            
    return redirect('worker_dashboard')