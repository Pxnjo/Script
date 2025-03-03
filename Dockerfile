FROM python:3.11.9
WORKDIR /usr/local/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main_project ./main_project
EXPOSE 443

RUN useradd app
RUN chown -R app:app /usr/local/app
USER app

VOLUME ["/usr/local/app/main_project/logs"]

ENTRYPOINT [ "python3", "main_project/script.py" ]