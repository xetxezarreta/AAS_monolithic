FROM python:3.6
ADD ./monolithic/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
# EXPOSE 8000
# ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
ENTRYPOINT gunicorn -b 0.0.0.0:${GUNICORN_PORT} app:app
