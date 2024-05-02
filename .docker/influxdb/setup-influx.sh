#!/bin/bash
set -e

# Wait for influxdb service to start
echo "Waiting for influxdb service to start..."
sleep 15

influx setup -f --username=admin --password=gsofpwr0342fj24u4asdasf -o ringobot --bucket coinDB -t gsofpwr0342fj24u4asdasf --host=http://influxdb:8086 || true
