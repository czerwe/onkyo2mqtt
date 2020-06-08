from setuptools import setup


setup(
    name="onkyo2mqtt",
    version="0.7.0",
    description="Reads prometheus metrics and produces changes to mqtt",
    author="cze",
    author_email="ernest@czerwonka.de",
    packages=["onkyo2mqtt"],
    install_requires=[
        "Flask>=1.1.1",
        "prometheus_flask_exporter",
        "gunicorn",
        "onkyo-eiscp",
        "paho-mqtt",
    ],
    # entry_points={"console_scripts": ["onkyo2mqtt = onkyo2mqtt.cmd:cli"]}
)
