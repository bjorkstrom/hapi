#!/usr/bin/env python3
import setuptools

setuptools.setup(
    name="hapi",
    packages=["hapi", "hapi.rest"],
    package_data={"hapi": ["swagger/*"]},
    install_requires = {
        "connexion==1.1.16",
        "SQLAlchemy==1.1.15",
        "jsonschema==2.6.0",
    },
)