#!/usr/bin/env python3

import connexion

if __name__ == "__main__":
    app = connexion.FlaskApp(__name__, port=9090, specification_dir="swagger/")
    app.add_api("hagring-api.yaml",
                arguments=dict(title="Hägring Cloud"))
    app.run()
