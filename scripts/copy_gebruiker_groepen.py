from ldap3 import Server, Connection, ALL, MODIFY_ADD, MODIFY_DELETE
import os
import sys

required_env = ["LDAP_HOST", "LDAP_USER", "LDAP_PASS", "vangebruiker", "naargebruiker", "sync"]
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
sync = os.environ["sync"].lower() == "true"

def get_user_entry(username):
    conn.search(base_dn, f"(sAMAccountName={username})", attributes=["distinguishedName", "memberOf"])
    if not conn.entries:
        print(f"[ERROR] Gebruiker '{username}' niet gevonden.")
        sys.exit(1)
    return conn.entries[0]

van_entry = get_user_entry(van_user)
naar_entry = get_user_entry(naar_user)

van_dn = van_entry.distinguishedName.value
naar_dn = naar_entry.distinguishedName.value

van_groups = set(van_entry.memberOf) if "memberOf" in van_entry else set()
naar_groups = set(naar_entry.memberOf) if "memberOf" in naar_entry else set()

to_add = van_groups - naar_groups
to_remove = naar_groups - van_groups if sync else set()

added, removed, failed_add, failed_remove = [], [], [], []

for group_dn in to_add:
    if conn.modify(group_dn, {'member': [(MODIFY_ADD, [naar_dn])]}):
        added.append(group_dn)
    else:
        failed_add.append((group_dn, conn.result['message']))

for group_dn in to_remove:
    if conn.modify(group_dn, {'member': [(MODIFY_DELETE, [naar_dn])]}):
        removed.append(group_dn)
    else:
        failed_remove.append((group_dn, conn.result['message']))

print("\n[RESULTAAT]")
if added:
    print("[INFO] Toegevoegd:")
    for g in added:
        print(" -", g)
if removed:
    print("[INFO] Verwijderd:")
    for g in removed:
        print(" -", g)
if failed_add:
    print("[ERROR] Mislukte toevoegingen:")
    for g, msg in failed_add:
        print(f" - {g}: {msg}")
if failed_remove:
    print("[ERROR] Mislukte verwijderingen:")
    for g, msg in failed_remove:
        print(f" - {g}: {msg}")
