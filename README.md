# REmind - REborn

Forked repository from REmind, with refactored code and new features.

## Setup Instructions

### Prerequisites

- Linux distribution (e.g., Ubuntu)
- Python 3.8 or higher
- pip (Python package installer)
- virtualenv (optional but recommended)
- Docker and docker compose (for containerized deployment)
- Git

### Steps for dockerized setup

1. Setup `app.env` and `db.env` files in the root directory of the repo, based on the provided templates `app.env.example` and `db.env.example`.
2. Execute `docker compose up --build -d` in the root directory of the repo.
3. Run the `sql/setup_db.sh` bash script to initialize the database.
4. Access the web interface at `http://localhost:4000`

## Deployment

When deploying in production there are a few key changes to consider:

1. You should use `compose-prod.yaml` which sets up an nginx reverse proxy and a `certbot` service to get your HTTPS certificate. So instead of `docker compose up -d` you'll use `docker compose -f compose-prod.yaml up -d`, or just rename it as `docker-compose.yaml` if you find it more convenient.
2. You should remember to open the necessary ports on your firewall (eg. `ufw allow https` if using ufw).
3. Setup some proper credentials and secret key for the app (check out https://flask.palletsprojects.com/en/stable/tutorial/deploy/#configure-the-secret-key).
4. Make sure to set "production" as your FLASK_ENV.
5. Update the `nginx/conf.d/remind.conf` with your own domain.
6. Setup your domain/subdomain. In many cases it's as easy as creating an A record pointing to the IP address of your server.

For the setup itself the steps remain the same. After you made sure that you can reach the app via http generate the HTTPS certificate running (change the email and domain):

```
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  -d remind.example.com \
  --email you@example.com \
  --agree-tos \
  --no-eff-email
```
And restart the nginx service with:

```
docker compose restart nginx
```
Now you should be able to correctly reach the app with https and the certificate should be valid. For the renewal you'll need to setup a cron job or similar running the command:

```
docker compose run --rm certbot renew && docker compose restart nginx
```

That's all folks!

## Something broke?

<img width="498" height="272" alt="image" src="https://github.com/user-attachments/assets/c31bc64b-66a0-4522-bdf2-8ddb83133894" />

No but really, have you tried?

### Exibit A: Nginx 502 Bad Gateway

After recreating my container nginx decided to break, likely some weirdness in the nginx container not expecting the app to go down and be unreachable, how to fix? **restart the nginx service**. 

## Updated guide for adding a challenge

1. Take a binary (tested and working on compiled from C)
2. From now on, `$num` represents a general number (for example 9) that is not already used in the other experiments
3. Generate the json files through the script:

```
deploy/deploy_chall.sh /path/to/binary /re-webui/jsons/chall_$num_json
```

To correctly run the scripts, a venv with Python 3.10.x is required, with `ang` and `r2pipe` installed.

4. Modify the `re-webui/config.ini` file by adding:

```
[chall $num]
challenge_num = $num
solution = $solution
```

5. In the same `config.ini` file, update the challs number under the DEFAULT section to the new total number of challenges:

```
[DEFAULT]
challs : $total_challs_number
experiment_mode : 1
```

