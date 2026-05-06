from django.contrib import admin
from .models import Service, Worker, Booking

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'service', 'phone', 'experience')
    list_filter = ('service',)
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'worker', 'booking_date', 'status')
    list_filter = ('status', 'booking_date')
    search_fields = ('user__username', 'worker__name')
    
admin.site.site_header = "Home Service Admin"
admin.site.site_title = "Home Service Portal"
admin.site.index_title = "Admin Dashboard"