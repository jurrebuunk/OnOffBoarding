from ldap3 import Server, Connection, ALL
import paramiko
import os
import sys

# Vereiste LDAP- en SSH-omgevingvariabelen
required_env = [
    "LDAP_HOST", "LDAP_USER", "LDAP_PASS",
    "cn", "givenName", "sn", "name",
    "userPrincipalName", "sAMAccountName",
    "userPassword"  # Toegevoegd voor wachtwoordinstelling via SSH
]

missing = [var for var in required_env if not os.getenv(var)]
if missing:
    print(f"[ERROR] Ontbrekende omgevingsvariabelen: {', '.join(missing)}")
    sys.exit(1)

# LDAP server connectie
print("[INFO] Verbinden met domain controller via LDAP...")
server = Server(os.environ["LDAP_HOST"], get_info=ALL)
conn = Connection(server, user=os.environ["LDAP_USER"], password=os.environ["LDAP_PASS"], auto_bind=True)
print(f"[INFO] Verbonden met {server.host} via LDAP.")

dn = f"CN={os.environ['cn']},OU=Domain-Users,DC=buunk,DC=org"

print(f"[INFO] Aanmaken van gebruiker: {os.environ['cn']}")
print(f"[DEBUG] DN: {dn}")

# Basis attributen
attributes = {
    'cn': os.environ['cn'],
    'givenName': os.environ['givenName'],
    'sn': os.environ['sn'],
    'name': os.environ['name'],
    'userPrincipalName': os.environ['userPrincipalName'],
    'sAMAccountName': os.environ['sAMAccountName'],
    'userAccountControl': 544
}

# Optionele attributen
optional_attrs = ['initials', 'mail', 'telephoneNumber']
for attr in optional_attrs:
    val = os.getenv(attr)
    if val:
        attributes[attr] = val

# Toevoegen gebruiker
result = conn.add(dn, ['top', 'person', 'organizationalPerson', 'user'], attributes)

if result:
    print("[SUCCESS] Gebruiker succesvol toegevoegd via LDAP.")
else:
    print(f"[ERROR] Fout bij toevoegen gebruiker: {conn.result}")
    sys.exit(1)

# SSH: wachtwoord instellen + gebruiker activeren + wachtwoord wijziging afdwingen
print("[INFO] Verwerken van wachtwoord en activatie via SSH...")

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

    out = stdout.read().decode()
    err = stderr.read().decode()

    if out:
        print(f"[SSH OUTPUT] {out.strip()}")
    if err:
        print(f"[SSH ERROR] {err.strip()}")

    ssh.close()
    print(f"[SUCCESS] Wachtwoord ingesteld en gebruiker '{target_user}' geactiveerd.")
except Exception as e:
    print(f"[ERROR] SSH-fout: {str(e)}")
    sys.exit(1)

print(f"[EINDE] Gebruiker '{os.environ['cn']}' is volledig verwerkt.")
