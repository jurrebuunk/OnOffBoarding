from ldap3 import Server, Connection, ALL, NTLM, MODIFY_REPLACE
import os

# LDAP server and credentials
ldap_server = 'ldap://192.168.2.14'
ldap_user = "BUUNK\\ldap-search"
ldap_password = os.getenv('AD_SEARCH_PW')

print(ldap_user)
print(ldap_password)

cn = os.getenv('cn')
given_name = os.getenv('givenName')
surname = os.getenv('sn')
initials = os.getenv('initials') or ''
name = os.getenv('name')
user_principal_name = os.getenv('userPrincipalName')
sam_account_name = os.getenv('sAMAccountName')
email = os.getenv('mail')
telephone = os.getenv('telephoneNumber') or ''

password = "Welkom01"

print("cn:", cn)
print("givenName:", given_name)
print("sn:", surname)
print("initials:", initials)
print("name:", name)
print("userPrincipalName:", user_principal_name)
print("sAMAccountName:", sam_account_name)
print("mail:", email)
print("telephoneNumber:", telephone)
print("password:", password)

user_dn = f'cn={cn},ou=Domain-Users,dc=buunk,dc=org'

# Connect to the server
server = Server(ldap_server, get_info=ALL)
conn = Connection(server, user=ldap_user, password=ldap_password, authentication=NTLM, auto_bind=True)

# Add the new user
conn.add(user_dn, ['top', 'person', 'organizationalPerson', 'user'], {
    'cn': cn,
    'givenName': given_name,
    'sn': surname,
    'displayName': name,
    'name': name,
    'userPrincipalName': user_principal_name,
    'sAMAccountName': sam_account_name
})

# Set the user's password
conn.extend.microsoft.modify_password(user_dn, password)

# Enable the user account
conn.modify(user_dn, {
    'userAccountControl': [(MODIFY_REPLACE, [512])]
})

# Unbind the connection
conn.unbind()
