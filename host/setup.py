#!/usr/bin/env python3
import setuptools

setuptools.setup(
    name = "hrapi",
    install_requires = {
        "bson==0.5.0",
        "connexion==1.1.16",
        "SQLAlchemy==1.1.14",
        "jsonschema==2.6.0",
    },
)
