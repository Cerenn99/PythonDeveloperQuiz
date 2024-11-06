import re
import time
import paramiko


HOST = 'ssh_host_address'
PORT = 22
USERNAME = 'username'
PASSWORD = 'password'

dhcp_request_regex = r"OPTION: 53 \( 1\) DHCP message type 3 \(DHCPREQUEST\)"
client_id_regex = r"OPTION: 61 \( 7\) Client-identifier ([^\s]+)"
ip_address_regex = r"OPTION: 50 \( 4\) Request IP address ([^\s]+)"
vendor_class_regex = r"OPTION: 60 \( \d+\) Vendor class identifier ([^\s]+)"
host_name_regex = r"OPTION: 12 \( \d+\) Host name ([^\s]+)"

def parse_dhcp_data(data):
 
    client_id = re.search(client_id_regex, data)
    ip_address = re.search(ip_address_regex, data)
    vendor_class = re.search(vendor_class_regex, data)
    host_name = re.search(host_name_regex, data)
    
    
    client_id_value = client_id.group(1) if client_id else None
    ip_address_value = ip_address.group(1) if ip_address else None
    vendor_class_value = vendor_class.group(1) if vendor_class else None
    host_name_value = host_name.group(1) if host_name else None
    
    
    return {
        "Client-identifier": client_id_value,
        "Request IP address": ip_address_value,
        "Vendor class identifier": vendor_class_value,
        "Host name": host_name_value
    }

def save_to_file(parsed_data):
   
    with open('parsed_data.txt', 'a') as file:
        file.write(f"TIME: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        for key, value in parsed_data.items():
            file.write(f"{key}: {value if value else 'N/A'}\n")
        file.write("\n")

def listen_for_dhcp_requests():
  
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USERNAME, password=PASSWORD, port=PORT)

   
    stdin, stdout, stderr = ssh.exec_command("ssh_command")
    
    try:
        while True:
        
            data = stdout.readline()
            if data:
                if re.search(dhcp_request_regex, data):
                    parsed_data = parse_dhcp_data(data)
                    save_to_file(parsed_data)
            time.sleep(1)  
    except KeyboardInterrupt:
        print("Process is over.")
    finally:
        ssh.close()

if __name__ == "__main__":
    listen_for_dhcp_requests()
