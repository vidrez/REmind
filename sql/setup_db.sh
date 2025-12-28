#! /bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../db.env"

if [ ! -f "$ENV_FILE" ]; then
echo "Error: Environment file not found at $ENV_FILE"
exit 1
fi

while read -r line || [ -n "$line" ]; do
    clean_line=$(echo "$line" | sed -e 's/\#.*//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]\*$//')
    [ -z "$clean_line" ] && continue
    export "$(echo "$clean_line" | sed -e 's/["'\'']//g' -e 's/\r$//')"
done < $ENV_FILE

docker exec -i remind_db mysql -u root -p$MYSQL_ROOT_PASSWORD $MYSQL_DATABASE < "$SCRIPT_DIR/schema.sql"
docker exec -i remind_db mysql -u root -p$MYSQL_ROOT_PASSWORD --execute "SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));"
docker exec -i remind_db mysql -u root -p$MYSQL_ROOT_PASSWORD --execute "GRANT ALL PRIVILEGES ON $MYSQL_DATABASE.* TO '$MYSQL_USER'@'%';"
docker exec -i remind_db mysql -u root -p$MYSQL_ROOT_PASSWORD --execute "FLUSH PRIVILEGES;"