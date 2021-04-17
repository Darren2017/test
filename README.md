
## Dependent installation
```shell
virtualenv --no-site-packages venv --python=python3
source venv/bin/activate
pip install -r requirements.txt
```
## First start
```
source venv/bin/activate
python manage.py shell
from app import db
db.create_all()
exit()
python wsgi.py
```
## start

```shell
python wsgi.py
```


