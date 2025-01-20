import os
from datetime import datetime, timedelta

from app import create_app, db


def clean_revoked_tokens():
    expiration = datetime.now() - timedelta(days=30)  # Example: 30-day expiration
    from app.models.revoked_token import RevokedToken
    RevokedToken.query.filter(RevokedToken.revoked_at < expiration).delete(commit=False)
    db.session.commit()


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    clean_revoked_tokens()

    app.run(debug=True, port=os.getenv("PORT", default=8080))
