import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-staticfiles',
    version='0.2.0',
    description="A Django app that provides helpers for serving static files.",
    long_description=read('README'),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    license='BSD',
    url='http://bitbucket.org/jezdez/django-staticfiles/',
    download_url='http://bitbucket.org/jezdez/django-staticfiles/downloads/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
)
