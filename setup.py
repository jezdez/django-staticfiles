import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-staticfiles',
    version='0.4',
    description="A Django app that provides helpers for serving static files.",
    long_description=read('README.rst'),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    license='BSD',
    url='http://django-staticfiles.readthedocs.org/',
    download_url='http://bitbucket.org/jezdez/django-staticfiles/downloads/',
    packages=[
        'staticfiles',
        'staticfiles.management',
        'staticfiles.management.commands',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
)
