from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import os
import sys
from colorama import init, Fore, Style

init(autoreset=True)

def print_info(msg):
    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {msg}")

def print_error(msg):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

required_env = ["LDAP_HOST", "LDAP_USER", "LDAP_PASS", "username"]
missing = [var for var in required_env if not os.getenv(var)]
if missing:
    print_error(f"Ontbrekende omgevingsvariabelen: {', '.join(missing)}")
    sys.exit(1)

print_info("Verbinden met domain controller...")
server = Server(os.environ["LDAP_HOST"], get_info=ALL)
conn = Connection(server, user=os.environ["LDAP_USER"], password=os.environ["LDAP_PASS"], auto_bind=True)
print_info(f"Verbonden met {server.host}.")

username = os.environ["username"]
base_dn = "DC=buunk,DC=org"
disabled_ou = f"OU=Disabled-Users,{base_dn}"

conn.search(base_dn, f"(sAMAccountName={username})", attributes=["distinguishedName", "userAccountControl"])
if not conn.entries:
    print_error(f"Gebruiker '{username}' niet gevonden.")
    sys.exit(1)

entry = conn.entries[0]
user_dn = entry.distinguishedName.value
current_uac = int(entry.userAccountControl.value)
disabled_uac = current_uac | 0x2  # ACCOUNTDISABLE bit

if conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [disabled_uac])]}):
    print_info(f"Gebruiker '{username}' uitgeschakeld.")
else:
    print_error(f"Uitschakelen mislukt: {conn.result}")
    sys.exit(1)

rdn = user_dn.split(',')[0]
new_dn = f"{rdn},{disabled_ou}"

if conn.modify_dn(user_dn, rdn, new_superior=disabled_ou):
    print_info(f"Gebruiker verplaatst naar: {disabled_ou}")
else:
    print_error(f"Verplaatsen mislukt: {conn.result}")
