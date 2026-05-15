FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Train models at build time so cold starts are instant
RUN python train.py || echo "train.py warning — models will train on first boot"

EXPOSE 7860

CMD ["python", "hf_run.py"]
