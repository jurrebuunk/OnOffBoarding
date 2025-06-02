from ldap3 import Server, Connection, ALL, NTLM, MODIFY_REPLACE
import os

server = Server('ldaps://ws1.buunk.org', get_info=ALL, use_ssl=True)
conn = Connection(server, user="BUUNK\\ldap-search", password=os.getenv('AD_SEARCH_PW'), authentication=NTLM)

if not conn.bind():
    print('Bind mislukt:', conn.last_error)
    exit(1)
print('Bind succesvol')

dn = f"cn={os.getenv('cn')},ou=Domain-Users,dc=buunk,dc=org"
attrs = {
    'cn': os.getenv('cn'),
    'givenName': os.getenv('givenName'),
    'sn': os.getenv('sn'),
    'displayName': os.getenv('name'),
    'name': os.getenv('name'),
    'userPrincipalName': os.getenv('userPrincipalName'),
    'sAMAccountName': os.getenv('sAMAccountName'),
    'mail': os.getenv('mail'),
    'telephoneNumber': os.getenv('telephoneNumber') or ''
}

conn.add(dn, ['top', 'person', 'organizationalPerson', 'user'], attrs)
if conn.result['description'] != 'success':
    print('Toevoegen mislukt:', conn.result)
    conn.unbind()
    exit(1)

if not conn.extend.microsoft.modify_password(dn, "Welkom01"):
    print('Wachtwoord zetten mislukt:', conn.result)
    conn.unbind()
    exit(1)

if not conn.modify(dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]}):
    print('Account activeren mislukt:', conn.result)
    conn.unbind()
    exit(1)

print('Gebruiker aangemaakt en geactiveerd')
conn.unbind()
