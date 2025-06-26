import paramiko

hostname = "192.168.2.14"      # IP van de Windows-server
port = 22
username = "jurre"
password = "F+NywdK7f8;eC~tD"
# PowerShell command: wijzig 'gebruikersnaam' en 'NieuwW8woord!' indien nodig
ps_command = 'powershell -Command "Set-ADAccountPassword -Identity \'usetes01\' -Reset -NewPassword (ConvertTo-SecureString \'NieuwW8woord!\' -AsPlainText -Force)"'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname, port, username, password)

stdin, stdout, stderr = client.exec_command(ps_command)

print("OUTPUT:")
print(stdout.read().decode())

print("ERRORS:")
print(stderr.read().decode())

client.close()
