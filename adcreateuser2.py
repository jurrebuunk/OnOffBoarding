from pyad import pyad
from pyad.aduser import ADUser
from pyad.adcontainer import ADContainer

pyad.set_defaults(ldap_server="192.168.2.14", username="BUUNK\\ldap-search", password=os.getenv('AD_SEARCH_PW'))

container = ADContainer.from_dn("ou=Domain-Users,dc=buunk,dc=org")

user = ADUser.create(
    sam_account_name=os.getenv('sAMAccountName'),
    container_object=container,
    password="Welkom01",
    optional_attributes={
        'givenName': os.getenv('givenName'),
        'sn': os.getenv('sn'),
        'displayName': os.getenv('name'),
        'userPrincipalName': os.getenv('userPrincipalName'),
        'mail': os.getenv('mail'),
        'telephoneNumber': os.getenv('telephoneNumber') or '',
    }
)

user.enable()
