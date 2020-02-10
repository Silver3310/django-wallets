from distutils.core import setup
setup(
  name='django-wallet',
  packages=['wallets'],
  version='0.2',
  license='MIT',
  description='Apple Wallet integration for a django project',
  author='Elivanov Alexey',
  author_email='epifanov998@mail.ru',
  url='https://github.com/Silver3310/django-wallets',
  download_url='https://github.com/Silver3310/django-wallets/archive/v_02.tar.gz',
  keywords=['django', 'wallet', 'apple', 'pass'],
  install_requires=[
          'celery',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
