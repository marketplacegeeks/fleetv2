from django.contrib import admin
from .models import (
    VehicleCapacity,
    VehicleType,
    ToteCapacity,
    Status,
    VehicleConcept,
    Make,
    Emirate,
    GPS,
    BrandingStatus,
    TailLiftBrand,
    VehicleMaster,
    Notification,
    UserNotificationSettings,
)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'notification_type', 'status', 'created_at', 'snoozed_until')
    list_filter = ('status', 'notification_type', 'created_at')
    search_fields = ('user__username', 'vehicle__plate_number')

@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'insurance_expiry_notifications', 'mulkia_expiry_notifications', 'permit_expiry_notifications', 'truck_registration_expiry_notifications')
    search_fields = ('user__username',)

admin.site.register(VehicleCapacity)
admin.site.register(VehicleType)
admin.site.register(ToteCapacity)
admin.site.register(Status)
admin.site.register(VehicleConcept)
admin.site.register(Make)
admin.site.register(Emirate)
admin.site.register(GPS)
admin.site.register(BrandingStatus)
admin.site.register(TailLiftBrand)

class VehicleMasterAdmin(admin.ModelAdmin):
    list_display = [
        "chassis_number",
        "plate_number",
        "truck_reg_date",
        "truck_registration_expiry_date",
        "insurance_registration_date",
        "insurance_registration_expiry_date",
        "mulkia_registration_date",
        "mulkia_registration_expiry_date",
        "permit_registration_date",
        "permit_registration_expiry_date",
    ]

admin.site.register(VehicleMaster, VehicleMasterAdmin)
