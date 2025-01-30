import os
import requests
from time import sleep
from threading import Thread, active_count
import random
import phonenumbers
from phonenumbers import PhoneNumberFormat
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup

# Define software and OS for User-Agent rotation
software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.EDGE.value, SoftwareName.OPERA.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]

# User-Agent Rotator
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1200)

# Configurations
THREADS = 1
PROXIES_TYPES = ('http', 'socks4', 'socks5')
time_out = 15
success_count = 0
error_count = 0
username = ""

print("This script was originally coded by @thehackingzone, recoded (updated for latest API) by @frostfoe (t.me/systemadminbd)...")

# Read a random email from emails.txt
def get_random_email(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            return random.choice(lines).strip() if lines else "default@example.com"
    except FileNotFoundError:
        return "default@example.com"

# Read a random phone number from numbers.txt
def get_random_phone_number(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            return random.choice(lines).strip() if lines else "+10000000000"
    except FileNotFoundError:
        return "+10000000000"

# Read a random message from message.txt
def get_random_message(filename, username):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            return random.choice(lines).strip().replace('{username}', username) if lines else "Default report message"
    except FileNotFoundError:
        return "Default report message"

# Function to send the report
def control(proxy, proxy_type, username):
    global success_count, error_count

    USER_AGENT = user_agent_rotator.get_random_user_agent()
    url = 'https://telegram.org/support'

    try:
        response = requests.get(url, proxies={'http': f'{proxy_type}://{proxy}', 'https': f'{proxy_type}://{proxy}'}, timeout=time_out)
    except Exception as e:
        error_count += 1
        return

    cookies = response.cookies
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form', action="/support")

    if not form:
        print("Form not found on the page.")
        return

    # Get email, phone, and message from files
    email = get_random_email('emails.txt')
    phone = get_random_phone_number('numbers.txt')
    message = get_random_message('message.txt', username)

    # Prepare form data to match the new field names
    data = {
        'support_problem': message,  # message text
        'legal_name': 'Anonymous',   # a placeholder full legal name (you can customize this)
        'email': email,              # email from file
        'phone': phone,              # phone from file
        'setln': '',                 # empty value for language or additional field
    }

    headers = {'User-Agent': USER_AGENT}

    try:
        response = requests.post(url, data=data, cookies=cookies, headers=headers)
        if response.status_code == 200:
            print(f"✅ Report Successful! Email: {email}, Phone: {phone}, Message: {message}, Proxy: {proxy, proxy_type}\n")
            success_count += 1
        else:
            error_count += 1
    except Exception as e:
        error_count += 1
        return

# Handle proxy threads
def get_views_from_saved_proxies(proxy_type, proxies, username):
    for proxy in proxies:
        control(proxy.strip(), proxy_type, username)

def start_view():
    while True:
        threads = []
        for proxy_type in PROXIES_TYPES:
            try:
                with open(f"{proxy_type}_proxies.txt", 'r') as file:
                    proxies = file.readlines()
                chunked_proxies = [proxies[i:i + 5] for i in range(0, len(proxies), 5)]
                for chunk in chunked_proxies:
                    thread = Thread(target=get_views_from_saved_proxies, args=(proxy_type, chunk, username))
                    threads.append(thread)
                    thread.start()
            except FileNotFoundError:
                print(f"⚠️ {proxy_type}_proxies.txt not found, skipping...")

        for t in threads:
            t.join()

# Display status of reports
def check_views():
    global success_count, error_count
    while True:
        print(f"\n[ 🔹 TOTAL THREADS ]: {active_count()}\n[ ✅ SUCCESSFUL REPORTS ]: {success_count}\n[ ❌ FAILED REPORTS ]: {error_count}\n")
        sleep(4)

# Get username input
username = input("Enter the username of the Channel, Person, or Group you want to report (or paste the link): ")

Thread(target=start_view).start()
Thread(target=check_views).start()
