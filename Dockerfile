FROM python:3.6

WORKDIR /user/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "python" ]
CMD [ "scrapper.py" ]