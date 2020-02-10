"""
API urls that are built in accordance to
https://developer.apple.com/library/archive/documentation/PassKit/Reference/PassKit_WebService/WebService.html
"""
from django.urls import path

from .views import handle_device
from .views import get_serial_numbers
from .views import get_latest_version
from .views import log_info


urlpatterns = [
    path(
        'v1/devices/<str:device_library_id>/registrations/<str:pass_type_id>/<str:serial_number>',
        handle_device,  # register and unregister a device
        name='handle_device'
    ),
    # for Android phones
    path(
        'v1/devices/<str:device_library_id>/registrations_attido/<str:pass_type_id>/<str:serial_number>',
        handle_device,  # register and unregister a device
        name='handle_device'
    ),
    path(
        'v1/devices/<str:device_library_id>/registrations/<str:pass_type_id>',
        get_serial_numbers,
        name='get_serial_numbers'
    ),
    path(
        'v1/passes/<str:pass_type_id>/<str:serial_number>',
        get_latest_version,
        name='get_latest_version'
    ),
    path(
        'v1/log',
        log_info,
        name='log_info'
    ),
]
