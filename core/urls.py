from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # 1. PUBLIC CORE URLs (Your Original Code)
    # ==========================================
    path('', views.home, name='home'),
    path('workers/<int:service_id>/', views.workers, name='workers'),

    # ==========================================
    # 2. AUTHENTICATION URLs (From ChatGPT)
    # ==========================================
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ==========================================
    # 3. PROTECTED BOOKING URLs
    # ==========================================
    path('book/<int:worker_id>/', views.book_worker, name='book_worker'),
   # ... inside your urlpatterns ...
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'), # ADD THIS LINE
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

# ==========================================
    # 4. WORKER MODULE URLs
    # ==========================================
    path('provider-dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('update-status/<int:booking_id>/<str:new_status>/', views.update_booking_status, name='update_status'),
    
    # ==========================================
    # 5. CUSTOM ADMIN URLs
    # ==========================================
    path('platform-admin/', views.admin_dashboard, name='admin_dashboard'),]