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

