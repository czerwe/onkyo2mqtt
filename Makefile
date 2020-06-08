.PHONY: runbe

assert-command-present = $(if $(shell which $1),,$(error '$1' missing and needed for this build))

runbe:
	$(call assert-command-present, gunicorn)
	O2M_LOGLEVEL=debug O2M_MQTT_TOPIC=testonkyo/ O2M_MQTT_HOST=mosquitto.service.consul O2M_ONKYO_ADDRESS=onkyo.tpf.local gunicorn --bind 0.0.0.0:8000 --timeout 120 onkyo2mqtt:app
