FROM python 
WORKDIR /app

COPY . .
RUN apt-get update
RUN apt-get install nano
RUN pip install bs4 && pip install psycopg2-binary 

ENTRYPOINT [ "/bin/bash" ]