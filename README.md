<h1 align="center"> 
Foodgram
</h1>

Foodgram is a project where users can share recipes for various dishes.

## Features
- REST API backend for SPA
- Registered users can create new recipes from the ingredients available on the site
- New ingredients can be added only by admin in admin section
- Regirtered users can add recipes and other users to favorites and put recipes to the shopping cart
- Cumulative list of ingredients from shopping cart can be downloded in PDF format
- Recipes can be shared by creating a short link to it
- Containerized with Docker (PostgreSQL, Nginx, backend, frontend)
- Implemented CI/CD pipeline with GitHub Actions (automatic testing and deployment)
- Configured Nginx as reverse proxy for backend/frontend

## 🛠️ Tech Stack

![Django](https://img.shields.io/badge/-Django-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/-DRF%20(Django%20REST)-8C1D40?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat&logo=nginx&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white)

## How to Deploy the Project

The project supports two versions: a development version and a production version. The development version is suitable for local setup, debugging, testing, and developing new features. The production version is intended for deployment on a remote server for end users.

To run the project locally, use the `docker-compose.yml` file. It is configured to build Docker images and start containers directly from the project code on your local machine. 

`docker-compose.production.yml` is used to run production version. The Docker images are taken from a remote repository on DockerHub.

### Local Deployment

To run the project locally, follow these steps:

1. Clone the repository and navigate into it:

```bash
git clone https://github.com/bashval/foodgram.git
cd foodgram
```

2. Create a `.env` file in the project directory. You can base it on the `.env.example` template.

3. Install Docker Compose:

```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```

4. Start the containers using the `docker-compose.yml` file:

```bash
sudo docker compose -f docker-compose.yml up -d
```

During startup, the containers automatically run database migrations, collect and copy static files, and load ingredients and tags into the database from CSV files.

The project will be accessible at [http://localhost:8000](http://localhost:8000).

---

### Remote Deployment

To deploy on a remote server:

1. Connect to the server via SSH:

```bash
ssh -i path_to_ssh_key/your_ssh_key user@server_ip
```

2. Install Docker Compose on the server:

```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```

3. Create a directory for the project and navigate into it:

```bash
mkdir foodgram
cd foodgram
```

4. Copy the production Docker Compose file to the server:

```bash
scp -i path_to_ssh_key/docker-compose.production.yml your_username@server_ip:/home/your_username/foodgram/docker-compose.production.yml
```

5. Create a `.env` file in the directory, based on `.env.example` or with your custom configuration.

6. Start the containers with the production compose file:

```bash
sudo docker compose -f docker-compose.production.yml up -d
```

Similar to local setup, containers will run database migrations, collect static files, and load ingredients and tags from CSV files.

The project will be available at `http://<server_ip>:8000`.

Optionally, you can configure an additional Nginx server to route requests from your domain to the Nginx container in Docker, enabling use of your custom domain name.

## GitHub Action Workflow

 The project is integrated with a `CI/CD` pipeline using GitHub Actions. [![Main Foodgram Workflow](https://github.com/bashval/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/bashval/foodgram/actions/workflows/main.yml)

The workflow is triggered automatically whenever a git push is made to any branch. During execution, automatic tests are run for both the frontend and backend. If all tests pass successfully, and only if the push is to the main branch, Docker images based on the latest code are built and uploaded to Docker Hub. 

In the future, the project on the remote server will be automatically deployed using these images for production. 

## Authors

Backend developer, Docker instructions and CI/CD implementation by : [Valentin Bashkatov](https://github.com/bashval).
