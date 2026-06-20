FROM python:latest
WORKDIR /app
COPY requirements.txt
RUN pip install --no-cache-dir -r requirement.txt
COPY ..
ENV PYTHONUNBUFFERED=1
EXPOSE 5000
CMD ["python", "app.py"]
