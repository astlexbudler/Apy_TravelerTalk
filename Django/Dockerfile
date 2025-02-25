FROM python:3.10
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install djangorestframework
COPY . /app/
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]