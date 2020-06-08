import logging
import eiscp
from .common import publish, sendavr, context


def msghandler(mqc, userdata, msg):
    logger = logging.getLogger("msghandler")
    ctx = context.Instance()

    rvd_payload = msg.payload.decode("utf-8")
    try:
        if msg.retain:
            return
        mytopic = msg.topic[len(ctx.mqtt_topic) :]
        if mytopic == "command":
            logger.info(f"command invocation: {rvd_payload}")
            sendavr(rvd_payload)
        elif mytopic[0:4] == "set/":
            cmd_to_iscp = f"{mytopic[4:]} {rvd_payload}"
            logger.info(f"Command to ISCP: {cmd_to_iscp}")
            llcmd = eiscp.core.command_to_iscp(cmd_to_iscp)
            logger.debug(f"llcmd: {llcmd}")
            sendavr(llcmd)
    except Exception as e:
        logging.warning("Error processing message: %s" % e)


def connecthandler(mqc, userdata, flags, rc):
    ctx = context.Instance()
    logging.getLogger("connecthandler").info(
        "Connected to MQTT broker with rc=%d" % (rc)
    )
    mqc.subscribe(ctx.mqtt_topic + "set/#", qos=0)
    mqc.subscribe(ctx.mqtt_topic + "command", qos=0)
    mqc.publish(ctx.mqtt_topic + "connected", 2, qos=1, retain=True)


def disconnecthandler(mqc, userdata, rc):
    logging.warning("Disconnected from MQTT broker with rc=%d" % (rc))
    time.sleep(5)
