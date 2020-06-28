from flask import Flask
import os
import logging
from .common import sendavr, publish, callback_loglevel, get_receiver, context


from prometheus_flask_exporter import PrometheusMetrics
# from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics
import paho.mqtt.client as mqtt
from .mqtt_handler import msghandler, connecthandler, disconnecthandler

# FE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "frontend")
_version = "0.9.0"

ctx = context.Instance()

logging.basicConfig(
    level=callback_loglevel(os.environ.get("O2M_LOGLEVEL", "warning")),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# app = Flask(__name__, static_url_path="", static_folder=FE_DIR)
app = Flask(__name__)

# metrics = GunicornPrometheusMetrics(app)
metrics = PrometheusMetrics(app)

# static information as metric
metrics.info('app_info', 'Application info', version=_version)

# app.route("/version", methods=["GET"])(version_info)

@app.route('/version')
def version():
    logger = logging.getLogger('route::version')
    logger.debug('called version')
    global version
    return version

@app.route("/")
def root():
    logger = logging.getLogger('route::root')
    logger.debug('called Root')
    return ''

ctx.mqc = mqtt.Client()
ctx.mqc.on_message = msghandler
ctx.mqc.on_connect = connecthandler
ctx.mqc.on_disconnect = disconnecthandler
ctx.mqc.will_set(ctx.mqtt_topic + "connected", 0, qos=2, retain=True)
ctx.mqc.connect(ctx.mqtt_host, ctx.mqtt_port, 60)
ctx.mqc.publish(ctx.mqtt_topic + "connected", 1, qos=1, retain=True)

ctx.receiver = get_receiver(onkyo_address=ctx.onkyo_address, onkyo_id=ctx.onkyo_id)

app.logger.info(f'Starting onkyo2mqtt V{_version} with topic prefix "{ctx.mqtt_topic}"')


for icmd in ("PWR", "MVL", "SLI", "SLA", "LMD"):
    sendavr(icmd + "QSTN")

ctx.mqc.loop_start()
ctx.start_thread()
