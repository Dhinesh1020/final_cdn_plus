import urllib3
import json

api_key = "3mM44UcgD6yfqn_X6qwSbHkxm7caenHceRU4g"
api_secret = "GAcsmAsYx9WKAqUEgcbMdv"
# customer_id = "your_customer_id"

def api_request(endpoint, method="GET", data=None, additional_headers=None):
    base_url = "https://api.ote-godaddy.com/v1/"
    url = f"{base_url}{endpoint}"

    generic_headers = {
        # "X-Shopper-Id": customer_id,
        "Content-Type": "application/json",
        "Authorization": f"sso-key {api_key}:{api_secret}",
    }

    headers = generic_headers.copy()

    if additional_headers:
        headers.update(additional_headers)

    http = urllib3.PoolManager()

    try:
        if method == "GET":
            response = http.request(method, url, headers=headers)
        elif method == "POST":
            encoded_data = json.dumps(data).encode("utf-8")
            response = http.request(method, url, headers=headers, body=encoded_data)
        # Add more methods if needed (e.g., PUT, DELETE)
        if response.status == 200:
            return json.loads(response.data.decode("utf-8"))
        else:
            print(f"Error: {response.status}, {response.data}")
            return None
    except urllib3.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        return None


class GoDaddy:
    def __init__(self):
        pass
    
    def get_domains(self):
        endpoint = "domains/"
        specific_headers = {}
        return api_request(endpoint, additional_headers=specific_headers)

    def get_domains_list(self):
        domains_list = []
        domains_data = self.get_domains()
        return [domain.get("domain") for domain in domains_data]
        
    
    def get_domain_details(self, domain_name):
        endpoint = f"domains/{domain_name}"
        specific_headers = {}
        return api_request(endpoint, additional_headers=specific_headers)
    
    def get_domain_cname_details(self, domain_name):
        endpoint = f"domains/{domain_name}/records/CNAME"
        specific_headers = {}
        return api_request(endpoint, additional_headers=specific_headers)
    
    def get_cname_list_by_domain_name(self, domain_name):
        # import pdb;pdb.set_trace()
        cname_data = self.get_domain_cname_details(domain_name)
        # Check if cname_data is not None before accessing its elements
        cname_list = []
        if cname_data:
            # Use list comprehension to create the list, filtering out None values
            for cname in cname_data:
                cname["domain"] = domain_name
                cname["alias"] = cname["name"]
                cname['cname'] = cname["data"]
                cname.pop("name")
                cname.pop("data")
                cname.pop("type")
                cname_list.append(cname)
            return cname_list
        else:
            # Handle the case where cname_data is None (e.g., return an empty list)
            return []

    def get_cname_list_all(self):
        all_cname_list = []
        domain_list = self.get_domains_list()
        for domain_name in domain_list[:2]:
            cname_list = self.get_cname_list_by_domain_name(domain_name)
            all_cname_list.extend(cname_list)
        return list(all_cname_list)
        
        

# go_daddy = GoDaddy()
# get_all_domains = go_daddy.get_domains()
# get_domain_details = go_daddy.get_domain_details(domain_name="akamaiddidemotest301.net")
# get_domain_cname_details = go_daddy.get_domain_cname_details(domain_name="akamaiddidemotest301.net")
# get_domains_list = go_daddy.get_domains_list()
# get_cname_list_by_domain_name = go_daddy.get_cname_list_by_domain_name("akamaiddidemotest301.net")
# get_cname_list_all = go_daddy.get_cname_list_all()
# print("exit")
