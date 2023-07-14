FROM python:latest

WORKDIR /StormTrooper

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME [ "/StormTrooper/resources", "/StormTrooper/logs"]

CMD [ "python", "./main.py" ]