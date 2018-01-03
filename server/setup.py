#!/usr/bin/env python
import setuptools

setuptools.setup(
    name="hapi",
    packages=["hapi", "hapi.rest"],
    package_data={"hapi": ["swagger/*"]},
    install_requires=[
        "connexion==1.1.16",
        "SQLAlchemy==1.1.15",
        "jsonschema==2.6.0",
        "pika==0.11.2",
        "PyMySQL==0.7.11",
        "boto3==1.4.8",
        "bcrypt==3.1.4",
    ],
)
