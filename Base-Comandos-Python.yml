import os
from netmiko import ConnectHandler
from datetime import datetime

device = {
    "device_type": "cisco_ios",
    "ip": os.environ.get("SW_IP"),
    "username": os.environ.get("SW_USER"),
    "password": os.environ.get("SW_PASS"),
    "secret": os.environ.get("SW_ENABLE"),
}

net_connect = ConnectHandler(**device)
net_connect.enable()

commands = [
    "no kron occurrence DAILY-BACKUP at 11:15 recurring",
    "no kron policy-list DAILY-BACKUP",
    "no logging host 10.10.21.81",
    "no archive",
    "no ip ftp username swbkftp",
    "no ip ftp password Flex.123",
    "no logging host 10.110.10.44 transport udp port 11001",
]

output = ""
for cmd in commands:
    result = net_connect.send_config_set([cmd])
    output += f"\n--- {cmd} ---\n{result}\n"

net_connect.save_config()
run_cfg = net_connect.send_command("show running-config")
intf_status = net_connect.send_command("show interfaces status")
net_connect.disconnect()

filename = f"/srv/semaphore-backups/{device['ip']}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
with open(filename, "w") as f:
    f.write(f"Host: {device['ip']}\n")
    f.write(f"Time: {datetime.now().isoformat()}\n\n")
    f.write("--- Resultados das alterações ---\n")
    f.write(output)
    f.write("\n--- Running Config ---\n")
    f.write(run_cfg)
    f.write("\n--- Interface Status ---\n")
    f.write(intf_status)
