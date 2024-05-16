FROM postgres:latest
COPY init.sql .
RUN apt update && apt install gettext-base
RUN export DB_REPL_USER=repl_user && export DB_REPL_PASS=Qq123456 && export DB_NAME=db_for_tgbot && envsubst < "init.sql" > "/docker-entrypoint-initdb.d/init.sql"
RUN mkdir -p /oracle/pg_data/archive/ && chown -R postgres:postgres /oracle && chown -R postgres:postgres /oracle/*
CMD ["postgres"]
