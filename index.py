from Nexa import Nserver,render_template
from routes.api import api
from routes.main import main
from routes.api_auth import authapi
from routes.description import description_api
from routes.dashboard import dashboard_api
from routes.careers import career_explorer_api
from routes.learning import learning_api
app = Nserver(__name__,debug=True)
app.route("/")(lambda:render_template("index.html"))
app.register_blueprint(description_api)
app.register_blueprint(api)
app.register_blueprint(main)
app.register_blueprint(authapi)
app.register_blueprint(dashboard_api)
app.register_blueprint(career_explorer_api)
app.register_blueprint(learning_api)


app.run()
