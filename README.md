# Project Description

I was tasked with developing a Python IDE which can run unverified python code. Thus creating a
trusted execution environment using Docker was the safest way to implement. A docker image is created everytime a user executes code, and upon running the code, it will either timeout, run valid code, or return an error and then the docker image will be dropped. I used Postgres to store
code when the user clicks submit, only when the code is valid. Thus , users cannot access sensitive data or if malicious code is submitted to break the system, the Docker image will timeout.

## How to run

- Clone the repository
- Run npm install
- Run npm run dev
- Open VSCode and nagivate to backend.

# spin up a postgres db

- change the URI in the main.py file to your postgres db

# setup virtual environment

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# build docker image

docker build -t python-sandbox .

# run fast api app

./run.sh
