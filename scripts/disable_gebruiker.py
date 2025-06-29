from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import os
import sys

required_env = ["LDAP_HOST", "LDAP_USER", "LDAP_PASS", "username"]
missing = [var for var in required_env if not os.getenv(var)]
if missing:
    print(f"[ERROR] Ontbrekende omgevingsvariabelen: {', '.join(missing)}")
    sys.exit(1)

print("[INFO] Verbinden met domain controller...")
server = Server(os.environ["LDAP_HOST"], get_info=ALL)
conn = Connection(server, user=os.environ["LDAP_USER"], password=os.environ["LDAP_PASS"], auto_bind=True)
print(f"[INFO] Verbonden met {server.host}.")

username = os.environ["username"]
base_dn = "DC=buunk,DC=org"
disabled_ou = f"OU=Disabled-Users,{base_dn}"

# Zoek gebruiker
conn.search(base_dn, f"(sAMAccountName={username})", attributes=["distinguishedName", "userAccountControl"])
if not conn.entries:
    print(f"[ERROR] Gebruiker '{username}' niet gevonden.")
    sys.exit(1)

entry = conn.entries[0]
user_dn = entry.distinguishedName.value
current_uac = int(entry.userAccountControl.value)
disabled_uac = current_uac | 0x2  # ACCOUNTDISABLE bit

# Zet account op disabled
success1 = conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [disabled_uac])]})
if success1:
    print(f"[INFO] Gebruiker '{username}' uitgeschakeld.")
else:
    print(f"[ERROR] Uitschakelen mislukt: {conn.result}")
    sys.exit(1)

# Verplaats naar OU
rdn = user_dn.split(',')[0]
new_dn = f"{rdn},{disabled_ou}"

success2 = conn.modify_dn(user_dn, rdn, new_superior=disabled_ou)
if success2:
    print(f"[INFO] Gebruiker verplaatst naar: {disabled_ou}")
else:
    print(f"[ERROR] Verplaatsen mislukt: {conn.result}")
