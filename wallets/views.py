import json
from datetime import datetime

import django.dispatch
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from django.db.models import Max

from .models import Device
from .models import Registration
from .models import Log


FORMAT = '%Y-%m-%d %H:%M:%S'
pass_registered = django.dispatch.Signal()
pass_unregistered = django.dispatch.Signal()


def is_authorized(
        request: HttpRequest,
        pass_: settings.PASS_MODEL,
) -> bool:
    """Check if a request is authorized"""

    client_token: str = request.META.get('HTTP_AUTHORIZATION')
    token_type, token = client_token.split(' ')

    return token_type in [
        'WalletUnionPass',  # for Androids (Wallet application)
        'ApplePass'  # for Apple
    ] and token == pass_.authentication_token


def get_pass(
        pass_type_id: str,
        serial_number: str
) -> settings.PASS_MODEL:
    """Return a pass or 404"""
    return get_object_or_404(
        settings.PASS_MODEL,
        pass_type_id=pass_type_id,
        serial_number=serial_number
    )


def latest_pass(
        request: HttpRequest,
        pass_type_id: str,
        serial_number: str
) -> datetime:
    return get_pass(
        pass_type_id,
        serial_number
    ).utime


@csrf_exempt
def handle_device(
        request: HttpRequest,
        device_library_id: str,
        pass_type_id: str,
        serial_number: str
):
    """
    Handle a device request, register or unregister it
    """
    # we already have this card
    pass_ = get_pass(pass_type_id, serial_number)

    if not is_authorized(request, pass_):
        return HttpResponse(status=401)

    # registering a device
    if request.method == 'POST':
        # if already registered
        try:
            Registration.objects.get(
                pass_object=pass_,
                device=Device.objects.get(
                    device_library_identifier=device_library_id
                )
            )
            return HttpResponse(status=200)
        except (Device.DoesNotExist, Registration.DoesNotExist):
            body = json.loads(request.body)

            new_device = Device(
                device_library_identifier=device_library_id,
                push_token=body['pushToken']
            )
            new_device.save()
            new_registration = Registration(
                pass_object=pass_,
                device=new_device
            )
            new_registration.save()

            pass_registered.send(sender=pass_)
            return HttpResponse(status=201)  # Created

    elif request.method == 'DELETE':
        try:
            device = Device.objects.get(
                device_library_identifier=device_library_id
            )
            old_registration = Registration.objects.filter(
                pass_object=pass_,
                device=device
            )
            old_registration.delete()
            device.delete()
            pass_unregistered.send(sender=pass_)
            return HttpResponse(status=200)
        except Device.DoesNotExist:
            return HttpResponse(status=404)

    else:
        return HttpResponse(status=400)


def get_serial_numbers(
        request: HttpRequest,
        device_library_id: str,
        pass_type_id: str
):
    """
    Get the Serial Numbers for passes associated with a device
    """
    device = get_object_or_404(
        Device,
        device_library_identifier=device_library_id
    )
    # get all the existing passes
    passes = settings.PASS_MODEL.objects.filter(
        registration__device=device,
        pass_type_id=pass_type_id
    )

    if passes.count() == 0:
        return HttpResponse(status=404)

    if 'passesUpdatedSince' in request.GET:
        passes: QuerySet = passes.filter(utime__gt=datetime.strptime(
            request.GET['passesUpdatedSince'], FORMAT
        ))

    if passes:
        last_updated: datetime = passes.aggregate(Max('utime'))['utime__max']
        serial_numbers = [
            p.serial_number for p in passes.filter(
                utime=last_updated
            ).all()
        ]
        response_data = {
            'lastUpdated': last_updated.strftime(FORMAT),
            'serialNumbers': serial_numbers
        }
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(status=204)  # no content


@condition(last_modified_func=latest_pass)
def get_latest_version(
        request: HttpRequest,
        pass_type_id: str,
        serial_number: str
):
    """
    Get the latest version of pass
    """
    pass_ = get_pass(pass_type_id, serial_number)

    if not is_authorized(request, pass_):
        return HttpResponse(status=401)

    response = HttpResponse(
        pass_.data.read(),
        content_type='application/vnd.apple.pkpass'
    )
    response['Content-Disposition'] = 'attachment; filename=pass.pkpass'
    return response


@csrf_exempt
def log_info(request: HttpRequest):
    """
    Log messages from devices
    """
    body = json.loads(request.body)
    for message in body['logs']:
        log = Log(message=message)
        log.save()
    return HttpResponse(status=200)
