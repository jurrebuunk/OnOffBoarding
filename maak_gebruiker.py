from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import ssl
import random
import string

def genereer_wachtwoord():
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(random.choice(chars) for _ in range(12))

server = Server('ldap://dc01.bedrijf.local', get_info=ALL)
conn = Connection(server, user='bedrijf\\admin', password='jouwWachtwoord', auto_bind=True)

gebruikersnaam = input("Gebruikersnaam: ")
voornaam = input("Voornaam: ")
achternaam = input("Achternaam: ")
groep = input("Groep: ")

wachtwoord = genereer_wachtwoord()
dn = f"CN={gebruikersnaam},OU=Gebruikers,DC=bedrijf,DC=local"

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

# Toevoegen aan groep
groep_dn = f"CN={groep},OU=Groepen,DC=bedrijf,DC=local"
conn.modify(groep_dn, {'member': [(MODIFY_REPLACE, [dn])]})

print(f"Gebruiker {gebruikersnaam} is aangemaakt.")
