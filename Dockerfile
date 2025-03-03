FROM python:3.11.9
WORKDIR /usr/local/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./main_project ./
EXPOSE 443

RUN useradd app
USER app

CMD [ "python", "./script.py" ]