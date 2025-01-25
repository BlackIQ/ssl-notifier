import os
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from termcolor import colored

SSL_DIR = "/app/ssl" # In Docker Container
# SSL_DIR = "./ssl" # In Local Development

def check_ssl_expiration(domain):
    cert_path = os.path.join(SSL_DIR, domain, "fullchain.pem")
    
    if not os.path.exists(cert_path):
        print(f"[WARNING] Certificate file not found for domain: {domain}")
        return
    
    try:
        with open(cert_path, "rb") as cert_file:
            cert_data = cert_file.read()
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            expiration_date = cert.not_valid_after_utc
            days_to_expire = (expiration_date - datetime.now().astimezone(expiration_date.tzinfo)).days
            
            if days_to_expire <= 5:
                print(colored(f"[ALERT] SSL certificate for {domain} is expiring in {days_to_expire} days!", "red"))
            elif 10 >= days_to_expire > 5:
                print(colored(f"SSL certificate for {domain} is expiring in {days_to_expire} days.", "yellow"))
            else:
                print(colored(f"SSL certificate for {domain} is valid for {days_to_expire} more days.", "green"))
    except Exception as e:
        print(f"[ERROR] Failed to process certificate for domain {domain}: {e}")

if __name__ == "__main__":
    domains = [d for d in os.listdir(SSL_DIR) if os.path.isdir(os.path.join(SSL_DIR, d))]

    for domain in domains:
        check_ssl_expiration(domain)
