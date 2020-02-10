from django.contrib import admin
from django.utils.translation import gettext as _

from .models import Registration
from .models import Device
from .models import Log


class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        'device_library_identifier',
        'get_brand',
    )

    def get_brand(self, obj):
        if len(obj.push_token) > 100:
            return 'Android'
        else:
            return 'iPhone'

    get_brand.short_description = _('Brand')


admin.site.register(Device, DeviceAdmin)

admin.site.register(Log)

admin.site.register(Registration)
