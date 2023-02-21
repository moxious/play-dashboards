#!/bin/bash

for file in `ls dashboards/*.json` ; do
  cat $file | jq --raw-output '.dashboard.panels[].datasource.type' 2>/dev/null >> datasource.type.txt
done

cat datasource.type.txt | sort | uniq
