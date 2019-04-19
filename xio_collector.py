#!/usr/bin/env python3

import os
import socket
import json
import sys
import logging
import coloredlogs
import requests
import urllib3

alfred = logging.getLogger("Xio_Collector")
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=alfred)
alfred.info("Begining Xio_Collector script")


def send_to_target_api(payload, target_api_url):
    """Method to send full payload to API endpoint

    Sends the payoad to the api endpoint specificied in our
    environement variable captured in the begining of the script.

    Args:
        payload: json object containing the fields required by our storage API

    Returns:
        None
    """
    alfred.info(f"Making post request to: {target_api_url}")
    json_payload = json.dumps(payload)
    headers = {'Content-type': 'application/json',
               'Accept': 'Application/json'}
    try:
        r = requests.put(target_api_url,
                         data=json_payload,
                         headers=headers,
                         verify=False)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        alfred.critical(f"Critical error trying to post to api: {e}")
        sys.exit(1)
    except requests.exceptions.HTTPError as err:
        alfred.error(f"HTTP error trying to post to api: {err}")
        sys.exit(1)


def get_xio_info(req):
    """ Method to get xio array information

    Gather XIO array cluster information

    Args:
      xioarrayname: name of an XIO array
      xiouser: admin user name
      xiopasswd: password of admin user

    Return:
      xioarrayinfo: xio array information in json format
    """

    xiourl = f"https://{req['xioarrayname']}/api/json/v2/types/clusters/1"
    xioapiresp = requests.get(xiourl,
                              auth=(req['xiouser'], req['xiopasswd']),
                              verify=False).json()

    model = xioapiresp['content']['size-and-capacity']
    sn = xioapiresp['content']['sys-psnt-serial-number']
    version = xioapiresp['content']['sys-sw-version']
    totalsize = xioapiresp['content']['ud-ssd-space']
    sizeinuse = xioapiresp['content']['ud-ssd-space-in-use']
    model = 'XtremIO' + ' ' + model
    tier = 'performance'
    vendor = 'DellEMC'
    usable = (float(totalsize) - float(sizeinuse)) / (2**30)
    totalsize = float(totalsize) / (2**30)

    xioarrayinfo = {
      "array_name": req['xioarrayname'],
      "serial_number": sn,
      "vendor": vendor,
      "model": model,
      "version": version,
      "tier": tier,
      "capacity": {
         "available_TBu": float(round(usable, 3)),
         "usable_TBu": float(round(totalsize, 3))
         },
    }

    return xioarrayinfo


def handle(req):
    """Gather Xio array information and send it to storage api target

    Gather Xio array information, create a json array object
    and send it to storage api taret

    Args:

    Return:
       None
    """

    try:
        socket.gethostbyname(req['xioarrayname'])
    except:
        alfred.error(f"Invalid Xio Array Name: {req['xioarrayname']}")
        sys.exit(1)

    alfred.info(f"Collecting Xio Array Information: {req['xioarrayname']}")

    xioarrayinfo = get_xio_info(req)

    alfred.debug(f"""Getting ready to send payload to API endpoint.
                 Here is the payload: {json.dumps(xioarrayinfo)}""")

    send_to_target_api(xioarrayinfo, req['target_api_url'])

    sys.exit(0)


if __name__ == "__main__":
    payload = {}
    payload['xioarrayname'] = os.environ['XIO_ARRAYNAME']
    payload['xiouser'] = os.environ['XIO_USERNAME']
    payload['xiopasswd'] = os.environ['XIO_PASSWD']
    payload['target_api_url'] = os.environ['TARGET_API_URL']

    handle(payload)
