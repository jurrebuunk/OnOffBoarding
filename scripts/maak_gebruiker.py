from ldap3 import Server, Connection, ALL
import paramiko
import os
import sys
from colorama import init, Fore, Style

init(autoreset=True)

def print_info(msg):
    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {msg}")

def print_error(msg):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

def print_success(msg):
    print(f"{Fore.CYAN}[SUCCESS]{Style.RESET_ALL} {msg}")

def print_debug(msg):
    print(f"{Fore.YELLOW}[DEBUG]{Style.RESET_ALL} {msg}")

required_env = [
    "LDAP_HOST", "LDAP_USER", "LDAP_PASS",
    "cn", "givenName", "sn", "name",
    "userPrincipalName", "sAMAccountName",
    "userPassword"
]

missing = [var for var in required_env if not os.getenv(var)]
if missing:
    print_error(f"Ontbrekende omgevingsvariabelen: {', '.join(missing)}")
    sys.exit(1)

# LDAP connectie
print_info("Verbinden met domain controller via LDAP...")
server = Server(os.environ["LDAP_HOST"], get_info=ALL)
conn = Connection(server, user=os.environ["LDAP_USER"], password=os.environ["LDAP_PASS"], auto_bind=True)
print_info(f"Verbonden met {server.host} via LDAP.")

dn = f"CN={os.environ['cn']},OU=Domain-Users,DC=buunk,DC=org"
print_info(f"Aanmaken van gebruiker: {os.environ['cn']}")
print_debug(f"DN: {dn}")

attributes = {
    'cn': os.environ['cn'],
    'givenName': os.environ['givenName'],
    'sn': os.environ['sn'],
    'name': os.environ['name'],
    'userPrincipalName': os.environ['userPrincipalName'],
    'sAMAccountName': os.environ['sAMAccountName'],
    'userAccountControl': 544
}

for attr in ['initials', 'mail', 'telephoneNumber']:
    val = os.getenv(attr)
    if val:
        attributes[attr] = val

result = conn.add(dn, ['top', 'person', 'organizationalPerson', 'user'], attributes)

if result:
    print_success("Gebruiker succesvol toegevoegd via LDAP.")
else:
    print_error(f"Fout bij toevoegen gebruiker: {conn.result}")
    sys.exit(1)

# SSH: wachtwoord instellen en gebruiker activeren
print_info("Verwerken van wachtwoord en activatie via SSH...")

ssh_host = os.environ["LDAP_HOST"]
ssh_user = os.environ["LDAP_USER"]
ssh_pass = os.environ["LDAP_PASS"]
target_user = os.environ["sAMAccountName"]
new_password = os.environ["userPassword"]

ps_command = f'''
powershell -Command "
Set-ADAccountPassword -Identity '{target_user}' -Reset -NewPassword (ConvertTo-SecureString '{new_password}' -AsPlainText -Force);
Enable-ADAccount -Identity '{target_user}';
Set-ADUser -Identity '{target_user}' -ChangePasswordAtLogon $true"
'''

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, username=ssh_user, password=ssh_pass)

    stdin, stdout, stderr = ssh.exec_command(ps_command)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()

    if out:
        print_debug(f"[SSH OUTPUT] {out}")
    if err:
        print_error(f"[SSH ERROR] {err}")

    ssh.close()
    print_success(f"Wachtwoord ingesteld en gebruiker '{target_user}' geactiveerd.")
except Exception as e:
    print_error(f"SSH-fout: {str(e)}")
    sys.exit(1)

print_info(f"EINDE: Gebruiker '{os.environ['cn']}' is volledig verwerkt.")
