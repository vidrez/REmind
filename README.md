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
4. Access the web interface at `http://localhost:4000`.

## How to generate disassembly and other binary analysis files

Simply, from the root directory of the repo, run `./deploy_chall.sh /path/to/binary_file /path/to/output`


## Deploy a new challenge

As of now, you just need to edit the config.ini accordingly to the new chall configurations, then adding a blueprint using the template_chall.py as a skeleton, and of course read the previous point for the disassembly/strings/binary info generation. 

For the frontend, the `static` directory includes the three main .js files that work as a library to make the challenge running. Just include them in an .html file with the name of the chall and copy the .html skeleton if you don't want any specific behavior.

TODO: implement an automatic way of doing that...

