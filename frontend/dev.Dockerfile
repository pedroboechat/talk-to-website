# USING NODE 20.16.0 LTS
FROM node:20.16.0-alpine3.20

# SET WORKDIR
WORKDIR /srv/app

# COPY SOURCE FILES
COPY . .

# RUN ENTRYPOINT
ENTRYPOINT [ "sh", "/srv/app/dev.entrypoint.sh" ]
