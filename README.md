# Cat9k_EDiag
Clone repository. Install python and run:
./device_status.py

This will create edge_analytics.html in the same directory.
Open html file in browser and you are in business :)

Please refer to https://github.com/CiscoDevNet/cat9k-device-monitoring-app
for more information about the basic monitoring app.

## Running server
1. pip install flask
2. FLASK_APP=server.py flask run
3. For html table open browser to http://127.0.0.1:5000/device_status.html
4. For json http://127.0.0.1:5000/device_status.json

example output:
```json
{
    "state": {
        "auto-negotiate": "false",
        "enable-flow-control": "false",
        "negotiated-duplex-mode": "full-duplex",
        "negotiated-port-speed": "speed-1gb"
    },
    "stats": {
        "in-errors": "0",
        "in-mac-control-frames": "0",
        "in-mac-pause-frames": "0",
        "in-octets": "164902",
        "out-errors": "0",
        "out-mac-control-frames": "0",
        "out-mac-pause-frames": "0",
        "out-octets": "132751042"
    },
    "summary": [
        "Application hosting interface is up",
        "No packet errors seen on the interface",
        "No MAC Pause frames seen on the interface"
    ]
}
```
