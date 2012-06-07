test:
	coverage run --branch --source=staticfiles `which django-admin.py` test --settings=staticfiles.test_settings staticfiles
	coverage report --omit=staticfiles/test*
