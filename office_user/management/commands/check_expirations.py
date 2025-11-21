from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from office_user.models import VehicleMaster, Notification, UserNotificationSettings
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Checks for vehicle document expirations and creates notifications'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Expiry checks configuration
        expiry_configs = [
            {'days': 90, 'field': 'truck_registration_expiry_date', 'type': 'truck'},
            {'days': 30, 'field': 'insurance_registration_expiry_date', 'type': 'insurance'},
            {'days': 45, 'field': 'mulkia_registration_expiry_date', 'type': 'mulkia'},
            {'days': 60, 'field': 'permit_registration_expiry_date', 'type': 'permit'},
        ]

        for config in expiry_configs:
            expiry_date = today + timedelta(days=config['days'])
            filter_kwargs = {
                f"{config['field']}__lte": expiry_date,
                f"{config['field']}__gte": today
            }
            expiring_vehicles = VehicleMaster.objects.filter(**filter_kwargs)

            for vehicle in expiring_vehicles:
                users_to_notify = User.objects.filter(groups__name='office_user')
                for user in users_to_notify:
                    settings, created = UserNotificationSettings.objects.get_or_create(user=user)
                    
                    # Check if user has enabled this notification type
                    if getattr(settings, f"{config['type']}_expiry_notifications", True):
                        # Check if a notification already exists
                        existing_notification = Notification.objects.filter(
                            user=user,
                            vehicle=vehicle,
                            notification_type=config['type']
                        ).first()

                        if not existing_notification:
                            message = f"The {config['type'].replace('_', ' ')} for vehicle {vehicle.plate_number} is expiring on {getattr(vehicle, config['field'])}."
                            Notification.objects.create(
                                user=user,
                                vehicle=vehicle,
                                notification_type=config['type'],
                                message=message
                            )
                            self.stdout.write(self.style.SUCCESS(f"Notification created for {user.username} for vehicle {vehicle.plate_number}"))

