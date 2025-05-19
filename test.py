import os
import json
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

# Create the main window
root = tk.Tk()
root.title("New Object - User")
root.geometry("435x410")
root.resizable(False, False)

# Create a frame to hold all the widgets
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)
frame.pack_propagate(False)


# Variables for syncing
user_var = tk.StringVar()
first_var = tk.StringVar()
last_var = tk.StringVar()
init_var = tk.StringVar()


# Load image for the icon (64x64), with fallback if not found
icon_path = "user_icon.png"
if os.path.exists(icon_path):
    user_img = Image.open(icon_path).resize((48, 48))
    user_photo = ImageTk.PhotoImage(user_img)
else:
    user_photo = None

def change_profile_picture():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.tiff;*.ico")])
    if file_path:
        try:
            img = Image.open(file_path).convert("RGB")
            w, h = img.size
            min_dim = min(w, h)
            left = (w - min_dim) // 2
            top = (h - min_dim) // 2
            right = left + min_dim
            bottom = top + min_dim
            cropped = img.crop((left, top, right, bottom)).resize((96, 96))

            cropped.save("profile_temp.jpg", format="JPEG")

            display_img = cropped.resize((48, 48), Image.LANCZOS)
            new_photo = ImageTk.PhotoImage(display_img)
            icon_button.config(image=new_photo)
            icon_button.image = new_photo
        except Exception as e:
            print("Error loading image:", e)

# Image button (icon left of "Create in")
icon_button = tk.Button(frame, image=user_photo, relief='flat', borderwidth=0, command=change_profile_picture, width=48, height=48)
icon_button.grid(row=0, column=0, sticky=tk.NW, padx=(25, 10), pady=10)

# "Create in" label next to the image
create_label = tk.Label(frame, text="Create in: buunk.org/Domain-Users")
create_label.grid(row=0, column=1, columnspan=3, sticky=tk.W, padx=0, pady=5)

# Horizontal line separator under image and label
sep1 = ttk.Separator(frame, orient='horizontal')
sep1.grid(row=1, column=0, columnspan=4, sticky='ew', padx=10, pady=0)

# First name and Initials
label_fn = tk.Label(frame, text="First name:")
label_fn.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
entry_fn = tk.Entry(frame, textvariable=first_var)
entry_fn.grid(row=2, column=1, padx=10, pady=5)

label_init = tk.Label(frame, text="Initials:")
label_init.grid(row=2, column=2, sticky=tk.W, padx=10, pady=5)
entry_init = tk.Entry(frame, textvariable=init_var)
entry_init.grid(row=2, column=3, padx=10, pady=5)

# Last name
label_ln = tk.Label(frame, text="Last name:")
label_ln.grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
entry_ln = tk.Entry(frame, textvariable=last_var)
entry_ln.grid(row=3, column=1, columnspan=3, sticky=tk.EW, padx=10, pady=5)

# Full name
label_full = tk.Label(frame, text="Full name:")
label_full.grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
entry_full = tk.Entry(frame)
entry_full.grid(row=4, column=1, columnspan=3, sticky=tk.EW, padx=10, pady=5)

def update_full_name(*args):
    current_full = entry_full.get()
    initial = init_var.get().strip()
    init_part = (initial + ".") if initial else ""
    parts = [first_var.get().strip()]
    if init_part:
        parts.append(init_part)
    parts.append(last_var.get().strip())
    combined = " ".join(p for p in parts if p)
    if combined != current_full:
        entry_full.delete(0, tk.END)
        entry_full.insert(0, combined)

first_var.trace_add('write', update_full_name)
last_var.trace_add('write', update_full_name)
init_var.trace_add('write', update_full_name)

# E-mail
label_email = tk.Label(frame, text="E-mail:")
label_email.grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
entry_email = tk.Entry(frame)
entry_email.grid(row=5, column=1, columnspan=3, sticky=tk.EW, padx=10, pady=5)

# Telephone number
label_phone = tk.Label(frame, text="Telephone:")
label_phone.grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
entry_phone = tk.Entry(frame)
entry_phone.grid(row=6, column=1, columnspan=3, sticky=tk.EW, padx=10, pady=5)

# User logon name
label_un = tk.Label(frame, text="User logon name:")
label_un.grid(row=7, column=0, columnspan=4, sticky=tk.W, padx=10, pady=(5, 0))
entry_un = tk.Entry(frame, textvariable=user_var)
entry_un.grid(row=8, column=0, columnspan=2, sticky=tk.EW, padx=(10, 5), pady=5)
combo_domain = ttk.Combobox(frame, values=["@buunk.org"])
combo_domain.current(0)
combo_domain.grid(row=8, column=2, columnspan=2, sticky=tk.EW, padx=(5, 10), pady=5)

# Pre-Windows 2000 logon name
label_pre = tk.Label(frame, text="User logon name (pre-Windows 2000):")
label_pre.grid(row=9, column=0, columnspan=4, sticky=tk.W, padx=10, pady=(5, 0))
entry_pre_ro = tk.Entry(frame, state='readonly', readonlybackground='#f0f0f0')
entry_pre_ro.grid(row=10, column=0, columnspan=2, sticky=tk.EW, padx=(10, 5), pady=5)
entry_pre = tk.Entry(frame, textvariable=user_var)
entry_pre.grid(row=10, column=2, columnspan=2, sticky=tk.EW, padx=(5, 10), pady=5)

# Horizontal line separator above buttons
sep2 = ttk.Separator(frame, orient='horizontal')
sep2.grid(row=11, column=0, columnspan=4, sticky='ew', padx=10, pady=5)

def print_ad_user_data():
    domain = combo_domain.get().lstrip("@")
    username = user_var.get().strip()
    first_name = first_var.get().strip()
    last_name = last_var.get().strip()
    initials = init_var.get().strip()
    full_name = entry_full.get().strip()
    email = entry_email.get().strip()
    phone = entry_phone.get().strip()

    env_vars = {
        "cn": full_name,
        "givenName": first_name,
        "sn": last_name,
        "initials": initials,
        "name": full_name,
        "userPrincipalName": f"{username}@{domain}",
        "sAMAccountName": username,
        "mail": email,
        "telephoneNumber": phone
    }

    url = "https://semaphore.buunk.org/api/project/1/environment/4"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer wiguvkryyipv7javuxkz9qfstckt7pvfvfywrvo9qww="
    }
    payload = {
        "id": 4,
        "name": "Create AD User",
        "project_id": 1,
        "password": "string",
        "json": "{}",
        "env": json.dumps(env_vars),
        "secrets": [
            {
                "id": 0,
                "type": "env",
                "name": "AD_SEARCH_PW",
                "secret": "DRPpgbzxr2CS6XMqYBZv",
                "operation": "create"
            }
        ]
    }

    response = requests.put(url, headers=headers, data=json.dumps(payload))
    print(f"Env Update Status: {response.status_code}")

    # Start task
    task_url = "https://semaphore.buunk.org/api/project/1/tasks"
    task_payload = {
        "template_id": 2
    }
    task_response = requests.post(task_url, headers=headers, data=json.dumps(task_payload))
    print(f"Task Trigger Status: {task_response.status_code}")
    print(f"Task Response: {task_response.text}")


# Buttons aligned to bottom right
button_frame = tk.Frame(frame)
button_frame.grid(row=12, column=0, columnspan=4, sticky=tk.E, padx=10, pady=10)
btn_add = tk.Button(button_frame, text="Add User", command=print_ad_user_data)
btn_add.pack(side=tk.LEFT, padx=5)
btn_cancel = tk.Button(button_frame, text="Cancel", command=root.destroy)
btn_cancel.pack(side=tk.LEFT, padx=5)

def update_email(*args):
    first = first_var.get().strip().lower()
    last = last_var.get().strip().lower()
    domain = combo_domain.get().lstrip("@")
    if first and last and domain:
        email = f"{first}.{last}@{domain}"
        entry_email.delete(0, tk.END)
        entry_email.insert(0, email)

first_var.trace_add('write', update_email)
last_var.trace_add('write', update_email)
combo_domain.bind("<<ComboboxSelected>>", lambda e: update_email())

def update_username(*args):
    first = first_var.get().strip().lower()
    last = last_var.get().strip().lower()
    if first and last:
        username = f"{first}{last}"
        user_var.set(username)

first_var.trace_add('write', update_username)
last_var.trace_add('write', update_username)

# Run the application
root.mainloop()
