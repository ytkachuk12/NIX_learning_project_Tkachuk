FROM python:3.9

WORKDIR /app

ENV PYTHONDONTWRITEBITECODE 1
ENV PYTHONUNBUFFERED 1
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000

# Add flask to the environment variables
CMD ["export", "FlASK_APP=app.py"]

#CMD ["python", "app.py"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
