import socket
import ssl
import json
import struct
import binascii
import urllib

from django.conf import settings

try:
    from celery import shared_task  # in case a user has celery installed
except ImportError:
    pass


@shared_task
def pass_push_apple(
        push_token: str,
):
    """
    Send a push notification to APNS
    (Apple Push Notification service)
    """

    pay_load = {}

    cert = settings.WALLET_CERTIFICATE_PATH

    host = settings.WALLET_APN_HOST

    pay_load = json.dumps(pay_load, separators=(',', ':'))

    device_token = binascii.unhexlify(push_token)
    fmt = "!BH32sH{}s".format(len(pay_load))

    msg = struct.pack(
        fmt,
        0,
        32,
        device_token,
        len(pay_load),
        bytes(pay_load, "utf-8")
    )

    ssl_sock = ssl.wrap_socket(
        socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        ),
        certfile=cert,
    )
    ssl_sock.connect(host)

    ssl_sock.write(msg)
    ssl_sock.close()


@shared_task
def pass_push_android(
        push_token: str
):
    """
    Send a push notification to Android
    """

    url = settings.WALLET_ANDROID_HOST
    hdr = {
        'Authorization': settings.WALLET_ANDROID_API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        "passTypeIdentifier": settings.WALLET_PASS_TYPE_ID,
        "pushTokens": [
            push_token,
        ]
    }
    print(json.dumps(data))
    data = json.dumps(data).encode()

    req = urllib.request.Request(
        url,
        headers=hdr,
        data=data,
        method='POST'
    )
    response = urllib.request.urlopen(req)
    response.read()
