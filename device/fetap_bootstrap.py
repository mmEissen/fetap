from dataclasses import dataclass
from http.server import HTTPServer, BaseHTTPRequestHandler
from os import path
import subprocess
import threading

from typing import Optional
import urllib.parse
import urllib.error
import urllib.request


COMPOSE_FILE_URL = "https://fetap.net/fetap-v1/docker-compose.yml"
FETAP_DIR = path.dirname(__file__)
COMPOSE_FILE_NAME = path.join(FETAP_DIR, "docker-compose.yml")


def main() -> None:
    ensure_internet()


def ensure_internet() -> None:
    nmcli.radio_wifi_on()
    while not is_connected():
        nmcli.device_wifi_hotspot()
        bssid, password = get_wifi_credentials()
        nmcli.device_wifi_connect(bssid, password)


def is_connected() -> bool:
    connections = nmcli.con_show()
    return any(
        c.device == nmcli.IFNAME and c.name != nmcli.HOTSPOT_CONN_NAME
        for c in connections
    )


_server_done = threading.Event()
_bssid = ""
_password = ""


def get_wifi_credentials() -> tuple[str, str]:
    _server_done.clear()
    server = HTTPServer(("0.0.0.0", 80), WifiConfigRequestHandler)
    server_thread = threading.Thread(
        target=server.serve_forever, name="wifi-config-server", daemon=True
    )
    server_thread.start()
    _server_done.wait()
    server.shutdown()
    server_thread.join()
    return _bssid, _password


class WifiConfigRequestHandler(BaseHTTPRequestHandler):
    _FORM_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>FETAP WiFi Config</title>
    </head>
    <body>
        <h1>Fetap WiFi Config</h1>
        <p>Please input the credentials for your WiFi below</p>
        <form action="/">
            <label for="bssid">WiFi Name:</label><br>
            <select name="bssid" id="bssid">
                {options}
            </select><br>

            <label for="pass">WiFi Password:</label><br>
            <input type="text" id="pass" name="pass"><br><br>
            <input type="submit" value="Submit">
        </form> 
    </body>
</html>
"""
    _OPTION_TEMPLATE = (
        '<option style="font-family:monospace;" value="{bssid}">{description}</option>'
    )

    _SUCCESS_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>FETAP WiFi Config</title>
    </head>
    <body>
        <h1>Success!</h1>
        <p>Your Fetap is now trying to connect to the WiFi</p>
    </body>
</html>
"""

    _FAVICON = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x02'IDAT8O\xa5\x92Ok\x13\x01\x10\xc5\xdfdw\x93m6\t\xfd\x93`LH\xa1E\x10\xa1&\xa4z\x0b\x14\xa3iQQD\xe8\xc5/\xa0\xf4\xa0E\xd0\x9b\"\xa2\xe0AA\xaa\x87\xe2\x17\xd0\x83\x1e\x14\xa5Hi\x12\x0f\xd6\x9b\x82)\nJ[M \xb4%i\x1a\xbaI\x9a\xcdn2\xb2k#\xc5zI\x9d\xe3\x0c\xef\xf7\x1e3C\xf8\xcf\xa2\xbf\xf5i\x1c\x13\x11\xdc\xf23\x1a} \x9bl\xcd\xb9U'\xd8\xd7\x91\xefZ\x8d\xe3\x9d\xb1Sc\x01fC\xd1\x80\xd4\xa4\x8b`>\xcd\x840\x18\x8e\x7f\x06#h\xc4\xc8\x80hF\x90\xe8\xc9H\xf6\xe3\n%\x03G\xc6\x88\xf99\xc0\x1eSDD\xd8\xd7\xedA\xb5\xaeA\xdd\xaa[\x1cw\x97\x0cEv`\xad\xbc\tf\xdef\x93\xcaD\xe3\x94\xdc\x1f\xcd\x12\xd0\xdfv\x14\x05\x01\xc1\xden\xd4\x1a:J\x95\xaa\xd5\xeeu)p\xda%\xe47\xca0\x8c\xe6\xcepYJ\x05\xa2\r0\xa4\xb6S\x8fK\xc1\xae\xc5lKL\xef\x8dJ\xf5O2\x10tJ\x07\xa2\xf7\x98qM\x91\x1d\xa2\xd7\xed\x02D\x11\xbe[WQ\xff\xb4\x001\xe0\x87I3\xf2\xab\x90\x87\x0f\xa3p\xfb!`\x18(\xa8\x15\xd4\xea\x9aA\xc0\x03\xcblah$$\x93\xf4\xd5F\xe4r\x1e\x8f\xc1u*\x0e\xf5\xe5[(\xf1\x98\xe5]M\xcd\xc3}\xfe$*3)\xd4\xd2\x1f\xcc=\xa8\xe5\x966t\xf4\xcb\xfb\x9c\x05X\x8e$\x1e1\xe32I\x12\x9c'b\x90\xfa\x83P_\xcd\xc2}6a\x01\xd4\xd7sp\x9f\x1b\x83\x9e\xcb\xa3\x96\x9c\x07\xeb:\x88\xf0x\xf0\xf3\xdc\x15\xfa>\x9c8d3\x90!@\xf4\xde\x9c\x84g\xfc\x0cXk\xa0x\x7f\x1a\xbe\x1b\x93\x16\xa0pw\n\xde\xeb\x13 \x87\x1d\x9b/\xde\xa0xg\xcal\xeb\x82\x88\x08-\x85G\x9f\x02|\xc1:\xa1$B:0\x80f\xb1\x84fa\x1d\xd2@\xc8\xecB\xff\x91\x83\xe0\xeb\x83\xe0\xed\x81\xbe\xf8\x13\xac\xb7\x7f\x89\x9e\xd1R8Q\x01\xa0\xec\xf1\xa3\xab\xb4\x1cN\xac0\xe0\xdf#`\x8d\x16#\xa3\x97\x88y\xda\xca\xdaY1\x13M\xfc\xbeB8~\xd0&8z;\xd1\xb7\x9aZi0\x93\xfe\xd6\xa9\xeb.\x8f_\xb9d\xc8\x82{Q/t\x00\x00\x00\x00IEND\xaeB`\x82"

    def do_GET(self) -> None:
        try:
            path, query_string = self.path.split("?", maxsplit=1)
        except ValueError:
            path = self.path
            query_string = ""

        if path == "/favicon.ico":
            self._get_favicon()
        elif path == "/":
            if query_string == "":
                self._get_form()
            else:
                self._submit(query_string)
        else:
            self._redirect()

    def _redirect(self) -> None:
        self.send_response(301)
        self.send_header("Location", "/")
        self.end_headers()

    def _get_success(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(self._SUCCESS_HTML.encode())

    def _submit(self, query_string: str) -> None:
        global _bssid
        global _password
        form_data = urllib.parse.parse_qs(query_string)
        try:
            _bssid = form_data["bssid"][0]
            _password = form_data["pass"][0]
        except (KeyError, IndexError):
            self._redirect()
            return
        _server_done.set()
        self._get_success()

    def _get_form(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html;charset=UTF-8")
        self.end_headers()

        wifis = nmcli.device_wifi_list()

        def bars(strength: int) -> str:
            max_bars = 4
            bars = min(round(strength / (100 / max_bars)), max_bars)
            return ("+" * bars).ljust(max_bars, "-")

        content = self._FORM_HTML.format(
            options="\n".join(
                self._OPTION_TEMPLATE.format(
                    bssid=wifi.bssid,
                    description=f"|{bars(wifi.signal)}| {wifi.ssid} ({wifi.channel})",
                )
                for wifi in wifis
                if wifi.ssid
            )
        )

        self.wfile.write(content.encode())

    def _get_favicon(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "image/png")
        self.end_headers()

        self.wfile.write(self._FAVICON)


def get_latest_compose_file() -> None:
    urllib.request.urlopen


class docker_compose:


    @classmethod
    def _docker_compose(cls, *args: str) -> str:
        return cls._run(
            ["docker", "compose", "-f", path.join(FETAP_DIR, "docker-compose.yml")]
            + list(args)
        )

    @staticmethod
    def _run(command: list[str], env: Optional[dict[str, str]] = None) -> str:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            check=True,
            text=True,
            env=env,
        )
        return result.stdout


class nmcli:
    HOTSPOT_CONN_NAME = "fetap-hotpot"
    IFNAME = "wlan0"

    @classmethod
    def radio_wifi_on(cls) -> None:
        cls._nmcli("radio", "wifi", "on")

    @dataclass
    class Connection:
        name: str
        uuid: str
        _type: str
        device: str

    @classmethod
    def con_show(cls) -> list[Connection]:
        output = cls._nmcli("con", "show")
        return [
            cls.Connection(name, uuid, _type, device)
            for name, uuid, _type, device in cls._split_output(output)
        ]

    @classmethod
    def con_up(cls, uuid: str) -> None:
        cls._nmcli("con", "up", uuid)

    @classmethod
    def con_delete(cls, uuid: str) -> None:
        cls._nmcli("con", "delete", uuid)

    @classmethod
    def device_wifi_connect(cls, bssid: str, password: str) -> None:
        cls._nmcli(
            "device",
            "wifi",
            "connect",
            bssid,
            "password",
            password,
            "ifname",
            cls.IFNAME,
        )

    @classmethod
    def device_wifi_hotspot(cls) -> None:
        cls._nmcli(
            "device",
            "wifi",
            "hotspot",
            "ifname",
            cls.IFNAME,
            "con-name",
            cls.HOTSPOT_CONN_NAME,
            "ssid",
            "fetap-config",
            "password",
            "password",
        )

    @dataclass
    class Wifi:
        bssid: str
        ssid: str
        channel: int
        signal: int

    @classmethod
    def device_wifi_list(cls) -> list[Wifi]:
        output = cls._nmcli(
            "device",
            "wifi",
            "list",
            "ifname",
            cls.IFNAME,
        )
        return [
            cls.Wifi(bssid, ssid, int(channel), int(signal))
            for _, bssid, ssid, _, channel, _, signal, _, _ in cls._split_output(output)
        ]

    @staticmethod
    def _split_output(output: str) -> list[tuple[str]]:
        def split_line(line: str) -> tuple[str]:
            return tuple(
                part.replace("___colon___", ":")
                for part in line.replace("\\:", "___colon___").split(":")
            )

        return [split_line(line) for line in output.strip().split("\n")]

    @classmethod
    def _nmcli(cls, *args: str) -> str:
        return cls._run(["nmcli", "-c", "no", "-t"] + list(args))

    @staticmethod
    def _run(command: list[str], env: Optional[dict[str, str]] = None) -> str:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            check=True,
            text=True,
            env=env,
        )
        return result.stdout


if __name__ == "__main__":
    main()
