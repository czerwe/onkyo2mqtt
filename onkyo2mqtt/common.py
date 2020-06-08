import logging
import time
import json
import os
import eiscp
from .thread import mainloop


class Singelton:
    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError("Singletons must be accessed through `Instance()`.")

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


@Singelton
class context(object):
    """docstring for context"""

    def __init__(self):
        self._last_send = 0

        self._mqtt_host = os.environ.get("O2M_MQTT_HOST", "localhost")
        self._mqtt_port = int(os.environ.get("O2M_MQTT_PORT", "1883"))
        self._mqtt_topic = os.environ.get("O2M_MQTT_TOPIC", "onkyo/")
        self._onkyo_address = os.environ.get("O2M_ONKYO_ADDRESS", None)
        self._onkyo_id = os.environ.get("O2M_ONKYO_ID", None)
        self.receiver = None
        self.mainthread = None

    @property
    def last_send(self):
        return self._last_send

    @last_send.setter
    def last_send(self, value):
        self._last_send = value

    @property
    def receiver(self):
        return self._receiver

    @receiver.setter
    def receiver(self, value):
        self._receiver = value

    @property
    def mqc(self):
        return self._mqc

    @mqc.setter
    def mqc(self, value):
        self._mqc = value

    @property
    def mqtt_host(self):
        return self._mqtt_host

    @property
    def mqtt_port(self):
        return self._mqtt_port

    @property
    def mqtt_topic(self):
        if not self._mqtt_topic.endswith("/"):
            return f"{self._mqtt_topic}/"
        return self._mqtt_topic

    @property
    def onkyo_address(self):
        return self._onkyo_address

    @property
    def onkyo_id(self):
        return self._onkyo_id

    def start_thread(self):
        self.mainthread = mainloop(self)
        self.mainthread.start()


def callback_loglevel(value):
    value = value.lower()

    if value == "info":
        return logging.INFO
    elif value == "debug":
        return logging.DEBUG
    elif value == "error":
        return logging.ERROR
    elif value == "warning":
        return logging.WARNING
    elif value == "critical":
        return logging.CRITICAL

    return logging.INFO


def sendavr(cmd):
    logger = logging.getLogger("sendavr")
    ctx = context.Instance()
    now = time.time()
    if now - ctx.last_send < 0.05:
        time.sleep(0.05 - (now - ctx.last_send))
    ctx.receiver.send(cmd)
    ctx.last_send = time.time()
    logger.info(f"Sent command '{cmd}'")


def publish(suffix, val, raw):
    ctx = context.Instance()
    logger = logging.getLogger("publish")
    robj = {}
    robj["val"] = val
    logger.info(f"val: {val}")
    if raw is not None:
        logger.info(f"raw: {raw}")
        robj["onkyo_raw"] = raw

    topic = ctx.mqtt_topic + "status/" + suffix
    value = json.dumps(robj)
    logger.debug(f'public to "{topic}": "{value}"')
    ctx.mqc.publish(topic, value, qos=0, retain=True)


def get_receiver(onkyo_address=None, onkyo_id=None):
    if onkyo_address:
        receiver = eiscp.eISCP(onkyo_address)
    else:
        app.logger.info("Starting auto-discovery of Onkyo AVRs")
        receivers = eiscp.eISCP.discover()
        for receiver in receivers:
            app.logger.info(
                "Disocvered %s at %s:%s with id %s"
                % (
                    receiver.info["model_name"],
                    receiver.host,
                    receiver.port,
                    receiver.info["identifier"],
                )
            )
        if onkyo_id:
            receivers = [r for r in receivers if onkyo_id in r.info["identifier"]]
        if len(receivers) == 0:
            app.logger.warning("No specified AVRs discovered")
            exit(1)
        elif len(receivers) != 1:
            app.logger.warning(
                "More than one AVR discovered, please specify explicitely using environemnt Variable O2M_ONKYO_ADDRESS or O2M_ONKYO_ID"
            )
            exit(1)
        receiver = receivers.pop(0)
        app.logger.info(f"Discovered AVR at {receiver}")
    return receiver
