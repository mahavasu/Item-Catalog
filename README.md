# Item-Catalog

udacity_fullstack_project3
udacity Full Stack Web Developer Nanodegree Project 3 - Item Catalog

Files

1. application.py -- python script with flask main application
2. catalog.db -- sqlite database for item catalog
3. database_setup.py -- pathon script for sqlalchemy database schema
4. addDatabase.py -- python script to polulate database with sample data
5. static/styles.css -- css style for all views
6. templates/additem.html -- template for item add view
7. templates/catalog.html -- template for catalog and category overview
8. templates/deleteitem.html -- template for item delete view
9. templates/edititem.html -- template for item edit view
10. templates/item.html -- template for item view
11. templates/header.html -- header for all views
12. templates/footer.html -- footer for all views


Requirements

1. python
2. flask
3. sqlalchemy

How to run the program

1. Go the specified directory
2. Vagrant up
3. Vagrant ssh
4. Again change current working Directory to /vagrant/catalog

To reset database:

1. rm catalog.db
2. python database_setup.py
3. python addDatabase.py


To start application

python application.py

In Web browser type http://localhost:8000
