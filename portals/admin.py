from django.contrib import admin
from .models import Portal, PortalAvailability


@admin.register(Portal)
class PortalAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'user', 'position', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['title', 'url', 'description']
    ordering = ['position', '-created_at']


@admin.register(PortalAvailability)
class PortalAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['portal', 'timestamp', 'is_available', 'response_time', 'status_code']
    list_filter = ['is_available', 'timestamp', 'portal']
    ordering = ['-timestamp']
