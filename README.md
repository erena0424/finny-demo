# Finny-demo
This repository contains a modified version of a website called "Finny" to exclude sensitive information.

## About Finny
An online service that helps people in Japan find services related to their studies. While numerous network-based platforms provide a variety of different learning services at a low cost in Japan, they are not well known. I believe better awareness of these services can make studying more accessible to a wider audience. Although education in Japan can be uniform, access to these resources fosters personalized learning for both children and professionals.

demonstration video:

https://github.com/erena0424/finny-demo/assets/124848190/b987652c-dc5a-4423-9738-316eafb71447


## Installation
To compile it from source:

### Clone this repository
```
git clone https://github.com/erena0424/finny-demo 
```

### Make a virtual environment and install necessaray liblaries
```
conda create -n finny python=3.11.4 
conda activate finny 
pip install -r requirements.txt 
```

## Configuration

This project requires some configuration settings in `flaskblog/config.py` to be set as environment variables. Here are the necessary settings:

- `SECRET_KEY`: A secret key for your application.
- `DATABASE_URL`: The database URL for SQLAlchemy.

Please add the environment variables or edit flaskblog/config.py to set these variables.


To run the application, please
run the `run.py` script.
Additionally, I added add_user.py under the migrations folder for reference. If you need to alter the database after creating it, please make a new migration.
