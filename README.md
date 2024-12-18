# Backend for my Personal Website!

This is the backend of my personal website, built with Flask, SQLAlchemy, &
an SQLite database. The frontend can be
found [here](https://github.com/7orivorian/personal-website-react).

## Installation

First make sure you're `cd`'d into the project root.

1. Run `python -m venv venv`
2. Run `venv/Scripts/activate`
3. Run `pip install -r requirements.txt`
4. Run `flask db init | flask db migrate | flask db upgrade`
5. Run `flask run`
