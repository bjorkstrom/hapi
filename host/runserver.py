#!/usr/bin/env python3

import connexion
import database
from connexion import resolver

app = connexion.FlaskApp(__name__, port=9090, specification_dir="swagger/")
app.add_api("hagring-api.yaml",
            validate_responses=True,
            resolver=resolver.RestyResolver("rest"),
            # TODO disable swagger UI in production?
            # swagger_ui=False
            arguments=dict(title="Hägring Cloud"))

@app.app.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()


if __name__ == "__main__":
    app.run()
