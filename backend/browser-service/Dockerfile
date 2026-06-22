FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1

EXPOSE 3001

CMD ["uvicorn", "browser_service.main:app", "--host", "0.0.0.0", "--port", "3001"]
