import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

VERSION = __import__("staticfiles").__version__

setup(
    name='django-staticfiles',
    version=VERSION,
    description="A Django app that provides helpers for serving static files.",
    long_description=read('README.rst'),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    license='BSD',
    url='http://django-staticfiles.readthedocs.org/',
    packages=[
        'staticfiles',
        'staticfiles.management',
        'staticfiles.management.commands',
        'staticfiles.templatetags',
    ],
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
    test_suite="tests.runtests.runtests",
)
