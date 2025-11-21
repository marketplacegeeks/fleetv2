from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.dateparse import parse_date
from datetime import date, datetime
import json
import csv
from django.urls import reverse

from .models import (
    VehicleMaster,
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
    ChangeLog,
    Notification,
    UserNotificationSettings,
)
from django.utils import timezone
from datetime import timedelta

class LoginView(View):
    def get(self, request):
        return render(request, 'login_page.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.groups.filter(name='office_user').exists():
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid credentials or not an office user.')
            return render(request, 'login_page.html')

def homepage(request):
    return render(request, 'homepage.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def vehicle_master(request):
    return render(request, 'vehicle_master.html')

@login_required(login_url='login')
def vehicle_update(request, chassis_number):
    change_logs = ChangeLog.objects.filter(chassis_number=chassis_number).order_by('-date', '-time')
    context = {
        'chassis_number': chassis_number,
        'change_logs': change_logs,
    }
    return render(request, 'vehicle_update.html', context)

@login_required(login_url='login')
def vehicle_create(request):
    return render(request, 'vehicle_create.html')

@login_required(login_url='login')
def vehicle_edit_partial(request):
    # Returns the edit form partial to be loaded into the modal via AJAX
    return render(request, 'vehicle_edit_partial.html')

def change_log(request):
    logs = ChangeLog.objects.order_by('-date', '-time')
    return render(request, 'change_log.html', {'change_logs': logs})

# -------------------------------
# Vehicle Master JSON API (GET, POST, PUT)
# -------------------------------

def _file_url_or_none(field_file):
    try:
        return field_file.url if field_file else None
    except Exception:
        return None

def serialize_vehicle(v: VehicleMaster):
    return {
        "chassis_number": v.chassis_number,
        "plate_number": v.plate_number,
        "vehicle_capacity": {
            "id": v.vehicle_capacity_id,
            "name": v.vehicle_capacity.name if v.vehicle_capacity_id else None,
        },
        "vehicle_type": {
            "id": v.vehicle_type_id,
            "name": v.vehicle_type.name if v.vehicle_type_id else None,
        },
        "tote_capacity": {
            "id": v.tote_capacity_id,
            "name": v.tote_capacity.name if v.tote_capacity_id else None,
        },
        "status": {
            "id": v.status_id,
            "name": v.status.name if v.status_id else None,
        },
        "vehicle_concept": {
            "id": v.vehicle_concept_id,
            "name": v.vehicle_concept.name if v.vehicle_concept_id else None,
        },
        "make": {
            "id": v.make_id,
            "name": v.make.name if v.make_id else None,
        },
        "truck_reg_date": v.truck_reg_date.isoformat() if v.truck_reg_date else None,
        "truck_registration_expiry_date": v.truck_registration_expiry_date.isoformat() if v.truck_registration_expiry_date else None,
        "insurance_document_url": _file_url_or_none(v.insurance_document),
        "insurance_registration_date": v.insurance_registration_date.isoformat() if v.insurance_registration_date else None,
        "insurance_registration_expiry_date": v.insurance_registration_expiry_date.isoformat() if v.insurance_registration_expiry_date else None,
        "mulkia_registration_date": v.mulkia_registration_date.isoformat() if v.mulkia_registration_date else None,
        "mulkia_registration_expiry_date": v.mulkia_registration_expiry_date.isoformat() if v.mulkia_registration_expiry_date else None,
        "mulkia_document_url": _file_url_or_none(v.mulkia_document),
        "emirates_permit": [{"id": e.id, "name": e.name} for e in v.emirates_permit.all()],
        "permit_registration_date": v.permit_registration_date.isoformat() if v.permit_registration_date else None,
        "permit_registration_expiry_date": v.permit_registration_expiry_date.isoformat() if v.permit_registration_expiry_date else None,
        "permit_document_url": _file_url_or_none(v.permit_document),
        "tl_no": v.tl_no,
        "tc_no": v.tc_no,
        "tc_owner": v.tc_owner,
        "salik_account_no": v.salik_account_no,
        "salik_tag_no": v.salik_tag_no,
        "darb_ac_no": v.darb_ac_no,
        "gps": {
            "id": v.gps_id,
            "name": v.gps.name if v.gps_id else None,
        },
        "branding_status": {
            "id": v.branding_status_id,
            "name": v.branding_status.name if v.branding_status_id else None,
        },
        "lift_gate": v.lift_gate,
        "tail_lift_brand": {
            "id": v.tail_lift_brand_id,
            "name": v.tail_lift_brand.name if v.tail_lift_brand_id else None,
        },
        "remarks": v.remarks,
        "truck_photos_url": _file_url_or_none(v.truck_photos),
    }

def _snapshot_vehicle(v: VehicleMaster):
    return {
        "plate_number": v.plate_number,
        "vehicle_capacity": v.vehicle_capacity.name if v.vehicle_capacity_id else "",
        "vehicle_type": v.vehicle_type.name if v.vehicle_type_id else "",
        "tote_capacity": v.tote_capacity.name if v.tote_capacity_id else "",
        "status": v.status.name if v.status_id else "",
        "vehicle_concept": v.vehicle_concept.name if v.vehicle_concept_id else "",
        "make": v.make.name if v.make_id else "",
        "truck_reg_date": v.truck_reg_date.isoformat() if v.truck_reg_date else "",
        "truck_registration_expiry_date": v.truck_registration_expiry_date.isoformat() if v.truck_registration_expiry_date else "",
        "insurance_registration_date": v.insurance_registration_date.isoformat() if v.insurance_registration_date else "",
        "insurance_registration_expiry_date": v.insurance_registration_expiry_date.isoformat() if v.insurance_registration_expiry_date else "",
        "mulkia_registration_date": v.mulkia_registration_date.isoformat() if v.mulkia_registration_date else "",
        "mulkia_registration_expiry_date": v.mulkia_registration_expiry_date.isoformat() if v.mulkia_registration_expiry_date else "",
        "permit_registration_date": v.permit_registration_date.isoformat() if v.permit_registration_date else "",
        "permit_registration_expiry_date": v.permit_registration_expiry_date.isoformat() if v.permit_registration_expiry_date else "",
        "tl_no": str(v.tl_no) if v.tl_no is not None else "",
        "tc_no": str(v.tc_no) if v.tc_no is not None else "",
        "tc_owner": v.tc_owner or "",
        "salik_account_no": v.salik_account_no or "",
        "salik_tag_no": v.salik_tag_no or "",
        "darb_ac_no": v.darb_ac_no or "",
        "gps": v.gps.name if v.gps_id else "",
        "branding_status": v.branding_status.name if v.branding_status_id else "",
        "lift_gate": "true" if v.lift_gate else "false",
        "tail_lift_brand": v.tail_lift_brand.name if v.tail_lift_brand_id else "",
        "remarks": v.remarks or "",
        "insurance_document": _file_url_or_none(v.insurance_document) or "",
        "mulkia_document": _file_url_or_none(v.mulkia_document) or "",
        "permit_document": _file_url_or_none(v.permit_document) or "",
        "truck_photos": _file_url_or_none(v.truck_photos) or "",
    }

def _log_changes(request, v: VehicleMaster, before: dict, after: dict):
    username = request.user.username if getattr(request, "user", None) and request.user.is_authenticated else None
    for field, old in before.items():
        new = after.get(field, "")
        if (old or "") != (new or ""):
            ChangeLog.objects.create(
                date=date.today(),
                time=datetime.now().time().replace(microsecond=0),
                chassis_number=v.chassis_number,
                plate_number=v.plate_number,
                field_name=field,
                old_value=old or "",
                new_value=new or "",
                username=username,
            )

def _parse_date(value):
    if value is None or value == "":
        return None
    return parse_date(value)

def _parse_int(value):
    if value in (None, "", "null"):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def _get_fk(model, fk_id):
    if fk_id in (None, "", "null"):
        return None
    try:
        return model.objects.get(pk=int(fk_id))
    except (ValueError, TypeError):
        # Fall back if PK is non-integer type
        return model.objects.get(pk=fk_id)

def _apply_payload_to_instance(instance: VehicleMaster, data: dict, creating: bool):
    # Required fields for creating a new row (non-file fields)
    required_keys_for_create = [
        "plate_number",
        "vehicle_capacity_id",
        "vehicle_type_id",
        "tote_capacity_id",
        "status_id",
        "vehicle_concept_id",
        "make_id",
        "truck_reg_date",
        "truck_registration_expiry_date",
        "insurance_registration_date",
        "insurance_registration_expiry_date",
        "mulkia_registration_date",
        "mulkia_registration_expiry_date",
        "permit_registration_date",
        "permit_registration_expiry_date",
        "tl_no",
        "tc_no",
        "tc_owner",
        "salik_account_no",
        "salik_tag_no",
        "darb_ac_no",
        "gps_id",
        "branding_status_id",
        "lift_gate",
        "tail_lift_brand_id",
    ]

    if creating:
        missing = [k for k in required_keys_for_create if k not in data]
        if missing:
            raise ValueError(f"Missing required fields for create: {', '.join(missing)}")

    # Scalars
    if "plate_number" in data:
        instance.plate_number = data["plate_number"]

    if "truck_reg_date" in data:
        instance.truck_reg_date = _parse_date(data["truck_reg_date"])
    if "truck_registration_expiry_date" in data:
        instance.truck_registration_expiry_date = _parse_date(data["truck_registration_expiry_date"])

    if "insurance_registration_date" in data:
        instance.insurance_registration_date = _parse_date(data["insurance_registration_date"])
    if "insurance_registration_expiry_date" in data:
        instance.insurance_registration_expiry_date = _parse_date(data["insurance_registration_expiry_date"])

    if "mulkia_registration_date" in data:
        instance.mulkia_registration_date = _parse_date(data["mulkia_registration_date"])
    if "mulkia_registration_expiry_date" in data:
        instance.mulkia_registration_expiry_date = _parse_date(data["mulkia_registration_expiry_date"])

    if "permit_registration_date" in data:
        instance.permit_registration_date = _parse_date(data["permit_registration_date"])
    if "permit_registration_expiry_date" in data:
        instance.permit_registration_expiry_date = _parse_date(data["permit_registration_expiry_date"])

    if "tl_no" in data:
        _tl = _parse_int(data["tl_no"])
        if _tl is not None:
            instance.tl_no = _tl

    if "tc_no" in data:
        _tc = _parse_int(data["tc_no"])
        if _tc is not None:
            instance.tc_no = _tc

    if "tc_owner" in data:
        instance.tc_owner = data["tc_owner"]

    if "salik_account_no" in data:
        instance.salik_account_no = data["salik_account_no"]

    if "salik_tag_no" in data:
        instance.salik_tag_no = data["salik_tag_no"]

    if "darb_ac_no" in data:
        instance.darb_ac_no = data["darb_ac_no"]

    if "lift_gate" in data:
        val = data["lift_gate"]
        if isinstance(val, str):
            instance.lift_gate = val.lower() in ("true", "1", "on", "yes")
        else:
            instance.lift_gate = bool(val)

    if "remarks" in data:
        instance.remarks = data["remarks"]

    # FKs by *_id
    if "vehicle_capacity_id" in data:
        if data["vehicle_capacity_id"] not in ("", None, "null"):
            instance.vehicle_capacity = _get_fk(VehicleCapacity, data["vehicle_capacity_id"])
    if "vehicle_type_id" in data:
        if data["vehicle_type_id"] not in ("", None, "null"):
            instance.vehicle_type = _get_fk(VehicleType, data["vehicle_type_id"])
    if "tote_capacity_id" in data:
        if data["tote_capacity_id"] not in ("", None, "null"):
            instance.tote_capacity = _get_fk(ToteCapacity, data["tote_capacity_id"])
    if "status_id" in data:
        if data["status_id"] not in ("", None, "null"):
            instance.status = _get_fk(Status, data["status_id"])
    if "vehicle_concept_id" in data:
        if data["vehicle_concept_id"] not in ("", None, "null"):
            instance.vehicle_concept = _get_fk(VehicleConcept, data["vehicle_concept_id"])
    if "make_id" in data:
        if data["make_id"] not in ("", None, "null"):
            instance.make = _get_fk(Make, data["make_id"])
    if "gps_id" in data:
        if data["gps_id"] not in ("", None, "null"):
            instance.gps = _get_fk(GPS, data["gps_id"])
    if "branding_status_id" in data:
        if data["branding_status_id"] not in ("", None, "null"):
            instance.branding_status = _get_fk(BrandingStatus, data["branding_status_id"])
    if "tail_lift_brand_id" in data:
        if data["tail_lift_brand_id"] not in ("", None, "null"):
            instance.tail_lift_brand = _get_fk(TailLiftBrand, data["tail_lift_brand_id"])

    # File fields excluded in JSON payload; keep existing on update.
    # For create, set to empty strings to satisfy NOT NULL text columns.
    if creating:
        if not instance.insurance_document:
            instance.insurance_document = ""
        if not instance.mulkia_document:
            instance.mulkia_document = ""
        if not instance.permit_document:
            instance.permit_document = ""
        if not instance.truck_photos:
            instance.truck_photos = ""

def vehicle_master_api(request):
    if request.method == "GET":
        qs = (
            VehicleMaster.objects.select_related(
                "vehicle_capacity",
                "vehicle_type",
                "tote_capacity",
                "status",
                "vehicle_concept",
                "make",
                "gps",
                "branding_status",
                "tail_lift_brand",
            ).prefetch_related("emirates_permit")
        )
        data = [serialize_vehicle(v) for v in qs]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "unauthorized"}, status=401)

        # Support multipart form-data for file uploads as well as JSON payloads
        content_type = request.META.get("CONTENT_TYPE", "")
        is_multipart = content_type.startswith("multipart/form-data")

        if is_multipart:
            chassis_number = (request.POST.get("chassis_number") or "").strip()
            if not chassis_number:
                return HttpResponseBadRequest("chassis_number is required")

            with transaction.atomic():
                existing = VehicleMaster.objects.select_for_update().filter(pk=chassis_number).first()
                before = _snapshot_vehicle(existing) if existing else None
                target = existing or VehicleMaster(chassis_number=chassis_number)

                # Build a dict like the JSON payload expected by _apply_payload_to_instance
                form_payload = {
                    "plate_number": request.POST.get("plate_number"),
                    "vehicle_capacity_id": request.POST.get("vehicle_capacity_id"),
                    "vehicle_type_id": request.POST.get("vehicle_type_id"),
                    "tote_capacity_id": request.POST.get("tote_capacity_id"),
                    "status_id": request.POST.get("status_id"),
                    "vehicle_concept_id": request.POST.get("vehicle_concept_id"),
                    "make_id": request.POST.get("make_id"),
                    "truck_reg_date": request.POST.get("truck_reg_date"),
                    "truck_registration_expiry_date": request.POST.get("truck_registration_expiry_date"),
                    "insurance_registration_date": request.POST.get("insurance_registration_date"),
                    "insurance_registration_expiry_date": request.POST.get("insurance_registration_expiry_date"),
                    "mulkia_registration_date": request.POST.get("mulkia_registration_date"),
                    "mulkia_registration_expiry_date": request.POST.get("mulkia_registration_expiry_date"),
                    "permit_registration_date": request.POST.get("permit_registration_date"),
                    "permit_registration_expiry_date": request.POST.get("permit_registration_expiry_date"),
                    "tl_no": request.POST.get("tl_no"),
                    "tc_no": request.POST.get("tc_no"),
                    "tc_owner": request.POST.get("tc_owner"),
                    "salik_account_no": request.POST.get("salik_account_no"),
                    "salik_tag_no": request.POST.get("salik_tag_no"),
                    "darb_ac_no": request.POST.get("darb_ac_no"),
                    "gps_id": request.POST.get("gps_id"),
                    "branding_status_id": request.POST.get("branding_status_id"),
                    "lift_gate": request.POST.get("lift_gate"),
                    "tail_lift_brand_id": request.POST.get("tail_lift_brand_id"),
                    "remarks": request.POST.get("remarks"),
                }

                _apply_payload_to_instance(target, form_payload, creating=(existing is None))

                # Assign files if provided
                if "insurance_document" in request.FILES:
                    target.insurance_document = request.FILES["insurance_document"]
                if "mulkia_document" in request.FILES:
                    target.mulkia_document = request.FILES["mulkia_document"]
                if "permit_document" in request.FILES:
                    target.permit_document = request.FILES["permit_document"]
                if "truck_photos" in request.FILES:
                    target.truck_photos = request.FILES["truck_photos"]

                target.save()
                # Log changes if updating an existing vehicle
                if existing and before is not None:
                    after = _snapshot_vehicle(target)
                    _log_changes(request, target, before, after)

                # M2M emirates_permit
                em_raw = request.POST.get("emirates_permit_ids")
                if em_raw is not None:
                    ids = []
                    try:
                        parsed = json.loads(em_raw)
                        if isinstance(parsed, list):
                            ids = parsed
                    except Exception:
                        try:
                            ids = [int(x) for x in str(em_raw).split(",") if x.strip()]
                        except Exception:
                            ids = []
                    target.emirates_permit.set(Emirate.objects.filter(id__in=ids))

                return JsonResponse({"status": "updated" if existing else "created", "vehicle": serialize_vehicle(target)})
        else:
            try:
                payload = json.loads(request.body.decode("utf-8"))
            except Exception:
                return HttpResponseBadRequest("Invalid JSON body")

            chassis_number = payload.get("chassis_number")
            if not chassis_number:
                return HttpResponseBadRequest("chassis_number is required")

            with transaction.atomic():
                existing = VehicleMaster.objects.select_for_update().filter(pk=chassis_number).first()
                if existing:
                    before = _snapshot_vehicle(existing)
                    _apply_payload_to_instance(existing, payload, creating=False)
                    existing.save()
                    # Log changes after update
                    after = _snapshot_vehicle(existing)
                    _log_changes(request, existing, before, after)
                    # M2M
                    if "emirates_permit_ids" in payload:
                        ids = payload["emirates_permit_ids"] or []
                        existing.emirates_permit.set(Emirate.objects.filter(id__in=ids))
                    return JsonResponse({"status": "updated", "vehicle": serialize_vehicle(existing)})
                else:
                    instance = VehicleMaster(chassis_number=chassis_number)
                    _apply_payload_to_instance(instance, payload, creating=True)
                    instance.save()
                    # M2M
                    if "emirates_permit_ids" in payload:
                        ids = payload["emirates_permit_ids"] or []
                        instance.emirates_permit.set(Emirate.objects.filter(id__in=ids))
                    return JsonResponse({"status": "created", "vehicle": serialize_vehicle(instance)})

    return HttpResponseNotAllowed(["GET", "POST"])

def vehicle_master_detail_api(request, chassis_number: str):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "unauthorized"}, status=401)

    if request.method == "GET":
        try:
            instance = VehicleMaster.objects.get(pk=chassis_number)
        except VehicleMaster.DoesNotExist:
            return HttpResponseBadRequest("VehicleMaster not found")
        return JsonResponse(serialize_vehicle(instance))

    if request.method == "PUT":
        content_type = request.META.get("CONTENT_TYPE", "")
        is_multipart = content_type.startswith("multipart/form-data")

        with transaction.atomic():
            try:
                instance = VehicleMaster.objects.select_for_update().get(pk=chassis_number)
                before = _snapshot_vehicle(instance)
            except VehicleMaster.DoesNotExist:
                return HttpResponseBadRequest("VehicleMaster not found")

            if is_multipart:
                form_payload = {
                    "plate_number": request.POST.get("plate_number"),
                    "vehicle_capacity_id": request.POST.get("vehicle_capacity_id"),
                    "vehicle_type_id": request.POST.get("vehicle_type_id"),
                    "tote_capacity_id": request.POST.get("tote_capacity_id"),
                    "status_id": request.POST.get("status_id"),
                    "vehicle_concept_id": request.POST.get("vehicle_concept_id"),
                    "make_id": request.POST.get("make_id"),
                    "truck_reg_date": request.POST.get("truck_reg_date"),
                    "truck_registration_expiry_date": request.POST.get("truck_registration_expiry_date"),
                    "insurance_registration_date": request.POST.get("insurance_registration_date"),
                    "insurance_registration_expiry_date": request.POST.get("insurance_registration_expiry_date"),
                    "mulkia_registration_date": request.POST.get("mulkia_registration_date"),
                    "mulkia_registration_expiry_date": request.POST.get("mulkia_registration_expiry_date"),
                    "permit_registration_date": request.POST.get("permit_registration_date"),
                    "permit_registration_expiry_date": request.POST.get("permit_registration_expiry_date"),
                    "tl_no": request.POST.get("tl_no"),
                    "tc_no": request.POST.get("tc_no"),
                    "tc_owner": request.POST.get("tc_owner"),
                    "salik_account_no": request.POST.get("salik_account_no"),
                    "salik_tag_no": request.POST.get("salik_tag_no"),
                    "darb_ac_no": request.POST.get("darb_ac_no"),
                    "gps_id": request.POST.get("gps_id"),
                    "branding_status_id": request.POST.get("branding_status_id"),
                    "lift_gate": request.POST.get("lift_gate"),
                    "tail_lift_brand_id": request.POST.get("tail_lift_brand_id"),
                    "remarks": request.POST.get("remarks"),
                }
                _apply_payload_to_instance(instance, form_payload, creating=False)

                # Files
                if "insurance_document" in request.FILES:
                    instance.insurance_document = request.FILES["insurance_document"]
                if "mulkia_document" in request.FILES:
                    instance.mulkia_document = request.FILES["mulkia_document"]
                if "permit_document" in request.FILES:
                    instance.permit_document = request.FILES["permit_document"]
                if "truck_photos" in request.FILES:
                    instance.truck_photos = request.FILES["truck_photos"]

                instance.save()
                after = _snapshot_vehicle(instance)
                _log_changes(request, instance, before, after)

                # M2M emirates_permit
                em_raw = request.POST.get("emirates_permit_ids")
                if em_raw is not None:
                    ids = []
                    try:
                        parsed = json.loads(em_raw)
                        if isinstance(parsed, list):
                            ids = parsed
                    except Exception:
                        try:
                            ids = [int(x) for x in str(em_raw).split(",") if x.strip()]
                        except Exception:
                            ids = []
                    instance.emirates_permit.set(Emirate.objects.filter(id__in=ids))
            else:
                try:
                    payload = json.loads(request.body.decode("utf-8"))
                except Exception:
                    return HttpResponseBadRequest("Invalid JSON body")

                _apply_payload_to_instance(instance, payload, creating=False)
                instance.save()
                after = _snapshot_vehicle(instance)
                _log_changes(request, instance, before, after)
                if "emirates_permit_ids" in payload:
                    ids = payload["emirates_permit_ids"] or []
                    instance.emirates_permit.set(Emirate.objects.filter(id__in=ids))

            return JsonResponse({"status": "updated", "vehicle": serialize_vehicle(instance)})

    return HttpResponseNotAllowed(["GET", "PUT"])

def dropdowns_api(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    if not request.user.is_authenticated:
        return JsonResponse({"error": "unauthorized"}, status=401)

    def _ser(qs):
        return [{"id": obj.id, "name": obj.name} for obj in qs.order_by("name")]

    data = {
        "vehicle_capacities": _ser(VehicleCapacity.objects.all()),
        "vehicle_types": _ser(VehicleType.objects.all()),
        "tote_capacities": _ser(ToteCapacity.objects.all()),
        "statuses": _ser(Status.objects.all()),
        "vehicle_concepts": _ser(VehicleConcept.objects.all()),
        "makes": _ser(Make.objects.all()),
        "emirates": _ser(Emirate.objects.all()),
        "gps_list": _ser(GPS.objects.all()),
        "branding_statuses": _ser(BrandingStatus.objects.all()),
        "tail_lift_brands": _ser(TailLiftBrand.objects.all()),
    }
    return JsonResponse(data)

@login_required(login_url='login')
def download_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vehicle_master.csv"'

    writer = csv.writer(response)
    
    # Get all field names from the VehicleMaster model
    field_names = [field.name for field in VehicleMaster._meta.get_fields() if not field.is_relation or field.one_to_one or (field.many_to_one and field.related_model)]
    writer.writerow(field_names)

    vehicles = VehicleMaster.objects.all().values_list(*field_names)
    for vehicle in vehicles:
        writer.writerow(vehicle)

    return response

@login_required(login_url='login')
def notifications_list(request):
    qs = Notification.objects.filter(user=request.user).order_by('-created_at')
    status = request.GET.get('status')
    if status in ('unread', 'read', 'snoozed'):
        qs = qs.filter(status=status)
    return render(request, 'notifications_list.html', {'notifications': qs, 'status': status})

@login_required(login_url='login')
def notification_settings(request):
    return render(request, 'notification_settings.html')

@login_required(login_url='login')
def notifications_api(request):
    if request.method == 'GET':
        # Fetch all unread notifications for any user in the 'office_user' group
        notifications = Notification.objects.filter(
            user__groups__name='office_user',
            status='unread'
        ).order_by('-created_at')
        
        unread_count = notifications.count()
        
        serialized_notifications = [{
            'id': n.id,
            'message': n.message,
            'status': n.status,
            'created_at': n.created_at.isoformat(),
            'vehicle_plate': n.vehicle.plate_number if n.vehicle else 'N/A',
            'vehicle_chassis': n.vehicle.chassis_number if n.vehicle else None,
            'edit_url': reverse('vehicle_update', args=[n.vehicle.chassis_number]) if n.vehicle else None,
        } for n in notifications]

        return JsonResponse({
            'notifications': serialized_notifications,
            'unread_count': unread_count,
        })
    return HttpResponseNotAllowed(['GET'])

@login_required(login_url='login')
def notification_action_api(request, notification_id, action):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
    except Notification.DoesNotExist:
        return HttpResponseBadRequest("Notification not found")

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    if action == 'read':
        notification.status = 'read'
        notification.snoozed_until = None
        notification.save()
        return JsonResponse({'status': 'ok'})
    elif action == 'unread':
        notification.status = 'unread'
        notification.snoozed_until = None
        notification.save()
        return JsonResponse({'status': 'ok'})
    elif action == 'snooze':
        # Support snoozing for 7, 14, or 30 days via ?days=7|14|30 or POST/JSON payload; default to 7
        days = 7
        try:
            # Query param
            if 'days' in request.GET:
                days = int(request.GET.get('days', 7))
            # JSON body
            elif request.META.get('CONTENT_TYPE', '').startswith('application/json'):
                try:
                    body = json.loads((request.body or b'').decode('utf-8') or '{}')
                    if isinstance(body, dict) and 'days' in body:
                        days = int(body.get('days', 7))
                except Exception:
                    pass
            # Form body
            elif 'days' in request.POST:
                days = int(request.POST.get('days', 7))
        except Exception:
            days = 7

        if days not in (7, 14, 30):
            days = 7

        notification.status = 'snoozed'
        notification.snoozed_until = timezone.now() + timedelta(days=days)
        notification.save()
        return JsonResponse({'status': 'ok', 'days': days, 'snoozed_until': notification.snoozed_until.isoformat()})
    else:
        return HttpResponseBadRequest("Invalid action")

@login_required(login_url='login')
def user_notification_settings_api(request):
    settings, created = UserNotificationSettings.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        return JsonResponse({
            'insurance_expiry_notifications': settings.insurance_expiry_notifications,
            'mulkia_expiry_notifications': settings.mulkia_expiry_notifications,
            'permit_expiry_notifications': settings.permit_expiry_notifications,
            'truck_registration_expiry_notifications': settings.truck_registration_expiry_notifications,
        })

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            settings.insurance_expiry_notifications = data.get('insurance_expiry_notifications', False)
            settings.mulkia_expiry_notifications = data.get('mulkia_expiry_notifications', False)
            settings.permit_expiry_notifications = data.get('permit_expiry_notifications', False)
            settings.truck_registration_expiry_notifications = data.get('truck_registration_expiry_notifications', False)
            settings.save()

            # Re-fetch from the database to confirm the save operation
            fresh_settings = UserNotificationSettings.objects.get(user=request.user)
            
            return JsonResponse({
                'status': 'ok',
                'sent_payload': data,
                'saved_settings': {
                    'insurance_expiry_notifications': fresh_settings.insurance_expiry_notifications,
                    'mulkia_expiry_notifications': fresh_settings.mulkia_expiry_notifications,
                    'permit_expiry_notifications': fresh_settings.permit_expiry_notifications,
                    'truck_registration_expiry_notifications': fresh_settings.truck_registration_expiry_notifications,
                }
            })
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return HttpResponseNotAllowed(['GET', 'POST'])
