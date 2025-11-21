from django.db import models
from django.contrib.auth.models import User

class VehicleCapacity(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Vehicle capacity"
        verbose_name_plural = "Vehicle capacitys"

    def __str__(self):
        return self.name

class VehicleType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Vehicle type"
        verbose_name_plural = "Vehicle types"

    def __str__(self):
        return self.name

class ToteCapacity(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Tote capacity"
        verbose_name_plural = "Tote capacitys"

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuss"

    def __str__(self):
        return self.name

class VehicleConcept(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Vehicle concept"
        verbose_name_plural = "Vehicle concepts"

    def __str__(self):
        return self.name

class Make(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Make"
        verbose_name_plural = "Makes"

    def __str__(self):
        return self.name

class Emirate(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Emirate"
        verbose_name_plural = "Emirates"

    def __str__(self):
        return self.name

class GPS(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "GPS"
        verbose_name_plural = "GPSs"

    def __str__(self):
        return self.name

class BrandingStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Branding status"
        verbose_name_plural = "Branding statuss"

    def __str__(self):
        return self.name

class TailLiftBrand(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Tail lift brand"
        verbose_name_plural = "Tail lift brands"

    def __str__(self):
        return self.name

class VehicleMaster(models.Model):
    class Meta:
        verbose_name = "Vehicle master"
        verbose_name_plural = "Vehicle masters"

    chassis_number = models.CharField(max_length=100, primary_key=True, unique=True)
    plate_number = models.CharField(max_length=50, unique=True)
    vehicle_capacity = models.ForeignKey(VehicleCapacity, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    tote_capacity = models.ForeignKey(ToteCapacity, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    vehicle_concept = models.ForeignKey(VehicleConcept, on_delete=models.CASCADE)
    make = models.ForeignKey(Make, on_delete=models.CASCADE)
    truck_reg_date = models.DateField()
    truck_registration_expiry_date = models.DateField(null=True, blank=True)
    insurance_document = models.FileField(upload_to='documents/')
    insurance_registration_date = models.DateField()
    insurance_registration_expiry_date = models.DateField(null=True, blank=True)
    mulkia_registration_date = models.DateField()
    mulkia_registration_expiry_date = models.DateField(null=True, blank=True)
    mulkia_document = models.FileField(upload_to='documents/')
    emirates_permit = models.ManyToManyField(Emirate)
    permit_registration_date = models.DateField()
    permit_registration_expiry_date = models.DateField(null=True, blank=True)
    permit_document = models.FileField(upload_to='documents/')
    tl_no = models.IntegerField()
    tc_no = models.IntegerField()
    tc_owner = models.CharField(max_length=100)
    salik_account_no = models.CharField(max_length=100)
    salik_tag_no = models.CharField(max_length=100)
    darb_ac_no = models.CharField(max_length=100)
    gps = models.ForeignKey(GPS, on_delete=models.CASCADE)
    branding_status = models.ForeignKey(BrandingStatus, on_delete=models.CASCADE)
    lift_gate = models.BooleanField()
    tail_lift_brand = models.ForeignKey(TailLiftBrand, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True, null=True)
    truck_photos = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.chassis_number

class ChangeLog(models.Model):
    class Meta:
        verbose_name = "Change log"
        verbose_name_plural = "Change logs"
        db_table = "change_log"

    date = models.DateField()
    time = models.TimeField()
    chassis_number = models.CharField(max_length=100, blank=True, null=True)
    plate_number = models.CharField(max_length=50, blank=True, null=True)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.date} {self.time} {self.field_name}"

class Notification(models.Model):
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('snoozed', 'Snoozed'),
    ]

    NOTIFICATION_TYPE_CHOICES = [
        ('insurance', 'Insurance Expiry'),
        ('mulkia', 'Mulkia Expiry'),
        ('permit', 'Permit Expiry'),
        ('truck', 'Truck Registration Expiry'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(VehicleMaster, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    created_at = models.DateTimeField(auto_now_add=True)
    snoozed_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.vehicle.plate_number} - {self.get_notification_type_display()}"

class UserNotificationSettings(models.Model):
    class Meta:
        verbose_name = "User Notification Setting"
        verbose_name_plural = "User Notification Settings"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    insurance_expiry_notifications = models.BooleanField(default=True)
    mulkia_expiry_notifications = models.BooleanField(default=True)
    permit_expiry_notifications = models.BooleanField(default=True)
    truck_registration_expiry_notifications = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification settings for {self.user.username}"
