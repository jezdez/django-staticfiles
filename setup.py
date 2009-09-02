from setuptools import setup, find_packages

setup(
    name='django-staticfiles',
    version='0.1.0',
    description="A Django app that provides helpers for serving static files.",
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
