FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY app /app
COPY worker /app/worker
ENV TMPDIR=/tmp
EXPOSE 8080
CMD ["python", "api.py"]