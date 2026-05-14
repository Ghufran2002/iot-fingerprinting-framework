FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python train.py

EXPOSE 7860

CMD ["python", "hf_run.py"]
