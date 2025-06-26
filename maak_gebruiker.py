from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import sys

# LDAP verbinding
print("[INFO] Verbinden met domain controller...")
server = Server('ldap://192.168.2.14', get_info=ALL)
conn = Connection(server, user='BUUNK\\jurre', password='F+NywdK7f8;eC~tD', auto_bind=True)
print(f"[INFO] Verbonden met {server.host}.")

gebruikersnaam = "testdihhh"
voornaam = "test"
achternaam = "dihhh"

dn = f"CN={gebruikersnaam},OU=Domain-Users,DC=buunk,DC=org"

print(f"[INFO] Aanmaken van gebruiker: {gebruikersnaam}")
print(f"[DEBUG] DN: {dn}")
print(f"[DEBUG] Voornaam: {voornaam}, Achternaam: {achternaam}")
print(f"[DEBUG] UserPrincipalName: {gebruikersnaam}@buunk.org")

# Gebruiker toevoegen zonder wachtwoord
result = conn.add(dn, ['top', 'person', 'organizationalPerson', 'user'], {
    'cn': gebruikersnaam,
    'givenName': voornaam,
    'sn': achternaam,
    'displayName': f"{voornaam} {achternaam}",
    'userPrincipalName': f"{gebruikersnaam}@buunk.org",
    'sAMAccountName': gebruikersnaam,
    'userAccountControl': 544  # Account disabled + PASSWD_NOTREQD
})

if result:
    print("[SUCCESS] Gebruiker succesvol toegevoegd.")
else:
    print(f"[ERROR] Fout bij toevoegen gebruiker: {conn.result}")
    sys.exit(1)

# Account ontgrendelen
print("[INFO] Proberen account te ontgrendelen...")
try:
    conn.extend.microsoft.unlock_account(dn)
    print("[SUCCESS] Account ontgrendeld.")
except Exception as e:
    print(f"[ERROR] Ontgrendelen mislukt: {e}")
    sys.exit(1)

# UserAccountControl opnieuw instellen op 512
print("[INFO] UserAccountControl opnieuw instellen op 512...")
mod_result = conn.modify(dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]})
if mod_result:
    print("[SUCCESS] userAccountControl ingesteld.")
else:
    print(f"[ERROR] userAccountControl wijzigen mislukt: {conn.result}")
    sys.exit(1)

print(f"[EINDE] Gebruiker '{gebruikersnaam}' is volledig verwerkt.")
