FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#EXPOSE 5252

#CMD ["fastapi", "run", "main.py", "--port", "5353"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5353"]