Hijos 🕯⛓⚒⚔️
=====

Free, open, small and simple lodge book-keeping management system

Features
---------

* Multiple lodge invoicing 💵
* 🇬🇧English and 🇪🇸Spanish supported
* Keep track of expenses, debtors, donors, etc. 💸💸
* Send individual account balance email or mass account balances to each member. 🔨


Technical description
----------------------

`hijos` is a small and simple management system built on [Django](https://www.djangoproject.com), [SQLite](https://www.sqlite.org) and [Docker](https://www.docker.com). Currently it just supports English and Spanish.


Getting Started
----------------

Thanks to `docker` and `git`, it's quite easy to setup. Assuming you have already installed both of them, for a local (testing/development) setup:

    $ git clone git@github.com:mbaragiola/hijos.git

    $ cd hijos

    $ cp config/settings/base.py.example config/settings/base.py

    $ cp config/settings/local.py.example config/settings/local.py

Edit both configs as you please.

    $ docker-compose build

    $ docker-compose run django python manage.py migrate

    $ docker-compose run django python manage.py createsuperuser

    $ docker-compose up

If you go to http://localhost:8000 (Linux) or http://192.168.99.100:8000 (macOS) you can start using `hijos` by logging with the username and password provided in the step before.

Going to http://localhost:8000/admin/ you can create a new lodge with its categories (i.e., Simple and Student Discount) with its corresponding prices.

For everything else, you can use the regular views on the main menu 
