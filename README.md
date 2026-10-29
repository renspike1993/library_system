# Library System (Django)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations administrative book library_service compliance
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Admin: http://127.0.0.1:8000/admin/
