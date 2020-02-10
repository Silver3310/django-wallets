import decimal
import hashlib
import json
import subprocess
import zipfile
from io import BytesIO

from django.conf import settings


class Alignment:
    LEFT = 'PKTextAlignmentLeft'
    CENTER = 'PKTextAlignmentCenter'
    RIGHT = 'PKTextAlignmentRight'
    JUSTIFIED = 'PKTextAlignmentJustified'
    NATURAL = 'PKTextAlignmentNatural'


class BarcodeFormat:
    PDF417 = 'PKBarcodeFormatPDF417'
    QR = 'PKBarcodeFormatQR'
    AZTEC = 'PKBarcodeFormatAztec'
    CODE128 = 'PKBarcodeFormatCode128'


class TransitType:
    AIR = 'PKTransitTypeAir'
    TRAIN = 'PKTransitTypeTrain'
    BUS = 'PKTransitTypeBus'
    BOAT = 'PKTransitTypeBoat'
    GENERIC = 'PKTransitTypeGeneric'


class DateStyle:
    NONE = 'PKDateStyleNone'
    SHORT = 'PKDateStyleShort'
    MEDIUM = 'PKDateStyleMedium'
    LONG = 'PKDateStyleLong'
    FULL = 'PKDateStyleFull'


class NumberStyle:
    DECIMAL = 'PKNumberStyleDecimal'
    PERCENT = 'PKNumberStylePercent'
    SCIENTIFIC = 'PKNumberStyleScientific'
    SPELLOUT = 'PKNumberStyleSpellOut'


class Field:

    def __init__(self, key, value, label=''):

        self.key = key  # Required. The key must be unique within the scope
        self.value = value  # Required. Value of the field. For example, 42
        self.label = label  # Optional. Label text for the field.
        # Optional. Format string for the alert text that is displayed when
        # the pass is updated
        self.change_message = ''
        self.text_alignment = Alignment.LEFT

    def json_dict(self):
        return self.__dict__


class DateField(Field):

    def __init__(self, key, value, label=''):
        super().__init__(key, value, label)
        self.date_style = DateStyle.SHORT  # Style of date to display
        self.time_style = DateStyle.SHORT  # Style of time to display
        # If true, the labels value is displayed as a relative date
        self.is_relative = False

    def json_dict(self):
        return self.__dict__


class NumberField(Field):

    def __init__(self, key, value, label=''):
        super().__init__(key, value, label)
        self.number_style = NumberStyle.DECIMAL  # Style of date to display

    def json_dict(self):
        return self.__dict__


class CurrencyField(Field):

    def __init__(self, key, value, label='', currency_code=''):
        super().__init__(key, value, label)
        self.currency_code = currency_code  # ISO 4217 currency code

    def json_dict(self):
        return self.__dict__


class Barcode:

    def __init__(
            self,
            message,
            format_=BarcodeFormat.PDF417,
            alt_text=''
    ):

        self.format = format_
        # Required. Message or payload to be displayed as a barcode
        self.message = message
        # Required. Text encoding that is used to convert the message
        self.message_encoding = 'iso-8859-1'
        self.altText = alt_text  # Optional. Text displayed near the barcode

    def json_dict(self):
        return self.__dict__


class Location:

    def __init__(self, latitude, longitude, altitude=0.0):
        # Required. Latitude, in degrees, of the location.
        try:
            self.latitude = float(latitude)
        except (ValueError, TypeError):
            self.latitude = 0.0
        # Required. Longitude, in degrees, of the location.
        try:
            self.longitude = float(longitude)
        except (ValueError, TypeError):
            self.longitude = 0.0
        # Optional. Altitude, in meters, of the location.
        try:
            self.altitude = float(altitude)
        except (ValueError, TypeError):
            self.altitude = 0.0
        # Optional. Notification distance
        self.distance = None
        # Optional. Text displayed on the lock screen when
        # the pass is currently near the location
        self.relevant_text = ''

    def json_dict(self):
        return self.__dict__


class IBeacon(object):
    def __init__(self, proximity_uuid, major, minor):
        # IBeacon data
        self.proximity_uuid = proximity_uuid
        self.major = major
        self.minor = minor

        # Optional. Text message where near the ibeacon
        self.relevant_text = ''

    def json_dict(self):
        return self.__dict__


class PassInformation:

    def __init__(self):
        self.header_fields = []
        self.primary_fields = []
        self.secondary_fields = []
        self.back_fields = []
        self.auxiliary_fields = []

    def add_header_field(self, key, value, label):
        self.header_fields.append(Field(key, value, label))

    def add_primary_field(self, key, value, label):
        self.primary_fields.append(Field(key, value, label))

    def add_secondary_field(self, key, value, label):
        self.secondary_fields.append(Field(key, value, label))

    def add_back_field(self, key, value, label):
        self.back_fields.append(Field(key, value, label))

    def add_auxiliary_field(self, key, value, label):
        self.auxiliary_fields.append(Field(key, value, label))

    def json_dict(self):
        d = {}
        if self.header_fields:
            d.update({
                'header_fields': [f.json_dict() for f in self.header_fields]
            })
        if self.primary_fields:
            d.update({
                'primary_fields': [f.json_dict() for f in self.primary_fields]
            })
        if self.secondary_fields:
            d.update({
                'secondary_fields': [
                    f.json_dict() for f in self.secondary_fields
                ]
            })
        if self.back_fields:
            d.update({
                'back_fields': [f.json_dict() for f in self.back_fields]
            })
        if self.auxiliary_fields:
            d.update({
                'auxiliary_fields': [
                    f.json_dict() for f in self.auxiliary_fields
                ]
            })
        return d


class BoardingPass(PassInformation):

    def __init__(self, transit_type=TransitType.AIR):
        super().__init__()
        self.transit_type = transit_type
        self.json_name = 'boardingPass'

    def json_dict(self):
        d = super().json_dict()
        d.update({'transitType': self.transit_type})
        return d


class Coupon(PassInformation):

    def __init__(self):
        super().__init__()
        self.json_name = 'coupon'


class EventTicket(PassInformation):

    def __init__(self):
        super().__init__()
        self.json_name = 'eventTicket'


class Generic(PassInformation):

    def __init__(self):
        super().__init__()
        self.json_name = 'generic'


class StoreCard(PassInformation):

    def __init__(self):
        super().__init__()
        self.json_name = 'storeCard'


class Pass:

    def __init__(
            self,
            pass_information,
            pass_type_identifier='',
            organization_name='',
            team_identifier='',
            foreground_color=None,
            background_color=None,
            label_color=None,
            logo_text=None,
            web_service_url='',
            authentication_token='',
            serial_number='',
            description='',
            format_version=1,
            barcode=None,
            suppress_strip_shine=False,
            locations=None,
            ibeacons=None,
            relevant_date=None,
            associated_store_identifiers=None,
            app_launch_url=None,
            user_info=None,
            expiration_date=None,
            voided=None
    ):

        self._files = {}  # Holds the files to include in the .pkpass
        self._hashes = {}  # Holds the SHAs of the files array

        # Standard Keys

        # Required. Team identifier of the organization that originated and
        # signed the pass, as issued by Apple.
        self.team_identifier = team_identifier
        # Required. Pass type identifier, as issued by Apple. The value must
        # correspond with your signing certificate. Used for grouping.
        self.pass_type_identifier = pass_type_identifier
        # Required. Display name of the organization that originated and
        # signed the pass.
        self.organization_name = organization_name
        # Required. Serial number that uniquely identifies the pass.
        self.serial_number = serial_number
        # Required. Brief description of the pass, used by the iOS
        # accessibility technologies.
        self.description = description
        # Required. Version of the file format. The value must be 1.
        self.format_version = format_version

        # Visual Appearance Keys
        # Optional. Background color of the pass
        self.background_color = background_color
        # Optional. Foreground color of the pass
        self.foreground_color = foreground_color
        self.label_color = label_color  # Optional. Color of the label text
        self.logo_text = logo_text  # Optional. Text displayed next to the logo
        self.barcode = barcode  # Optional. Information specific to barcodes.
        # Optional. If true, the strip image is displayed
        self.suppress_strip_shine = suppress_strip_shine

        # Web Service Keys

        # Optional. If present, authenticationToken must be supplied
        self.web_service_url = web_service_url
        # The authentication token to use with the web service
        self.authentication_token = authentication_token

        # Relevance Keys

        # Optional. Locations where the pass is relevant.
        # For example, the location of your store.
        self.locations = locations
        # Optional. IBeacons data
        self.ibeacons = ibeacons
        # Optional. Date and time when the pass becomes relevant
        self.relevant_date = relevant_date

        # Optional. A list of iTunes Store item identifiers for
        # the associated apps.
        self.associated_store_identifiers = associated_store_identifiers
        self.app_launch_url = app_launch_url
        # Optional. Additional hidden data in json for the passbook
        self.user_info = user_info

        self.expiration_date = expiration_date
        self.voided = voided

        self.pass_information = pass_information

    # Adds file to the file array
    def add_file(self, name, fd):
        self._files[name] = fd.read()

    # Creates the actual .pkpass file
    def create(
            self,
            zip_file=None
    ):
        zip_file = settings.WALLET_PASS_PATH.format(self.serial_number)
        pass_json = self._create_pass_json()
        manifest = self._create_manifest(pass_json)
        signature = self._create_signature(
            manifest,
            settings.WALLET_CERTIFICATE_PATH,
            settings.WALLET_KEY_PATH,
            settings.WALLET_WWDR_PATH,
            settings.WALLET_PASSWORD,
        )
        if not zip_file:
            zip_file = BytesIO()
        self._create_zip(
            pass_json,
            manifest,
            signature,
            zip_file=zip_file
        )
        return zip_file

    def _create_pass_json(self):
        return json.dumps(self, default=pass_handler).encode('utf-8')

    # creates the hashes for the files and adds them into a json string.
    def _create_manifest(self, pass_json):
        # Creates SHA hashes for all files in package
        self._hashes['pass.json'] = hashlib.sha1(pass_json).hexdigest()
        for filename, filedata in self._files.items():
            self._hashes[filename] = hashlib.sha1(filedata).hexdigest()
        return json.dumps(self._hashes).encode('utf-8')

    # Creates a signature and saves it
    @staticmethod
    def _create_signature(
            manifest,
            certificate,
            key,
            wwdr_certificate,
            password
    ):
        openssl_cmd = [
            'openssl',
            'smime',
            '-binary',
            '-sign',
            '-certfile',
            wwdr_certificate,
            '-signer',
            certificate,
            '-inkey',
            key,
            '-outform',
            'DER',
            '-passin',
            'pass:{}'.format(password),
        ]
        process = subprocess.Popen(
            openssl_cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        process.stdin.write(manifest)
        der, error = process.communicate()
        if process.returncode != 0:
            raise Exception(error)

        return der

    # Creates .pkpass (zip archive)
    def _create_zip(self, pass_json, manifest, signature, zip_file=None):
        zf = zipfile.ZipFile(zip_file or 'pass.pkpass', 'w')
        zf.writestr('signature', signature)
        zf.writestr('manifest.json', manifest)
        zf.writestr('pass.json', pass_json)
        for filename, filedata in self._files.items():
            zf.writestr(filename, filedata)
        zf.close()

    def json_dict(self):
        d = {
            'description': self.description,
            'formatVersion': self.format_version,
            'organizationName': self.organization_name,
            'passTypeIdentifier': self.pass_type_identifier,
            'serialNumber': self.serial_number,
            'teamIdentifier': self.team_identifier,
            'suppressStripShine': self.suppress_strip_shine,
            self.pass_information.json_name: self.pass_information.json_dict()
        }
        if self.barcode:
            d.update({'barcode': self.barcode.json_dict()})
        if self.relevant_date:
            d.update({'relevantDate': self.relevant_date})
        if self.background_color:
            d.update({'backgroundColor': self.background_color})
        if self.foreground_color:
            d.update({'foregroundColor': self.foreground_color})
        if self.label_color:
            d.update({'labelColor': self.label_color})
        if self.logo_text:
            d.update({'logoText': self.logo_text})
        if self.locations:
            d.update({'locations': self.locations})
        if self.ibeacons:
            d.update({'beacons': self.ibeacons})
        if self.user_info:
            d.update({'userInfo': self.user_info})
        if self.associated_store_identifiers:
            d.update({
                'associatedStoreIdentifiers': self.associated_store_identifiers
            })
        if self.app_launch_url:
            d.update({'appLaunchURL': self.app_launch_url})
        if self.expiration_date:
            d.update({'expirationDate': self.expiration_date})
        if self.voided:
            d.update({'voided': True})
        if self.web_service_url:
            d.update({'webServiceURL': self.web_service_url,
                      'authenticationToken': self.authentication_token})
        return d


def pass_handler(obj):
    if hasattr(obj, 'json_dict'):
        return obj.json_dict()
    else:
        # For Decimal latitude and logitude etc.
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        else:
            return obj
