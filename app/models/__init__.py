# importing all models so SQLAlchemy/Alembic can detect them
from app.models.user import User
from app.models.application import Application
from app.models.refresh_token import RefreshToken