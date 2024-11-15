## Dule Chat

To setup virtual environment, run the following command:

```bash
python -m venv venv
```

To run alembic migrations, run the following command:

```bash
alembic upgrade head
```

To run the application, run the following command:

```bash
call venv\Scripts\activate

pip install -r requirements.txt

flet run --web --port 80 main.py
```