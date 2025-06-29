import os
import sys
import json
import argparse
import requests
from colorama import init, Fore, Style

init(autoreset=True)

api_config = None

def print_info(msg):
    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {msg}")

def print_error(msg):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

def get_fields_input(fields):
    values = {}
    i = 0
    while i < len(fields):
        field = fields[i]
        value = input(f"{field}: ")
        if value.lower() == "back":
            if i > 0:
                i -= 1
            else:
                print_info("Already at the first field.")
            continue
        values[field] = value
        i += 1
    return values

def set_env_vars(vargroup_id, groupname, env_vars):
    if not api_config:
        print_error("Geen API-config geladen.")
        sys.exit(1)

    try:
        url = f"{api_config['url'].rstrip('/')}/api/project/1/environment/{vargroup_id}"
        headers = {
            "Authorization": f"Bearer {api_config['key']}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "id": vargroup_id,
            "name": groupname,
            "project_id": 1,
            "password": "string",
            "json": "{}",
            "env": json.dumps(env_vars),
            "secrets": []
        }
        r = requests.put(url, headers=headers, json=payload)
        if r.status_code in [200, 204]:
            print_info(f"API env-variabelen ingesteld voor groep '{groupname}'.")
        else:
            print_error(f"API fout bij instellen vars: {r.status_code} - {r.text}")
    except Exception as e:
        print_error(f"API env-update gefaald: {e}")
        sys.exit(1)

def start_task(template_id):
    if not api_config:
        print_error("Geen API-config geladen.")
        sys.exit(1)

    try:
        url = f"{api_config['url'].rstrip('/')}/api/project/1/tasks"
        headers = {
            "Authorization": f"Bearer {api_config['key']}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        r = requests.post(url, headers=headers, json={"template_id": int(template_id)})
        if r.status_code == 201:
            task_id = r.json().get("id")
            if task_id:
                print_info(f"API taak gestart met ID {task_id}.")
                print("Bezoek de volgende link om de resultaten te zien:")
                print(f"https://semaphore.buunk.org/project/1/templates/{template_id}/tasks?t={task_id}")
            else:
                print_info("API taak gestart, maar task ID kon niet worden opgehaald.")
        else:
            print_error(f"API fout bij starten taak: {r.status_code} - {r.text}")
    except Exception as e:
        print_error(f"API taak-start gefaald: {e}")
        sys.exit(1)

def confr(value):
    try:
        with open("oobconf.json", "r") as f:
            conf = json.load(f)
        return conf.get(value, "")
    except Exception as e:
        print_error(f"Laden van oobconf.json mislukt: {e}")
        sys.exit(1)

def create_user():
    input_fields = ["givenName", "sn"]

    static_fields = {
        "LDAP_HOST": confr("LDAP_HOST"),
        "LDAP_USER": confr("LDAP_USER"),
        "LDAP_PASS": confr("LDAP_PASS")
    }

    user_data = get_fields_input(input_fields)

    user_data["initials"] = input("initials (Optioneel): ")
    user_data["mail"] = input("mail (Optioneel): ")
    user_data["telephoneNumber"] = input("telephoneNumber (Optioneel): ")

    for key, value in static_fields.items():
        user_data[key] = value

    if api_config:
        set_env_vars(vargroup_id=4, groupname="maak_gebruiker_var", env_vars=user_data)
        start_task(template_id=3)
    else:
        for key, value in user_data.items():
            os.environ[key] = value
        os.system("python scripts/maak_gebruiker.py")
        print_info("Lokaal uitgevoerd.")

def zoek_gebruiker():
    input_fields = [
        "search"
    ]

    static_fields = {
        "LDAP_HOST": confr("LDAP_HOST"),
        "LDAP_USER": confr("LDAP_USER"),
        "LDAP_PASS": confr("LDAP_PASS")
    }

    user_data = get_fields_input(input_fields)

    for key, value in static_fields.items():
        user_data[key] = value

    if api_config:
        set_env_vars(vargroup_id=5, groupname="zoek_gebruiker_var", env_vars=user_data)
        start_task(template_id=3)
    else:
        for key, value in user_data.items():
            os.environ[key] = value
        os.system("python scripts/zoek_gebruiker.py")
        print_info("Lokaal uitgevoerd.")

def voeg_gebruiker_aan_groep():
    input_fields = [
        "username",
        "group"
    ]

    static_fields = {
        "LDAP_HOST": confr("LDAP_HOST"),
        "LDAP_USER": confr("LDAP_USER"),
        "LDAP_PASS": confr("LDAP_PASS")
    }

    user_data = get_fields_input(input_fields)

    for key, value in static_fields.items():
        user_data[key] = value

    if api_config:
        set_env_vars(vargroup_id=6, groupname="voeg_gebruiker_aan_groep_var", env_vars=user_data)
        start_task(template_id=5)
    else:
        for key, value in user_data.items():
            os.environ[key] = value
        os.system("python scripts/voeg_gebruiker_aan_groep.py")
        print_info("Lokaal uitgevoerd.")

def copy_gebruiker_groepen():
    input_fields = [
        "vangebruiker",
        "naargebruiker"
    ]

    static_fields = {
        "LDAP_HOST": confr("LDAP_HOST"),
        "LDAP_USER": confr("LDAP_USER"),
        "LDAP_PASS": confr("LDAP_PASS")
    }

    user_data = get_fields_input(input_fields)

    # Vraag naar sync
    sync = input("Exacte kopie (true/false, standaard=false)? ")
    user_data["sync"] = "true" if sync == "true" else "false"

    for key, value in static_fields.items():
        user_data[key] = value

    if api_config:
        set_env_vars(vargroup_id=7, groupname="copy_gebruiker_groepen_var", env_vars=user_data)
        start_task(template_id=6)
    else:
        for key, value in user_data.items():
            os.environ[key] = value
        os.system("python scripts/copy_gebruiker_groepen.py")
        print_info("Lokaal uitgevoerd.")

def disable_gebruiker():
    input_fields = [
        "username"
    ]

    static_fields = {
        "LDAP_HOST": confr("LDAP_HOST"),
        "LDAP_USER": confr("LDAP_USER"),
        "LDAP_PASS": confr("LDAP_PASS")
    }

    user_data = get_fields_input(input_fields)

    for key, value in static_fields.items():
        user_data[key] = value

    if api_config:
        set_env_vars(vargroup_id=8, groupname="disable_gebruiker_var", env_vars=user_data)
        start_task(template_id=7)
    else:
        for key, value in user_data.items():
            os.environ[key] = value
        os.system("python scripts/disable_gebruiker.py")
        print_info("Lokaal uitgevoerd.")

commands = {
    "maak_gebruiker": create_user,
    "zoek_gebruiker": zoek_gebruiker,
    "voeg_gebruiker_aan_groep": voeg_gebruiker_aan_groep,
    "copy_gebruiker_groepen": copy_gebruiker_groepen,
    "disable_gebruiker": disable_gebruiker,
}

def load_api_config(path="api.json"):
    global api_config
    try:
        with open(path, 'r') as f:
            api_config = json.load(f)
    except Exception as e:
        print_error(f"API-config laden gefaald: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="Command to run", choices=commands.keys())
    parser.add_argument("-a", "--api", nargs='?', const="api.json", help="Pad naar API-config JSON (optioneel, standaard: api.json)")
    args = parser.parse_args()

    if args.api:
        load_api_config(args.api)

    func = commands.get(args.command)
    if func:
        func()
    else:
        print_error(f"Unknown command: {args.command}")
