# Books App
This project 'Books App' is my own customized version of Udacity's project 'Item catalog' which is part of Udacity's full-stack nanodegree. The app aims to organise books into categories and both of them -the categories and the books- can be created, edited or deleted by the authorized users.

The app is minimalist focusing only on the back-end and the design wasn't taking into consideration at all. 

## Table of Contents
* [Installation Guide](#installation-guide)
* [App Logic](#app-logic)

## Installation Guide
* Make sure you have python3 installed, if not download it from [here](https://www.python.org/downloads/)
* Install vagrant, VM and configuration file
    * download and install virtual box version that corresponds to your operating system from [here](https://www.virtualbox.org/wiki/Downloads)
    * download and install vagrant version that corresponds to your operating system from [here](https://www.vagrantup.com/downloads.html)
    * make sure that vagrant is installed by running this command in your terminal `vagrant --version`. N.B. if you're using windows OS, you will need to install and use git terminal
    * Clone this repository and start the vm
        * clone this repository using 
            ```
            git clone https://github.com/i-mw/books-app
            ```
        * `cd` to the project
            ```
            cd books-app
            ```
        * start the virtual machine by running `vagrant up`. This will cause Vagrant to download the Linux operating system and install it.

* Run vagrant Virtual machine:
    * `vagrant ssh`
* From vagrant terminal:
    * `cd /vagrant` to move to the shared folder which is the project folder
    * run the following command to install the needed modules:
        * 
        ```
        pip3 install flask sqlalchemy oauth2client requests
        ```
    * initiate the database by running:
        ```
        python3 database_setup.py
        ```
    * populate the database by running:
        ```
        python3 lotsofbookswithusers.py
        ```
    * Run the app:
        ```
        python3 app.py
        ```
* From your own browser:
    * go to `localhost:8000` to view the app


## App Logic
* An unlogged user can only view/read the categories and books
* A logged user who didn't create anything yet, in addition to viewing all the content, can only add new categories or books.
* A logged user who created a book or category, in addition to viewing and adding content, can edit and delete the content he has created.