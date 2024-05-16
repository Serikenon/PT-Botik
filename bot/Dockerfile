FROM python:3.10
WORKDIR /bot
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
CMD ["python3.10", "bot.py"]
