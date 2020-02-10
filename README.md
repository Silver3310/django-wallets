
# django-wallets

Apple Wallet integration for a django a project

## Getting Started

To get started you should copy the 'wallets' folder to the your project directory

```
git clone https://github.com/Silver3310/django-wallets
cp -r django-wallets/wallets your-project-directory
```

### Prerequisites

If you want to make asynchronous pushes to users when their passes are updated you should install celery
```
pip install celery 
```

### Installing

After you copied the app to your project directory, you should do the following steps

Add the app to your project settings
```python
INSTALLED_APPS = [
    ...
    'wallets',
    ...
 ]
```
```python
# Wallets management
path(
    "/",
    include("index_auth_service.wallets.urls")
),
```

Define the model with your Pass from PassAbstract and add fields you need
```python
from wallets.models import PassAbstract    
  
class Pass(PassAbstract):  
"""  
    The pass model for Apple Wallet 
"""  
discount_card = models.ForeignKey(  
    DiscountCard,  
    on_delete=models.CASCADE,  
    verbose_name=_('Discount card')  
)
```

Add the necessary constants
```python
# APPLE WALLET
WALLET_CERTIFICATE_PATH = 'path-to-certificate-pem-file'
WALLET_KEY_PATH = 'path-to-key-certificate-pem-file'
WALLET_WWDR_PATH = 'path-to-wwdr-certificate-pem-file'
WALLET_PASS_TYPE_ID = 'pass.com.you.pass.id'
WALLET_PASS_PATH = os.path.join(
    'the-path-where-you-want-store-passes',
    'passes',
    'pass{}.pkpass'
)
WALLET_TEAM_IDENTIFIER = 'your-team-identifier'
WALLET_ORGANIZATION_NAME = 'organization-name'
WALLET_APN_HOST = ('gateway.push.apple.com', 2195)
WALLET_ANDROID_HOST = 'https://push.walletunion.com/send'
WALLET_ANDROID_API_KEY = 'get-it-in-the-official-site'
WALLET_PASSWORD = 'certificate-key-passowrd'
WALLET_ENABLE_NOTIFICATIONS = False  # True if you want to send notifications (Celery needed for it)
PASS_MODEL = 'your_app.your_model'
```
Make migrations for your model and the wallets app and migrate them
```
python manage.py makemigrations
python manage.py migrate
```

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details