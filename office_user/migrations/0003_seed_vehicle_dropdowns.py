from django.db import migrations


def seed_dropdowns(apps, schema_editor):
    VehicleCapacity = apps.get_model("office_user", "VehicleCapacity")
    VehicleType = apps.get_model("office_user", "VehicleType")
    ToteCapacity = apps.get_model("office_user", "ToteCapacity")
    Status = apps.get_model("office_user", "Status")
    VehicleConcept = apps.get_model("office_user", "VehicleConcept")
    Make = apps.get_model("office_user", "Make")
    Emirate = apps.get_model("office_user", "Emirate")

    capacities = ["3.5 Ton", "7 Ton", "4.2 Ton"]
    types = ["GOH", "Flat"]
    totes = ["200 Totes", "160 Totes", "150 Totes"]
    # Corrected typo per your instruction
    statuses = ["Active", "Temporary Discontinue", "Discontinued Permanently"]
    concepts = ["Babyshop", "Splash", "Lifestyle", "Max", "Shoemart", "LRIL-Max AUD", "LRIL-Max DXB"]
    makes = ["ISUZU", "Mitsubishi Canter", "Mitsubishi Fuso"]
    emirates = ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"]

    for name in capacities:
        VehicleCapacity.objects.get_or_create(name=name)
    for name in types:
        VehicleType.objects.get_or_create(name=name)
    for name in totes:
        ToteCapacity.objects.get_or_create(name=name)
    for name in statuses:
        Status.objects.get_or_create(name=name)
    for name in concepts:
        VehicleConcept.objects.get_or_create(name=name)
    for name in makes:
        Make.objects.get_or_create(name=name)
    for name in emirates:
        Emirate.objects.get_or_create(name=name)


def unseed_dropdowns(apps, schema_editor):
    VehicleCapacity = apps.get_model("office_user", "VehicleCapacity")
    VehicleType = apps.get_model("office_user", "VehicleType")
    ToteCapacity = apps.get_model("office_user", "ToteCapacity")
    Status = apps.get_model("office_user", "Status")
    VehicleConcept = apps.get_model("office_user", "VehicleConcept")
    Make = apps.get_model("office_user", "Make")
    Emirate = apps.get_model("office_user", "Emirate")

    names_map = {
        VehicleCapacity: ["3.5 Ton", "7 Ton", "4.2 Ton"],
        VehicleType: ["GOH", "Flat"],
        ToteCapacity: ["200 Totes", "160 Totes", "150 Totes"],
        Status: ["Active", "Temporary Discontinue", "Discontinued Permanently"],
        VehicleConcept: ["Babyshop", "Splash", "Lifestyle", "Max", "Shoemart", "LRIL-Max AUD", "LRIL-Max DXB"],
        Make: ["ISUZU", "Mitsubishi Canter", "Mitsubishi Fuso"],
        Emirate: ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"],
    }

    for Model, names in names_map.items():
        Model.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("office_user", "0002_alter_brandingstatus_options_alter_emirate_options_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_dropdowns, unseed_dropdowns),
    ]
