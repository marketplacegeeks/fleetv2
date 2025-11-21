from django.db import migrations


def seed_dropdowns(apps, schema_editor):
    VehicleCapacity = apps.get_model("office_user", "VehicleCapacity")
    VehicleType = apps.get_model("office_user", "VehicleType")
    ToteCapacity = apps.get_model("office_user", "ToteCapacity")
    Status = apps.get_model("office_user", "Status")
    VehicleConcept = apps.get_model("office_user", "VehicleConcept")
    Make = apps.get_model("office_user", "Make")
    Emirate = apps.get_model("office_user", "Emirate")
    GPS = apps.get_model("office_user", "GPS")
    BrandingStatus = apps.get_model("office_user", "BrandingStatus")
    TailLiftBrand = apps.get_model("office_user", "TailLiftBrand")

    # Vehicle Capacity
    for name in ["3.5 Ton", "7 Ton", "4.2 Ton"]:
        VehicleCapacity.objects.get_or_create(name=name)

    # Vehicle Type
    for name in ["GOH", "Flat"]:
        VehicleType.objects.get_or_create(name=name)

    # Tote Capacity
    for name in ["200 Totes", "160 Totes", "150 Totes"]:
        ToteCapacity.objects.get_or_create(name=name)

    # Status (corrected spelling to "Discontinued Permanently")
    for name in ["Active", "Temporary Discontinue", "Discontinued Permanently"]:
        Status.objects.get_or_create(name=name)

    # Vehicle Concept
    for name in ["Babyshop", "Splash", "Lifestyle", "Max", "Shoemart", "LRIL-Max AUD", "LRIL-Max DXB"]:
        VehicleConcept.objects.get_or_create(name=name)

    # Make
    for name in ["ISUZU", "Mitsubishi Canter", "Mitsubishi Fuso"]:
        Make.objects.get_or_create(name=name)

    # Emirates
    for name in ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"]:
        Emirate.objects.get_or_create(name=name)

    # GPS
    for name in ["Samtech", "Telematics"]:
        GPS.objects.get_or_create(name=name)

    # Branding Status
    for name in [
        "Old Branding",
        "Proposed for CP Branding",
        "No Branding",
        "Babyshop Branding",
        "Splash Branding",
        "Proposed Max Branding",
        "Lifestyle Branding",
    ]:
        BrandingStatus.objects.get_or_create(name=name)

    # Tail Lift Brand
    for name in ["Dhollandia", "Dautel"]:
        TailLiftBrand.objects.get_or_create(name=name)


def unseed_dropdowns(apps, schema_editor):
    # No-op: keep seeded values if migration is reversed
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("office_user", "0002_alter_brandingstatus_options_alter_emirate_options_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_dropdowns, reverse_code=unseed_dropdowns),
    ]
