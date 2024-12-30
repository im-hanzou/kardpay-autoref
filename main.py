import requests
import json
import random
import time
import string
import names
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

header = {
    'User-Agent': "okhttp/4.9.2 (Linux; Android 14; Pixel 8 Pro Build/UQ1A.240105.004)",
    'Connection': "keep-alive", 
    'Accept': "application/json, text/plain, */*",
    'Accept-Encoding': "gzip, deflate, br",
    'Content-Type': "application/json; charset=UTF-8",
    'Cache-Control': "no-cache",
    'Pragma': "no-cache"
}

def get_log_prefix(account_num=None, total=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if account_num is not None and total is not None:
        return f"[{Fore.LIGHTBLUE_EX}{timestamp}{Style.RESET_ALL}] [{Fore.LIGHTCYAN_EX}{account_num}/{total}{Style.RESET_ALL}]"
    return f"[{Fore.LIGHTBLUE_EX}{timestamp}{Style.RESET_ALL}]"

def get_random_proxy(proxies):
    if not proxies:
        return None
    return random.choice(proxies)

def load_proxies(file_path):
    try:
        with open(file_path, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        print(f"{Fore.LIGHTGREEN_EX}Loaded {len(proxies)} proxies{Style.RESET_ALL}")
        return proxies
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}No proxy file found, running without proxies{Style.RESET_ALL}")
        return []
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error loading proxies: {str(e)}{Style.RESET_ALL}")
        return []

def generate_keyword():
    vowels = 'aeiou'
    consonants = ''.join(set(string.ascii_lowercase) - set(vowels))
    return random.choice(consonants) + random.choice(vowels)

def get_random_domain(proxy_dict):
    keyword = generate_keyword()
    #url = f"https://emailfake.com/search.php?key={keyword}"
    url = f"https://generator.email/search.php?key={keyword}"
    
    try:
        resp = requests.get(url, proxies=proxy_dict, timeout=60)
        resp.raise_for_status()
        domains = resp.json()
        return random.choice(domains) if domains else None
    except Exception as e:
        print(f"{get_log_prefix()} {Fore.LIGHTRED_EX}Error fetching domain: {str(e)}{Style.RESET_ALL}")
        return None

def generate_username():
    first_name = names.get_first_name().lower()
    last_name = names.get_last_name().lower()
    separator = random.choice(['', '.'])
    random_numbers = ''.join(random.choices(string.digits, k=3))
    return f"{first_name}{separator}{last_name}{random_numbers}"

def generate_password():
    word = ''.join(random.choices(string.ascii_letters, k=5))
    numbers = ''.join(random.choices(string.digits, k=3))
    return f"{word.capitalize()}@{numbers}#"

def generate_email(proxy_dict):
    domain = get_random_domain(proxy_dict)
    if not domain:
        return None
    username = generate_username()
    return f"{username}@{domain}"

def save_account(email, password, account_num, total):
    with open('accounts.txt', 'a') as f:
        f.write(f"{email}|{password}\n")
    print(f"{get_log_prefix(account_num, total)} {Fore.LIGHTMAGENTA_EX}Complete! Account saved to accounts.txt{Style.RESET_ALL}")

def send_otp(email, password, proxy_dict, account_num, total):
    url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser"
    params = {
        'key': "AIzaSyDmqZpkteihdMSDV5-VkNjgGBeLbFjGRCg"
    }
    payload = {
        "email": email,
        "password": password,
        "clientType": "CLIENT_TYPE_ANDROID"
    }

    headers = dict(header)

    try:
        response = requests.post(url, params=params, json=payload,
                               headers=headers, proxies=proxy_dict, timeout=60)
        result = response.json()

        if response.status_code == 200:
            print(f"{get_log_prefix(account_num, total)} {Fore.LIGHTGREEN_EX}Success Register{Style.RESET_ALL}")
            return result
        else:
            print(f"{get_log_prefix(account_num, total)} {Fore.LIGHTRED_EX}Register failed: {result}{Style.RESET_ALL}")
            return None
    except requests.RequestException as e:
        print(f"{get_log_prefix(account_num, total)} {Fore.LIGHTRED_EX}Request error: {str(e)}{Style.RESET_ALL}")
        return None

def login(id_token, proxy_dict, account_num, total):
    url = "https://api.kardpay.app/waitinglist/users/user/login"
    headers = dict(header)
    headers['Authorization'] = f"Bearer {id_token}"

    try:
        response = requests.post(url, headers=headers, proxies=proxy_dict, timeout=60)
        response.raise_for_status()
        print(f"{get_log_prefix(account_num, total)} {Fore.LIGHTGREEN_EX}Success Login{Style.RESET_ALL}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{get_log_prefix(account_num, total)} {Fore.LIGHTRED_EX}Login error: {str(e)}{Style.RESET_ALL}")
        return None

def set_reff(referral_code, token, proxy_dict, account_num, total):
    url = "https://api.kardpay.app/waitinglist/users/user/sponsor"
    payload = {"referralCode": referral_code}
    headers = dict(header)
    headers['Authorization'] = f"Bearer {token}"

    try:
        response = requests.post(url, headers=headers, json=payload, proxies=proxy_dict, timeout=60)
        if response.status_code == 200:
            print(f"{get_log_prefix(account_num, total)} {Fore.LIGHTGREEN_EX}Success Referral{Style.RESET_ALL}")
            return True
        else:
            print(f"{get_log_prefix(account_num, total)} {Fore.LIGHTRED_EX}Failed to referral: {response.text}{Style.RESET_ALL}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{get_log_prefix(account_num, total)} {Fore.LIGHTRED_EX}Referral error: {str(e)}{Style.RESET_ALL}")
        return False

def print_banner():
    banner = f"""
{Fore.LIGHTCYAN_EX}╔═══════════════════════════════════════════╗
║          KardPay Autoreferral             ║
║       https://github.com/im-hanzou        ║
╚═══════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def process_single_registration(proxies, referral_code, account_num, total_referrals):
    proxy = get_random_proxy(proxies)
    proxy_dict = {"http": proxy, "https": proxy} if proxy else None
    
    while True:
        email = generate_email(proxy_dict)
        if not email:
            print(f"{get_log_prefix(account_num, total_referrals)} {Fore.LIGHTRED_EX}Failed to generate email. Retrying...{Style.RESET_ALL}")
            time.sleep(2)
            continue

        password = generate_password()
        print(f"{get_log_prefix(account_num, total_referrals)} {Fore.LIGHTYELLOW_EX}Email: {email}{Style.RESET_ALL}")
        print(f"{get_log_prefix(account_num, total_referrals)} {Fore.LIGHTYELLOW_EX}Password: {password}{Style.RESET_ALL}")

        otp_result = send_otp(email, password, proxy_dict, account_num, total_referrals)
        if not otp_result:
            time.sleep(2)
            continue

        id_token = otp_result.get("idToken")
        if not id_token:
            print(f"{get_log_prefix(account_num, total_referrals)} {Fore.LIGHTRED_EX}No ID token received{Style.RESET_ALL}")
            time.sleep(2)
            continue

        login_result = login(id_token, proxy_dict, account_num, total_referrals)
        if not login_result:
            time.sleep(2)
            continue

        if referral_code.strip():
            if not set_reff(referral_code, id_token, proxy_dict, account_num, total_referrals):
                time.sleep(2)
                continue

        save_account(email, password, account_num, total_referrals)
        return True

def main():
    print_banner()
    print(f"{Fore.LIGHTCYAN_EX}Use this script at your own risk!{Style.RESET_ALL}")
    proxies = load_proxies('proxies.txt')
    
    referral_code = ""
    while not referral_code.strip():
        referral_code = input(f"{Fore.LIGHTCYAN_EX}Enter referral code: {Style.RESET_ALL}")
        if not referral_code.strip():
            print(f"{Fore.LIGHTRED_EX}Referral code is required! Please enter a valid code.{Style.RESET_ALL}")
    
    total_referrals = 0
    while total_referrals <= 0:
        try:
            total_referrals = int(input(f"{Fore.LIGHTCYAN_EX}Enter total referrals: {Style.RESET_ALL}"))
            if total_referrals <= 0:
                print(f"{Fore.LIGHTRED_EX}Please enter a positive number!{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.LIGHTRED_EX}Please enter a valid number!{Style.RESET_ALL}")
    
    print(f"\n")
    
    attempt_count = 0
    current_account = 1
    
    while current_account <= total_referrals:
        attempt_count += 1
        print(f"{get_log_prefix(current_account, total_referrals)} {Fore.LIGHTCYAN_EX}{'='*50}{Style.RESET_ALL}")

        if process_single_registration(proxies, referral_code, current_account, total_referrals):
            current_account += 1
            
        time.sleep(5)
    
    print(f"\n{get_log_prefix()} {Fore.LIGHTGREEN_EX}All {total_referrals} referrals completed successfully!{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{get_log_prefix()} {Fore.LIGHTYELLOW_EX}Program terminated by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{get_log_prefix()} {Fore.LIGHTRED_EX}Unexpected error: {str(e)}{Style.RESET_ALL}")
