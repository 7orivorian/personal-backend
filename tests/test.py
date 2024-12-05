from app.models.user import User
from app import app

app.app_context()

user = User.create(email='contact@7ori.dev', username='test', password='supersafepassword')
print(user.password)
