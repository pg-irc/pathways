FROM postgres:9.6

COPY ./docker/production/postgres/backup.sh /usr/local/bin/backup
RUN chmod +x /usr/local/bin/backup

COPY ./docker/production/postgres/restore.sh /usr/local/bin/restore
RUN chmod +x /usr/local/bin/restore

COPY ./docker/production/postgres/list-backups.sh /usr/local/bin/list-backups
RUN chmod +x /usr/local/bin/list-backups
