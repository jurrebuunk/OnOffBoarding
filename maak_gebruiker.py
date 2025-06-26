from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import ssl
import random
import string

def genereer_wachtwoord():
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(random.choice(chars) for _ in range(12))

server = Server('ldap://192.168.2.14', get_info=ALL)
conn = Connection(server, user='BUUNK\\jurre', password='F+NywdK7f8;eC~tD', auto_bind=True)

gebruikersnaam = "testdih"
voornaam = "test"
achternaam = "dih"

wachtwoord = genereer_wachtwoord()
dn = f"CN={gebruikersnaam},OU=Domain-Users,DC=buunk,DC=org"

conn.add(dn, ['top', 'person', 'organizationalPerson', 'user'], {
    'cn': gebruikersnaam,
    'givenName': voornaam,
    'sn': achternaam,
    'displayName': f"{voornaam} {achternaam}",
    'userPrincipalName': f"{gebruikersnaam}@bedrijf.local",
    'sAMAccountName': gebruikersnaam,
    'userAccountControl': 512,
    'unicodePwd': ('"%s"' % wachtwoord).encode('utf-16-le')
})

conn.extend.microsoft.unlock_account(dn)
conn.modify(dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]})

print(f"Gebruiker {gebruikersnaam} is aangemaakt.")
