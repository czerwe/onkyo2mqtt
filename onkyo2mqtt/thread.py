import threading
import time
import logging
import json
import eiscp
import onkyo2mqtt.common


class mainloop(threading.Thread):
    """instance that regiser running jobs"""

    def __init__(self, ctx):
        super(mainloop, self).__init__(daemon=True)
        self.logger = logging.getLogger("threads::mainloop")
        self.ctx = ctx

    def run(self):
        self.logger.debug(f"Starting mainloop thread {id(self)}")
        while True:
            try:
                msg = self.ctx.receiver.get(3600)
            except Exception as e:
                self.logger.warning(f"exception on receiver.get: {e}")
            else:
                if msg is not None:
                    if msg.startswith("MVL"):
                        self.logger.info(f"Set Main Volume to {int(msg[-2:], 16)}")
                    else:
                        self.logger.debug(f"got msg: {msg}")

                    try:
                        parsed = eiscp.core.iscp_to_command(msg)
                        self.logger.debug(f"Parsed Message: {parsed}")
                        # Either part of the parsed command can be a list
                        if isinstance(parsed[1], str) or isinstance(parsed[1], int):
                            val = parsed[1]
                        else:
                            val = parsed[1][0]
                        if isinstance(parsed[0], str):
                            onkyo2mqtt.common.publish(parsed[0], val, msg)
                        else:
                            for pp in parsed[0]:
                                onkyo2mqtt.common.publish(pp, val, msg)
                    except Exception as e:
                        self.logger.info(f"parsing failed: {e}")
                        onkyo2mqtt.common.publish(msg[:3], msg[3:], msg)
