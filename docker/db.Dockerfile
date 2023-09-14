FROM postgres
COPY ./scripts/install-extensions.sql /docker-entrypoint-initdb.d