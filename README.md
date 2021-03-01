# Docker-Website

This dockerized project creates a simple REST application by using the Flask framework.

Data is stored in the relational database MySQL which is located in a secondary container.

A third container connects Adminer to the MySQL database which provides a graphical interface for the MySQL database.

# Getting started
Prerequisites: In order to run this application you need to have Docker installed on your machine.

To start the 3 containers:
1. docker-compose build --no-cache
2. docker-compose up


Connect to the database in a terminal: 
1. docker ps -> find <container_id> for the MySQL image
2. docker exec -it <container_id> mysql -p

# Useful links
1. Website: http://localhost:8000/
2. Adminer: http://localhost:8080/