import os
from dotenv import load_dotenv

load_dotenv()

def get_formatted_cookies():
    """
    Reads the raw cookie string and domain from the environment,
    converts them into the JSON format required by Playwright,
    and returns the result as a Python list.
    """
    cookie_string = os.getenv("SESSION_COOKIES")
    domain = os.getenv("TARGET_DOMAIN")

    if not cookie_string or not domain:
        raise ValueError("SESSION_COOKIES or TARGET_DOMAIN not found in the .env file.")

    cookies_list = []
    for cookie_pair in cookie_string.split(';'):
        cookie_pair = cookie_pair.strip()
        if '=' in cookie_pair:
            name, value = cookie_pair.split('=', 1)
            cookies_list.append({
                "name": name,
                "value": value,
                "domain": domain,
                "path": "/"
            })
            
    return cookies_list

# print(get_formatted_cookies())