# Guardar dependencias en requirements.txt

```bash
  pip freeze > requirements.txt
```


# Puesta en marcha

```bash
  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
  python -m venv venv
  venv\Scripts\activate
  pip install --upgrade -r requirements.txt
  uvicorn app.main:app --host 0.0.0.0 --port 8000
```