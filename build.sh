#!/usr/bin/env bash


ENV_FILE="./.env"

if [ -f "$ENV_FILE" ]; then
    source $ENV_FILE
else
    echo "Файл с переменными окружения не найден, идёт загрузка из хостинга"
fi


make install && psql -a -d $DATABASE_URL -f database.sql