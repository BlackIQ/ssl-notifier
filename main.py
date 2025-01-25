import os
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import requests

SSL_DIR = "./ssl"

bot_token = "8004860601:AAEMpaK6oT_Z27Od9fyzAJkb7RGAELgONeE"
chat_ids = [
    # -1002372829101, # NOC Organization
    # -4040648190, # DEV Organization
    -4699216187, # NOC Amir
]

def send_message(message, chat_id):        
    data = {
        "chat_id": chat_id,
        "text": message
    }

    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage", data=data)
    
results = [
    "🐳 SSL Notifier",
    "",
    "Hi 👋, let's review SSLs expirations",
    ""
]

def check_ssl_expiration(domain):
    cert_path = os.path.join(SSL_DIR, domain, "fullchain.pem")
        
    if not os.path.exists(cert_path):
        results.append(f"[#WARNING] Certificate file not found for domain: {domain}")
        return
    
    try:
        with open(cert_path, "rb") as cert_file:
            cert_data = cert_file.read()
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            expiration_date = cert.not_valid_after_utc
            days_to_expire = (expiration_date - datetime.now().astimezone(expiration_date.tzinfo)).days
            
            if days_to_expire <= 5:
                results.append(f"[#ALERT] SSL certificate for {domain} is expiring in {days_to_expire} days!")
            else:
                results.append(f"Certificate for {domain} is valid for {days_to_expire} more days.")
    except Exception as e:
        results.append(f"[#ERROR] Failed to process certificate for domain {domain}: {e}")
        
if __name__ == "__main__":
    domains = [d for d in os.listdir(SSL_DIR) if os.path.isdir(os.path.join(SSL_DIR, d))]

    for domain in domains:
        check_ssl_expiration(domain)

    message = "\n".join(results)
    
    for chatid in chat_ids:
        send_message(message, chatid)