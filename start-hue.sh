#!/bin/bash
# Fixup hue.ini
python /data/install/update-hue-ini.py /data/install/hue-template.ini /usr/local/hue/desktop/conf/hue.ini 

# Start hue if fixup is successful
if [ $? -eq 0 ]; then
    /usr/local/hue/build/env/bin/hue runserver 0.0.0.0:8000
else
    echo "Error generating hue.ini, HUE not started"
    exit 1
fi




