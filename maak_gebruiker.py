from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, SUBTREE
import random
import string

def genereer_wachtwoord():
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    wachtwoord = ''.join(random.choice(chars) for _ in range(12))
    print(f"[INFO] Gegenereerd wachtwoord: {wachtwoord}")
    return wachtwoord

# LDAP verbinding
print("[INFO] Verbinden met domain controller...")
server = Server('ldap://192.168.2.14', get_info=ALL)
conn = Connection(server, user='BUUNK\\jurre', password='F+NywdK7f8;eC~tD', auto_bind=True)
print("[INFO] Verbonden met ws1.buunk.org.")

gebruikersnaam = "testdihhh"
voornaam = "test"
achternaam = "dihhh"

wachtwoord = genereer_wachtwoord()
dn = f"CN={gebruikersnaam},OU=Domain-Users,DC=buunk,DC=org"

print(f"[INFO] Aanmaken van gebruiker: {gebruikersnaam}")
print(f"[DEBUG] DN: {dn}")
print(f"[DEBUG] Voornaam: {voornaam}, Achternaam: {achternaam}")
print(f"[DEBUG] UserPrincipalName: {gebruikersnaam}@buunk.org")

# Gebruiker toevoegen
result = conn.add(dn, ['top', 'person', 'organizationalPerson', 'user'], {
    'cn': gebruikersnaam,
    'givenName': voornaam,
    'sn': achternaam,
    'displayName': f"{voornaam} {achternaam}",
    'userPrincipalName': f"{gebruikersnaam}@buunk.org",
    'sAMAccountName': gebruikersnaam,
    'userAccountControl': 512,
    'unicodePwd': ('"%s"' % wachtwoord).encode('utf-16-le')
})

if result:
    print("[SUCCESS] Gebruiker succesvol toegevoegd.")
else:
    print(f"[ERROR] Fout bij toevoegen gebruiker: {conn.result}")

# Account ontgrendelen
print("[INFO] Proberen account te ontgrendelen...")
try:
    conn.extend.microsoft.unlock_account(dn)
    print("[SUCCESS] Account ontgrendeld.")
except Exception as e:
    print(f"[ERROR] Ontgrendelen mislukt: {e}")

# UserAccountControl resetten naar enabled
print("[INFO] UserAccountControl opnieuw instellen op 512...")
mod_result = conn.modify(dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]})
if mod_result:
    print("[SUCCESS] userAccountControl ingesteld.")
else:
    print(f"[ERROR] userAccountControl wijzigen mislukt: {conn.result}")

print(f"[EINDE] Gebruiker '{gebruikersnaam}' is volledig verwerkt.")
