from flask import Flask, request
import subprocess

app = Flask(__name__)


@app.route("/")
def home():
    with open("index.html", encoding="utf-8") as f:
        return f.read()


@app.route("/run")
def run_command():

    cmd = request.args.get("cmd")

    # ==========================================
    # DELETE VLANs
    # مثال:
    # no vlan 5,6,7
    # ==========================================
    if cmd.startswith("no vlan"):

        data = cmd.replace("no vlan", "").strip()

        vlans = data.split(",")

        output = ""

        for v in vlans:

            vlan_id = v.strip()

            result = subprocess.run(
                f'ansible switches -i inventory '
                f'-m cisco.ios.ios_config '
                f'-a \'lines="no vlan {vlan_id}"\'',
                shell=True,
                capture_output=True,
                text=True
            )

            output += result.stdout
            output += result.stderr
            output += "\n"

        return f"<pre>{output}</pre>"


    # ==========================================
    # CREATE VLAN + INTERFACE VLAN
    # مثال:
    # vlan 5:HR,6:IT,7:VOICE
    # ==========================================
    elif cmd.startswith("vlan"):

        data = cmd.replace("vlan", "").strip()

        vlan_list = data.split(",")

        output = ""

        for item in vlan_list:

            vlan_id, vlan_name = item.split(":")

            vlan_id = vlan_id.strip()
            vlan_name = vlan_name.strip()

            # Create VLAN
            result1 = subprocess.run(
                [
                    "ansible",
                    "switches",
                    "-i",
                    "inventory",
                    "-m",
                    "cisco.ios.ios_config",
                    "-a",
                    f'lines="vlan {vlan_id},name {vlan_name}"'
                ],
                capture_output=True,
                text=True
            )

            # Create Interface VLAN
            result2 = subprocess.run(
                [
                    "ansible",
                    "switches",
                    "-i",
                    "inventory",
                    "-m",
                    "cisco.ios.ios_config",
                    "-a",
                    f'parents="interface vlan {vlan_id}" lines="no shutdown"'
                ],
                capture_output=True,
                text=True
            )

            output += result1.stdout + result1.stderr
            output += result2.stdout + result2.stderr

        return f"<pre>{output}</pre>"
# ==========================================
    # RESET / DELETE INTERFACE CONFIG
    # مثال:
    # default interface fa0/1-10
    # ==========================================
    elif cmd.startswith("default interface"):

        port_range = cmd.replace("default interface", "").strip()

        result = subprocess.run(
            [
                "ansible",
                "switches",
                "-i",
                "inventory",
                "-m",
                "cisco.ios.ios_config",
                "-a",
                f'commands="default interface {port_range}"'
            ],
            capture_output=True,
            text=True
        )

        return f"<pre>{result.stdout + result.stderr}</pre>"
# ==========================================
    # WIPE SVI (FULL DELETE EFFECT)
    # مثال:
    # wipe svi 5,6,7
    # ==========================================
    elif cmd.startswith("wipe svi"):

        data = cmd.replace("wipe svi", "").strip()

        vlans = data.split(",")

        output = ""

        for v in vlans:

            vlan_id = v.strip()

            result1 = subprocess.run(
                [
                    "ansible",
                    "switches",
                    "-i",
                    "inventory",
                    "-m",
                    "cisco.ios.ios_config",
                    "-a",
                    f'parents="interface vlan {vlan_id}" lines="shutdown,no ip address"'
                ],
                capture_output=True,
                text=True
            )

            result2 = subprocess.run(
                [
                    "ansible",
                    "switches",
                    "-i",
                    "inventory",
                    "-m",
                    "cisco.ios.ios_config",
                    "-a",
                    f'lines="no vlan {vlan_id}"'
                ],
                capture_output=True,
                text=True
            )

            output += result1.stdout + result1.stderr
            output += result2.stdout + result2.stderr
            output += "\n"

        return f"<pre>{output}</pre>"
    # ==========================================
    # SHUTDOWN PORT RANGE
    # مثال:
    # shutdown fa0/1-10
    # ==========================================
    elif cmd.startswith("shutdown"):

        port_range = cmd.replace("shutdown", "").strip()

        result = subprocess.run(
            [
                "ansible",
                "switches",
                "-i",
                "inventory",
                "-m",
                "cisco.ios.ios_config",
                "-a",
                f'parents="interface range {port_range}" lines="shutdown"'
            ],
            capture_output=True,
            text=True
        )

        return f"<pre>{result.stdout + result.stderr}</pre>"


    # ==========================================
    # OPEN PORT RANGE
    # مثال:
    # no shutdown fa0/1-10
    # ==========================================
    elif cmd.startswith("no shutdown"):

        port_range = cmd.replace("no shutdown", "").strip()

        result = subprocess.run(
            [
                "ansible",
                "switches",
                "-i",
                "inventory",
                "-m",
                "cisco.ios.ios_config",
                "-a",
                f'parents="interface range {port_range}" lines="no shutdown"'
            ],
            capture_output=True,
            text=True
        )

        return f"<pre>{result.stdout + result.stderr}</pre>"
# ==========================================
    # REMOVE PORT SECURITY
    # مثال:
    # no security fa0/1-10
    # ==========================================
    elif cmd.startswith("no security"):

        port_range = cmd.replace("no security", "").strip()

        result = subprocess.run(
            [
                "ansible",
                "switches",
                "-i",
                "inventory",
                "-m",
                "cisco.ios.ios_config",
                "-a",
                (
                    f'parents="interface range {port_range}" '
                    'lines="no switchport port-security,'
                    'no switchport port-security maximum 2,'
                    'no switchport port-security violation restrict,'
                    'no switchport port-security mac-address sticky"'
                )
            ],
            capture_output=True,
            text=True
        )

        return f"<pre>{result.stdout + result.stderr}</pre>"


    # ==========================================
    # APPLY PORT SECURITY
    # مثال:
    # security fa0/1-10
    # ==========================================
    elif cmd.startswith("security"):

        port_range = cmd.replace("security", "").strip()

        result = subprocess.run(
            [
                "ansible",
                "switches",
                "-i",
                "inventory",
                "-m",
                "cisco.ios.ios_config",
                "-a",
                (
                    f'parents="interface range {port_range}" '
                    'lines="switchport mode access,'
                    'switchport port-security,'
                    'switchport port-security maximum 2,'
                    'switchport port-security violation restrict,'
                    'switchport port-security mac-address sticky"'
                )
            ],
            capture_output=True,
            text=True
        )

        return f"<pre>{result.stdout + result.stderr}</pre>"


    # ==========================================
    # SHOW COMMANDS
    # ==========================================
    elif cmd.startswith("show"):

        result = subprocess.run(
            [
                "ansible",
                "switches",
                "-i",
                "inventory",
                "-m",
                "cisco.ios.ios_command",
                "-a",
                f'commands="{cmd}"'
            ],
            capture_output=True,
            text=True
        )

        return f"<pre>{result.stdout + result.stderr}</pre>"


    # ==========================================
    # OTHER CONFIG COMMANDS
    # ==========================================
    else:

        result = subprocess.run(
            [
                "ansible",
                "switches",
                "-i",
                "inventory",
                "-m",
                "cisco.ios.ios_config",
                "-a",
                f'lines="{cmd}"'
            ],
            capture_output=True,
            text=True
        )

        return f"<pre>{result.stdout + result.stderr}</pre>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
