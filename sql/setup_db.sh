#! /bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" =~ ^# ]] && continue
    declare "$key=$value"
done < $SCRIPT_DIR/../db.env

docker exec -i remind_db mysql -u root -p$MYSQL_ROOT_PASSWORD $MYSQL_DATABASE < "$SCRIPT_DIR/schema.sql"
docker exec -i remind_db mysql -u root -p$MYSQL_ROOT_PASSWORD --execute "SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));"
docker exec -i remind_db mysql -u root -p$MYSQL_ROOT_PASSWORD --execute "GRANT ALL PRIVILEGES ON $MYSQL_DATABASE.* TO '$MYSQL_USER'@'%';"
docker exec -i remind_db mysql -u root -p$MYSQL_ROOT_PASSWORD --execute "FLUSH PRIVILEGES;"