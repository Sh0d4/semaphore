from paramiko import Transport, RSAKey

# Forçar algoritmos antigos
Transport._preferred_kex = (
    "diffie-hellman-group1-sha1",
    "diffie-hellman-group14-sha1",
)
Transport._preferred_keys = ("ssh-rsa",)

import os
from netmiko import ConnectHandler
from datetime import datetime

# Inventário embutido
switches = {
    "SAOTS012": {"ansible_host": "10.110.0.112"},
}

# Credenciais vindas do Semaphore (secrets)
username = "saoevcar"
password = "3v4ndr0Abc!@#$"

# Lista de comandos
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
    print(f"Conectando ao switch {name} ({ip})...")

    conn = ConnectHandler(
        device_type="cisco_ios",
        ip=ip,
        username=username,
        password=password,
        ssh_config_file="~/.ssh/config"
    )
    conn.enable()

    # Executar comandos e registrar saída
    results = {}
    for cmd in commands:
        try:
            result = conn.send_config_set([cmd])
            results[cmd] = "OK"
        except Exception as e:
            results[cmd] = str(e)

    conn.save_config()
    conn.disconnect()

    # Consolidar resultados em arquivo
    filename = f"/srv/semaphore-backups/{ip}-alteracoes.txt"
    with open(filename, "w") as f:
        f.write(f"Host: {name}\n")
        f.write(f"Time: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}\n\n")
        f.write("--- Resultados das alterações ---\n")
        f.write(f"*Kron occurrence: {results.get(commands[0], 'OK')}\n")
        f.write(f"*Kron policy: {results.get(commands[1], 'OK')}\n")
        f.write(f"*Logging 10.10.21.81: {results.get(commands[2], 'OK')}\n")
        f.write(f"*Archive: {results.get(commands[3], 'OK')}\n")
        f.write(f"*FTP user: {results.get(commands[4], 'OK')}\n")
        f.write(f"*FTP pass: {results.get(commands[5], 'OK')}\n")
        f.write(f"*Logging 10.110.10.44: {results.get(commands[6], 'OK')}\n")

    print(f"Arquivo gerado: {filename}")
