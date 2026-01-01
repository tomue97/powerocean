"""ecoflow.py: API for PowerOcean integration."""

import requests
import datetime,time
import base64
import json
import re
import hashlib, hmac
import os

from collections import namedtuple
from homeassistant.exceptions import IntegrationError
from requests.exceptions import RequestException, Timeout

from .const import _LOGGER, ISSUE_URL_ERROR_MESSAGE


# Better storage of PowerOcean endpoint
PowerOceanEndPoint = namedtuple(
    "PowerOceanEndPoint",
    "internal_unique_id, serial, name, friendly_name, value, unit, description",
)


# ecoflow_api to detect device and get device info, fetch the actual data from the PowerOcean device, and parse it
class ecoflow_api:
    def __init__(self, serialnumber, accessKey, secretKey):
        self.accessKey = accessKey
        self.secretKey = secretKey
        self.sn = serialnumber
        self.token = ""
        self.device = None
        self.session = requests.Session()

    def generate_header(self):
        nonce = os.urandom(3).hex()
        timestamp = str(int(time.time() * 1000))
        signClr = "&".join(["sn=" + self.sn, "accessKey=" + self.accessKey, "nonce=" + nonce, "timestamp=" + timestamp])
        sign = hmac.HMAC(self.secretKey.encode(), signClr.encode(), hashlib.sha256).digest().hex()
        print(f"signClr={signClr}")
        print(f"sign={sign}")
        return {
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": sign
        }

    def detect_device(self):
        self.device = {
            "product": "PowerOcean",
            "vendor": "Ecoflow",
            "serial": self.sn,
            "version": "5.1.8",
            "build": "13",
            "name": "PowerOcean",
            "features": "Photovoltaik",
        }

        return self.device

    def get_json_response(self, request):
        if request.status_code != 200:
            raise Exception(
                f"Got HTTP status code {request.status_code}: {request.text}"
            )

        try:
            response = json.loads(request.text)
            response_message = response["message"]
        except KeyError as key:
            raise Exception(f"Failed to extract key {key} from {response}")
        except Exception as error:
            raise Exception(f"Failed to parse response: {request.text} Error: {error}")

        if response_message.lower() != "success":
            raise Exception(f"{response_message}")

        return response

    # Fetch the data from the PowerOcean device, which then constitues the Sensors
    def fetch_data(self):
        url = f"https://api-e.ecoflow.com/iot-open/sign/device/quota/all?sn={self.sn}"

        try:
            header = self.generate_header();
            headers = {
                "content-type": "application/json;charset=utf-8",
                "accessKey": self.accessKey,
                "nonce": header["nonce"],
                "timestamp": header["timestamp"],
                "sign": header["sign"]
            }
            data = {
                "sn": self.sn
            }

            request = requests.get(url, headers=headers, json=data, timeout=30)
            response = self.get_json_response(request)

            _LOGGER.debug(f"{response}")

            # Proceed to parsing
            return self.__parse_data(response)

        except ConnectionError:
            error = f"ConnectionError in fetch_data: Unable to connect to {url}. Device might be offline."
            _LOGGER.warning(error + ISSUE_URL_ERROR_MESSAGE)
            raise IntegrationError(error)
            return None

        except RequestException as e:
            error = f"RequestException in fetch_data: Error while fetching data from {url}: {e}"
            _LOGGER.warning(error + ISSUE_URL_ERROR_MESSAGE)
            raise IntegrationError(error)
            return None

    def __parse_data(self, response):
        # Implement the logic to parse the response from the PowerOcean device

        data = {}
        for key, value in response["data"].items():
            if key == "quota":
                continue
            unique_id = f"{self.sn}_{key}"
            unit_tmp = ""
            description_tmp = {key}
            if key == "sysLoadPwr":
                unit_tmp = "W"
                description_tmp = "Hausnetz"
            if key == "sysGridPwr":
                unit_tmp = "W"
                description_tmp = "Stromnetz"
            if key == "mpptPwr":
                unit_tmp = "W"
                description_tmp = "Solarertrag"
            if key == "bpPwr":
                unit_tmp = "W"
                description_tmp = "Batterieleistung"
            if key == "bpSoc":
                unit_tmp = "%"
                description_tmp = "Ladezustand der Batterie"

            if "Energy" in key:
                unit_tmp = "Wh"
            if "Generation" in key:
                unit_tmp = "kWh"
            
            if key == "ems_change_report.bpTotalChgEnergy":
                unit_tmp = "Wh"
                description_tmp = "Batterie Laden Total"
            if key == "ems_change_report.bpTotalDsgEnergy":
                unit_tmp = "Wh"
                description_tmp = "Batterie Entladen Total"

            data[unique_id] = PowerOceanEndPoint(
                internal_unique_id=unique_id,
                serial=self.sn,
                name=f"{self.sn}_{key}",
                friendly_name=key,
                value=value,
                unit=unit_tmp,
                description=description_tmp,
            )

        return data


class AuthenticationFailed(Exception):
    """Exception to indicate authentication failure."""
