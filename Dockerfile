FROM python:3.9-slim
ENV BOT_TOKEN="6884392040:AAFoWQzgOUCQjK1icKy28AAqRIkn_bHB_mY"
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir /app/logger/log
RUN mkdir /app/saved/sessions
CMD ["python", "main.py"]