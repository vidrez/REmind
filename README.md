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
deploy/deploy_chall.sh /path/to/binary /re-webui/jsons/$num_chall_json
```

To correctly run the scripts, a venv with Python 3.10.x is required, with `ang` and `r2pipe` installed.

4. Modify the `re-webui/config.ini` file by adding

```
[chall $num]
challenge_num = $num
obfuscation = True
solution = $solution
```

5. In `/template` add a folder `template_$num`, copy it from another template, and modify the names and the content of all the HTML pages.

6. Add `$num_chall.py` changing:

```
bp = Blueprint('$num_chall', __name__, url_prefix='/$num_chall', template_folder='templates/template_$num/')

CHALL_ID = &num   # <--- ID of your challenge

json_path = './jsons/$num_chall_json/'
```

And all references to the HTML files in the rest of the code.

7. In `remind.py` modify and add

```
# Register Blueprints
    from . import auth, rev_webui, first_chall, fourth_chall, fifth_chall, seventh_chall, @num_chall    

    blueprints = [
        auth.bp,
        rev_webui.bp,
        first_chall.bp,
        fourth_chall.bp,
        fifth_chall.bp,
        seventh_chall.bp,
        @num_chall.bp,
    ]
```

8. Add the link to `/re-webui/templates/general/` with

```
<li><a id="$num_chall" href="$num_chall/?function=main">Added test</a></li>
```



### Another simpler option

If desired, you can replace an existing challenge in the program and substitute it with your own customized challenge.

It is sufficient to:

1. replace the json files created in step 3 with those of the experiment you want to replace,
2. change the solution in the `re-webui/config.ini` of the chosen experiment.

