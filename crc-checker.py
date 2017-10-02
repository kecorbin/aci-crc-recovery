import os
import websocket
import json
import requests
from acitoolkit.acitoolkit import Session

# TODO: these gotta go somewhere else
URL = os.getenv('APIC_URL')
USER = os.getenv('APIC_LOGIN')
PASSWORD = os.getenv('APIC_PASSWORD')
roomId = os.getenv('SPARK_ROOM_ID')
token = os.getenv('SPARK_TOKEN')

if not all([URL, USER, PASSWORD]):
    print """
    Please make sure you have set the following environment variables

    e.g.
    export APIC_URL=http://myapic
    export APIC_LOGIN=admin
    export APIC_PASSWORD=supersecret
    export SPARK_ROOM_ID=sdlkfj23lkj42l4kjslk
    export SPARK_TOKEN=4klj42lkj23lkj234lkjlkdsjfsadfdff8sf8sd7f987324uwsdf

    """
    exit(1)

headers = {"Content-Type": "application/json",
           "Authorization": "Bearer {}".format(token)}


test_port = "topology/pod-1/paths-103/pathep-[eth1/29]"

# may also want to be able to exclude ports
excluded_ports = []


def send_spark_message(msg):
    url = "https://api.ciscospark.com/v1/messages"
    payload = {"roomId": roomId,
               "text": msg}
    return requests.post(url, json.dumps(payload), headers=headers)


def pathep_from_phys(physdn):
    """
    returns pathep dn from phys dn
    e.g. topology/pod-1/node-101/sys/phys-[eth1/50] becomes topology/pod-1/paths-103/pathep-[eth1/71]
    """
    pathep = physdn.replace('node', 'paths')
    pathep = pathep.replace('phys', 'pathep')
    pathep = pathep.replace('/sys/', '/')
    return pathep


def shutdown_port(pathep):
    """
    shuts down a port given a pathep
    """
    payload = {"fabricRsOosPath": {"attributes": {"tDn": "{}".format(pathep), "lc": "blacklist"}, "children": []}}
    return session.push_to_apic('/api/node/mo/uni/fabric/outofsvc.json', payload)


def on_close(ws):
    print "### closed ###"


def on_message(ws, message):
    msg = json.loads(message)
    for i in msg['imdata']:
        # only shutdown physical ports
        if 'phys' in i['rmonEtherStats']['attributes']['dn']:
            phys = "/".join(i['rmonEtherStats']['attributes']['dn'].split('/')[:-1])
            dn = pathep_from_phys(phys)
            if 'cRCAlignErrors' in i['rmonEtherStats']['attributes']:
                if dn not in excluded_ports:
                    print "Shutting Down {}:".format(dn) + shutdown_port(dn).text
                    if roomId and token:
                        send_spark_message("Detected {} CRC errors on {}. Shutting it down".format("", dn))

if __name__ == "__main__":

    # Establish an API session to the APIC
    session = Session(URL, USER, PASSWORD)
    if session.login().ok:
        print "Logged into APIC"

        # Create a websocket
        ws = websocket.WebSocketApp("ws://{}/socket{}".format(session.ipaddr, session.token),
                                    on_message=on_message,
                                    on_close=on_close)
        # create a subscription
        subscription_id = session.get('/api/class/rmonEtherStats.json?subscription=yes').text
        ws.run_forever()
    else:
        print "Could not login to apic"
