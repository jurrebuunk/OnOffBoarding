from ldap3 import Server, Connection, ALL
import json
import os

# LDAP server and credentials
ldap_server = 'ldap://192.168.2.14'
ldap_user = os.getenv('AD_SEARCH_UN')
ldap_password = os.getenv('AD_SEARCH_PW')

# Connect to the server
server = Server(ldap_server, get_info=ALL)
conn = Connection(server, user=ldap_user, password=ldap_password, auto_bind=True)

# Search for the user
search_base = 'dc=buunk,dc=org'
search_filter = '(sAMAccountName=jurre)'
conn.search(search_base, search_filter, attributes=['cn', 'displayName', 'mail', 'memberOf'])

# Display user information and group memberships
for entry in conn.entries:
    print(f"Common Name: {entry.cn}")
    print(f"Display Name: {entry.displayName}")
    print(f"Email: {entry.mail}")
    print("Groups:")
    for group_dn in entry.memberOf:
        print(f"  {group_dn}")

conn.unbind()
