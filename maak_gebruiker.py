from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import os
import sys

# Vereiste LDAP-omgevingvariabelen
required_env = [
    "LDAP_HOST", "LDAP_USER", "LDAP_PASS",
    "cn", "givenName", "sn", "name",
    "userPrincipalName", "sAMAccountName"
]

missing = [var for var in required_env if not os.getenv(var)]
if missing:
    print(f"[ERROR] Ontbrekende omgevingsvariabelen: {', '.join(missing)}")
    sys.exit(1)

# LDAP server connectie
print("[INFO] Verbinden met domain controller...")
server = Server(os.environ["LDAP_HOST"], get_info=ALL)
conn = Connection(server, user=os.environ["LDAP_USER"], password=os.environ["LDAP_PASS"], auto_bind=True)
print(f"[INFO] Verbonden met {server.host}.")

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

# Optionele attributen alleen toevoegen als ze bestaan en niet leeg zijn
optional_attrs = ['initials', 'mail', 'telephoneNumber']
for attr in optional_attrs:
    val = os.getenv(attr)
    if val:
        attributes[attr] = val

# Toevoegen gebruiker
result = conn.add(dn, ['top', 'person', 'organizationalPerson', 'user'], attributes)

if result:
    print("[SUCCESS] Gebruiker succesvol toegevoegd.")
else:
    print(f"[ERROR] Fout bij toevoegen gebruiker: {conn.result}")
    sys.exit(1)


print(f"[EINDE] Gebruiker '{os.environ['cn']}' is volledig verwerkt.")
