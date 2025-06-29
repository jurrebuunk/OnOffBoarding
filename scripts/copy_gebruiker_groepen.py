from ldap3 import Server, Connection, ALL, MODIFY_ADD
import os
import sys

required_env = ["LDAP_HOST", "LDAP_USER", "LDAP_PASS", "vangebruiker", "naargebruiker"]
missing = [var for var in required_env if not os.getenv(var)]
if missing:
    print(f"[ERROR] Ontbrekende omgevingsvariabelen: {', '.join(missing)}")
    sys.exit(1)

print("[INFO] Verbinden met domain controller...")
server = Server(os.environ["LDAP_HOST"], get_info=ALL)
conn = Connection(server, user=os.environ["LDAP_USER"], password=os.environ["LDAP_PASS"], auto_bind=True)
print(f"[INFO] Verbonden met {server.host}.")

base_dn = "DC=buunk,DC=org"
van_user = os.environ["vangebruiker"]
naar_user = os.environ["naargebruiker"]

# Zoek DN's van beide gebruikers
def get_user_dn(username):
    conn.search(base_dn, f"(sAMAccountName={username})", attributes=["distinguishedName", "memberOf"])
    if not conn.entries:
        print(f"[ERROR] Gebruiker '{username}' niet gevonden.")
        sys.exit(1)
    return conn.entries[0]

van_entry = get_user_dn(van_user)
naar_entry = get_user_dn(naar_user)

van_dn = van_entry.distinguishedName.value
naar_dn = naar_entry.distinguishedName.value

groepen = van_entry.memberOf if "memberOf" in van_entry else []
success_groups = []
failed_groups = []

for group_dn in groepen:
    if conn.modify(group_dn, {'member': [(MODIFY_ADD, [naar_dn])]}):
        success_groups.append(group_dn)
    else:
        failed_groups.append((group_dn, conn.result['message']))

print("\n[RESULTAAT]")
if success_groups:
    print("[INFO] Succesvol gekopieerde groepen:")
    for g in success_groups:
        print(" -", g)
if failed_groups:
    print("[ERROR] Mislukte toevoegingen:")
    for g, msg in failed_groups:
        print(f" - {g}: {msg}")
