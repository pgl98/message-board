FROM python:3

ENV FLASK_APP app.py
ENV FLASK_CONFIG development

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .

ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]