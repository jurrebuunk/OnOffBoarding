from ldap3 import Server, Connection, ALL, MODIFY_ADD
import os
import sys
from colorama import init, Fore, Style

init(autoreset=True)

def print_info(msg):
    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {msg}")

def print_error(msg):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

required_env = ["LDAP_HOST", "LDAP_USER", "LDAP_PASS", "username", "group"]
missing = [var for var in required_env if not os.getenv(var)]
if missing:
    print_error(f"Ontbrekende omgevingsvariabelen: {', '.join(missing)}")
    sys.exit(1)

print_info("Verbinden met domain controller...")
server = Server(os.environ["LDAP_HOST"], get_info=ALL)
conn = Connection(server, user=os.environ["LDAP_USER"], password=os.environ["LDAP_PASS"], auto_bind=True)
print_info(f"Verbonden met {server.host}.")

username = os.environ["username"]
group_names = [g.strip() for g in os.environ["group"].split(',')]
base_dn = "DC=buunk,DC=org"

conn.search(
    base_dn,
    f"(sAMAccountName={username})",
    attributes=['distinguishedName']
)

if not conn.entries:
    print_error(f"Gebruiker '{username}' niet gevonden.")
    sys.exit(1)

user_dn = conn.entries[0].distinguishedName.value
print_info(f"Gebruiker gevonden: {user_dn}")

success_groups = []
failed_groups = []

for group_name in group_names:
    group_dn = f"CN={group_name},OU=Security-groups,{base_dn}"
    if conn.modify(group_dn, {'member': [(MODIFY_ADD, [user_dn])]}):
        success_groups.append(group_name)
    else:
        failed_groups.append((group_name, conn.result['message']))

print("\n[RESULTAAT]")
if success_groups:
    print_info(f"Succesvol toegevoegd aan: {', '.join(success_groups)}")
if failed_groups:
    print_error("Mislukt bij:")
    for g, msg in failed_groups:
        print(f"  - {g}: {msg}")
