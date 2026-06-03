FROM python:3.11-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--port", "8000"]