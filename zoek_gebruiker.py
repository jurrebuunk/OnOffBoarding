from ldap3 import Server, Connection, ALL, SUBTREE
import os
import sys

# Vereiste LDAP-omgevingvariabelen
required_env = ["LDAP_HOST", "LDAP_USER", "LDAP_PASS"]

missing = [var for var in required_env if not os.getenv(var)]
if missing:
    print(f"[ERROR] Ontbrekende omgevingsvariabelen: {', '.join(missing)}")
    sys.exit(1)

print("[INFO] Verbinden met domain controller...")
server = Server(os.environ["LDAP_HOST"], get_info=ALL)
conn = Connection(server, user=os.environ["LDAP_USER"], password=os.environ["LDAP_PASS"], auto_bind=True)
print(f"[INFO] Verbonden met {server.host}.")

base_dn = "DC=buunk,DC=org"
search_user = os.getenv("search")
if not search_user:
    print("[ERROR] Omgevingsvariabele 'search' is niet gezet.")
    sys.exit(1)

print(f"[INFO] Gezocht wordt op: {search_user}")

# Filter zoekt op sAMAccountName, cn (full name), givenName (voornaam), sn (achternaam)
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

conn.search(base_dn, search_filter, search_scope=SUBTREE, attributes=['cn', 'sAMAccountName', 'mail', 'memberOf'])

print("[INFO] Resultaten:")
for entry in conn.entries:
    cn = entry.cn.value
    sam = entry.sAMAccountName.value
    mail = entry.mail.value if 'mail' in entry else "n/a"
    print(f"CN: {cn}, SAM: {sam}, Mail: {mail}")
    if 'memberOf' in entry:
        groepen = [g.split(',')[0].replace("CN=", "") for g in entry.memberOf]
    	print("---------------")
   	for groep in groepen:
            print(groep)
    	print("---------------")
    else:
    	print("  Groepen: geen")


print(f"[INFO] Totaal gevonden gebruikers: {len(conn.entries)}")
