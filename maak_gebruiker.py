from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import os
import sys

# Vereiste LDAP-omgevingvariabelen
required_env = [
    "LDAP_HOST", "LDAP_USER", "LDAP_PASS",
    "cn", "givenName", "sn", "initials", "name",
    "userPrincipalName", "sAMAccountName", "mail", "telephoneNumber"
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

# Toevoegen gebruiker
result = conn.add(dn, ['top', 'person', 'organizationalPerson', 'user'], {
    'cn': os.environ['cn'],
    'givenName': os.environ['givenName'],
    'sn': os.environ['sn'],
    'initials': os.environ['initials'],
    'name': os.environ['name'],
    'userPrincipalName': os.environ['userPrincipalName'],
    'sAMAccountName': os.environ['sAMAccountName'],
    'mail': os.environ['mail'],
    'telephoneNumber': os.environ['telephoneNumber'],
    'userAccountControl': 544
})

if result:
    print("[SUCCESS] Gebruiker succesvol toegevoegd.")
else:
    print(f"[ERROR] Fout bij toevoegen gebruiker: {conn.result}")
    sys.exit(1)

print("[INFO] Proberen account te ontgrendelen...")
try:
    conn.extend.microsoft.unlock_account(dn)
    print("[SUCCESS] Account ontgrendeld.")
except Exception as e:
    print(f"[ERROR] Ontgrendelen mislukt: {e}")
    sys.exit(1)

print("[INFO] UserAccountControl opnieuw instellen op 512...")
mod_result = conn.modify(dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]})
if mod_result:
    print("[SUCCESS] userAccountControl ingesteld.")
else:
    print(f"[ERROR] userAccountControl wijzigen mislukt: {conn.result}")
    sys.exit(1)

print(f"[EINDE] Gebruiker '{os.environ['cn']}' is volledig verwerkt.")
