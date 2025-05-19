from ldap3 import Server, Connection, ALL, NTLM, MODIFY_REPLACE
import os

# LDAP server and credentials
ldap_server = 'ldap://192.168.2.14'
ldap_user = "BUUNK\\ldap-search"
ldap_password = os.getenv('AD_SEARCH_PW')

print(ldap_user)
print(ldap_password)

# New user details from environment variables
sAMAccountName = os.getenv('sAMAccountName')
password = "Welkom01"
givenName = os.getenv('givenName')
surname = os.getenv('surname')

user_dn = f'cn={sAMAccountName},ou=Domain-Users,dc=buunk,dc=org'

# Connect to the server
server = Server(ldap_server, get_info=ALL)
conn = Connection(server, user=ldap_user, password=ldap_password, authentication=NTLM, auto_bind=True)

# Add the new user
conn.add(user_dn, ['top', 'person', 'organizationalPerson', 'user'], {
    'cn': sAMAccountName,
    'givenName': givenName,
    'sn': surname,
    'displayName': f'{first_name} {last_name}',
    'sAMAccountName': sAMAccountName,
    'userPrincipalName': f'{new_username}@buunk.org'
})

# Set the user's password
conn.extend.microsoft.modify_password(user_dn, new_password)

# Enable the user account
conn.modify(user_dn, {
    'userAccountControl': [(MODIFY_REPLACE, [512])]
})

# Unbind the connection
conn.unbind()
