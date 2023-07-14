FROM python:latest

WORKDIR /Supplier

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME [ "/Supplier/logs", "/Supplier/resources"]

CMD [ "python", "./main.py" ]