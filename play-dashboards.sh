#!/bin/bash

for uid in $(curl --silent https://play.grafana.org/api/search?query= | jq --raw-output '.[].uid') ; do
  curl --silent "https://play.grafana.org/api/dashboards/uid/$uid" > "dashboards/$uid.json"
done
