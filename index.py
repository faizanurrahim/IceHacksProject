import os

from Nexa import NXserver
from routes.api import api
from routes.main import main, render_page
from routes.api_auth import authapi
from routes.description import description_api
from routes.dashboard import dashboard_api
from routes.careers import career_explorer_api
from routes.learning import learning_api
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
DEBUG_ENABLED = (
    False
    if APP_ENV == "production"
    else os.getenv("DEBUG", "true").strip().lower() in {"1", "true", "yes", "on"}
)
app = NXserver(__name__, debug=DEBUG_ENABLED)
app.route("/")(lambda:render_page("index.html"))
app.register_blueprint(description_api)
app.register_blueprint(api)
app.register_blueprint(main)
app.register_blueprint(authapi)
app.register_blueprint(dashboard_api)
app.register_blueprint(career_explorer_api)
app.register_blueprint(learning_api)


app.run()
