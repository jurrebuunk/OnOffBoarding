from ldap3 import Server, Connection, ALL, SUBTREE
import os
import sys
from colorama import init, Fore, Style

init(autoreset=True)

def print_info(msg):
    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {msg}")

def print_error(msg):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

required_env = ["LDAP_HOST", "LDAP_USER", "LDAP_PASS"]
missing = [var for var in required_env if not os.getenv(var)]
if missing:
    print_error(f"Ontbrekende omgevingsvariabelen: {', '.join(missing)}")
    sys.exit(1)

print_info("Verbinden met domain controller...")
server = Server(os.environ["LDAP_HOST"], get_info=ALL)
conn = Connection(server, user=os.environ["LDAP_USER"], password=os.environ["LDAP_PASS"], auto_bind=True)
print_info(f"Verbonden met {server.host}.")

base_dn = "DC=buunk,DC=org"
search_user = os.getenv("search")
if not search_user:
    print_error("Omgevingsvariabele 'search' is niet gezet.")
    sys.exit(1)

print_info(f"Gezocht wordt op: {search_user}")

search_filter = (
    "(&"
    "(objectClass=user)"
    "(|"
    f"(sAMAccountName={search_user})"
    f"(cn={search_user})"
    f"(givenName={search_user})"
    f"(sn={search_user})"
    ")"
    ")"
)

conn.search(
    base_dn,
    search_filter,
    search_scope=SUBTREE,
    attributes=['cn', 'sAMAccountName', 'mail', 'memberOf', 'userAccountControl']
)

print_info("Resultaten:")
for entry in conn.entries:
    cn = entry.cn.value
    sam = entry.sAMAccountName.value
    mail = entry.mail.value if 'mail' in entry else "n/a"
    uac = int(entry.userAccountControl.value)
    enabled = not (uac & 0x2)
    status = "Ingeschakeld" if enabled else "Uitgeschakeld"

    print(f"CN: {cn}, SAM: {sam}, Mail: {mail}, Status: {status}")
    if 'memberOf' in entry:
        groepen = [g.split(',')[0].replace("CN=", "") for g in entry.memberOf]
        print("---------------")
        for groep in groepen:
            print(groep)
        print("---------------")
    else:
        print("  Groepen: geen")

print_info(f"Totaal gevonden gebruikers: {len(conn.entries)}")
