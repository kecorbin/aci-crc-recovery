# aci-crc-recovery

This is a simple demonstration of disabling interfaces which have incrementing CRC errors

There are two main components in this repo

## [generator.py](./generator.py) - CRC generation

Largely based on the following URL
https://stackoverflow.com/questions/6329583/how-to-reliably-generate-ethernet-frame-errors-in-software

This project adds a simple REST api on top for easily generating errors on demand
Unforunately, this only works on bare metal servers w/ an e1000 NIC

**Note**this script needs to be ran as superuser to bind raw sockets

### Running

```
sudo python generator.py
```

### Usage

You can use the API to generate a number of CRC errors on the specified interface

```
curl -X POST 127.0.0.1:5050/api/errors/10

```

## [crc-checker.py](./crc-checker.py)

This script performs the actual work of monitoring for CRC errors and disabling ports.

The script requires some environment variables to be set, a sample is provied [here](./.env.sample)


It performs the following steps

1. Login to APIC
2. Create a websocket subscription to the ACI fabric (currently subscribing to rmonEtherStats)
3. Upon receiving a message on the websocket, it checks to see if the message contains an updated cRCAlignErrors key
4. If so, it will blacklist the port
5. The script will notify the user of ports being disabled via the console, and additionally via Cisco Spark
   provided that the following environment variables are set
   - SPARK_ROOM_ID
   - SPARK_TOKEN
