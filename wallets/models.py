"""
The models are built in accordance to the Wallet Developer Guide
https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Updating.html#//apple_ref/doc/uid/TP40012195-CH5-SW1
"""
from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _


class PassAbstract(models.Model):
    """
    The pass model for Apple Wallet
    """
    pass_type_id = models.CharField(
        max_length=50,
        verbose_name=_('Pass Type identifier')
    )
    serial_number = models.CharField(
        max_length=50,
        verbose_name=_('Serial number'),
    )
    authentication_token = models.CharField(
        max_length=50,
        verbose_name=_('Authentication token')
    )
    data = models.FileField(
        upload_to='passes',
        verbose_name=_('Data (pass file)')
    )
    ctime = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    utime = models.DateTimeField(
        blank=True,
        default=datetime.now,
        verbose_name=_('Updated at')
    )

    def __str__(self):
        return '{} ({})'.format(
            self.pass_type_id,
            self.serial_number
        )

    class Meta:
        abstract = True
        unique_together = [['pass_type_id', 'serial_number']]
        ordering = ['-pk']
        verbose_name = _('Apple Wallet Pass')
        verbose_name_plural = _('Apple Wallet Passes')


class Device(models.Model):
    """
    Device that passes are associated with
    """
    device_library_identifier = models.CharField(
        max_length=50,
        verbose_name=_('Device identifier'),
        unique=True
    )
    push_token = models.CharField(
        max_length=250,
        verbose_name=_('Push token')
    )

    def __str__(self):
        return self.device_library_identifier

    class Meta:
        ordering = ['-pk']
        verbose_name = _('Connected device')
        verbose_name_plural = _('Connected devices')


class Registration(models.Model):
    """
    A registration is a relationship between a device and a pass
    """
    pass_object = models.ForeignKey(
        settings.PASS_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Apple Wallet pass')
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        verbose_name=_('Associated device')
    )

    def __str__(self):
        return '{} - {}'.format(
            self.pass_object,
            self.device
        )

    class Meta:
        ordering = ['-pk']
        unique_together = [['pass_object', 'device']]
        verbose_name = _('Relation: pass - device')
        verbose_name_plural = _('Relations: pass - device')


class Log(models.Model):
    """
    Logs that are sent by devices
    """
    message = models.TextField(
        verbose_name=_('Message')
    )

    def __str__(self):
        return self.message[:50]

    class Meta:
        ordering = ['-pk']
        verbose_name = _('Log')
        verbose_name_plural = _('Logs')
