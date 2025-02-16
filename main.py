import os
from datetime import datetime, timedelta

from flask_migrate import upgrade

from app import create_app, db

app = create_app()


def clean_revoked_tokens():
    expiration = datetime.now() - timedelta(days=30)  # Example: 30-day expiration
    from app.models.revoked_token import RevokedToken
    RevokedToken.query.filter(RevokedToken.revoked_at < expiration).delete(commit=False)
    db.session.commit()


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://princeling.dev')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    upgrade()

    app.run(debug=True, port=os.getenv("PORT", default=8080))

    clean_revoked_tokens()
