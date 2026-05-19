import yaml
from netmiko import ConnectHandler
from datetime import datetime

# Carregar inventário Ansible
with open("hosts.yml") as f:
    inventory = yaml.safe_load(f)

switches = inventory["all"]["hosts"]

commands = [
    "no kron occurrence DAILY-BACKUP at 11:15 recurring",
    "no kron policy-list DAILY-BACKUP",
    "no logging host 10.10.21.81",
    "no archive",
    "no ip ftp username swbkftp",
    "no ip ftp password Flex.123",
    "no logging host 10.110.10.44 transport udp port 11001",
]

for name, device in switches.items():
    ip = device["ansible_host"]
    user = device["ansible_user"]
    passwd = device["ansible_password"]
    enable = device.get("ansible_become_password")

    print(f"Conectando ao switch {name} ({ip})...")
    conn = ConnectHandler(
        device_type="cisco_ios",
        ip=ip,
        username=user,
        password=passwd,
        secret=enable,
    )
    conn.enable()

    output = ""
    for cmd in commands:
        result = conn.send_config_set([cmd])
        output += f"\n--- {cmd} ---\n{result}\n"

    save_output = conn.save_config()
    run_cfg = conn.send_command("show running-config")
    intf_status = conn.send_command("show interfaces status")
    conn.disconnect()

    filename = f"/srv/semaphore-backups/{ip}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    with open(filename, "w") as f:
        f.write(f"Host: {name}\n")
        f.write(f"Time: {datetime.now().isoformat()}\n\n")
        f.write("--- Resultados das alterações ---\n")
        f.write(output)
        f.write("\n--- Save Config ---\n")
        f.write(save_output)
        f.write("\n--- Running Config ---\n")
        f.write(run_cfg)
        f.write("\n--- Interface Status ---\n")
        f.write(intf_status)

    print(f"Arquivo gerado: {filename}")
