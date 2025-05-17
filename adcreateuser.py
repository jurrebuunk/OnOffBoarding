from ldap3 import Server, Connection, ALL, NTLM, MODIFY_REPLACE
import os

# LDAP server and credentials
ldap_server = 'ldap://192.168.2.14'
ldap_user = "BUUNK\\ldap-search"
ldap_password = os.getenv('AD_SEARCH_PW')

# New user details from environment variables
new_username = os.getenv('username')
new_password = os.getenv('password')
first_name = os.getenv('firstname')
last_name = os.getenv('lastname')
user_dn = f'cn={new_username},ou=Domain-Users,dc=buunk,dc=org'

print("username:", new_username)
print("firstname:", first_name)
print("lastname:", last_name)
print("password:", new_password)

# Connect to the server
server = Server(ldap_server, get_info=ALL)
conn = Connection(server, user=ldap_user, password=ldap_password, authentication=NTLM, auto_bind=True)

# Add the new user
conn.add(user_dn, ['top', 'person', 'organizationalPerson', 'user'], {
    'cn': new_username,
    'givenName': first_name,
    'sn': last_name,
    'displayName': f'{first_name} {last_name}',
    'sAMAccountName': new_username,
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
