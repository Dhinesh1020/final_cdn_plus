from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from cdn_plus.models import DBTable, Inventory, Cname
from django.contrib import messages
from .forms import CdnForm
from django.views import View
from django.shortcuts import render
from vendors.cloudfront.distribution import Cloudfront
from vendor_config import vendor_config
from .serializers import CnameSerializer
from vendors.dns.go_daddy import GoDaddy
import datetime
from django.utils import timezone
import random
import string
import os
import json

# Create your views here.

Cloudfront_object = Cloudfront(vendor_config["cloudfront"]["aws_access_key"],
                               vendor_config["cloudfront"]["aws_secret_access_key"],
                               vendor_config["cloudfront"]["aws_region"]
                               )

def members(request):
    users = DBTable.objects.all().values()
    template = loader.get_template('allMembers.html')
    
    context = {
        "mymembers": users
    }
    return HttpResponse(template.render(context, request))

def cdn_discovery():
    try:
        cloudfront_response = Cloudfront_object.fetch_all_distributions()
        # clear old model data,
        Inventory.objects.all().delete()        
        if cloudfront_response:
            for distribution in cloudfront_response:
                price_class = distribution.get("PriceClass","")
                price_class_region_map = {
                    "PriceClass_All":["North America", "Europe", "Israel", "South Africa", "Kenya", "MiddleEast", "South America", "Japan", "Australia", "New Zealand", "Hong Kong", "Indonesia", "Philippines", "Singapore", "South Korea", "Taiwan", "Thailand", "India"],
                    "PriceClass_100":["North America", "Europe", "Israel", "South Africa", "Kenya", "MiddleEast", "Japan", "Hong Kong", "Indonesia", "Philippines", "Singapore", "South Korea", "Taiwan", "Thailand", "India"],
                    "PriceClass_200":["North America", "Europe", "Israel"]
                    }
                regions = price_class_region_map[str(price_class)]
                regions = ", ".join(regions)
                inventory_object = Inventory(
                    id=distribution.get("Id",""),
                    vendor="CloudFront",
                    description=distribution.get("Comment",""),
                    domain_name=distribution.get("DomainName",""),
                    regions=regions,
                    origins=distribution["Origins"]["Items"][0].get("DomainName",""),
                    state=distribution.get("State",""),
                    status=distribution.get("Status",""),
                    last_modified=distribution["LastModifiedTime"],
                )
                inventory_object.save()
        else:
            inventory_object = Inventory(
                id="",
                vendor="",
                description="",
                domain_name="",
                regions="",
                origins="",
                state="",
                status="",
                last_modified="",
            )
            inventory_object.save()

        # Azure CDN Dummy Data
        azure_response = [
            {
                "vendor": "Azure",
                "domain_name": "tutorialspoint.azureedge.net",
                "origins": "www.tutorialspoint.org",
                "state": "Enabled",
                "status": "Deployed",
                "last_modified": datetime.date(2023, 4, 6)
            },
            {
                "vendor": "Azure",
                "domain_name": "fiserv.azureedge.net",
                "origins": "www.fiserv.com/en-in",
                "state": "Disabled",
                "status": "Deployed",
                "last_modified": datetime.date(2022, 8, 24)
            }
        ]
        for distribution in azure_response:
            inventory_object = Inventory(
                id=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(14)),
                vendor=distribution["vendor"],
                description="RANDOM",
                domain_name=distribution["domain_name"],
                regions="North America, Europe, Israel",
                origins=distribution["origins"],
                state=distribution["state"],
                status=distribution["status"],
                last_modified=distribution["last_modified"]
                )
            inventory_object.save()
        return "CDN Inventory DB Sync Successfull."                        
    except Exception as error:
        return f"DB Sync failed due to error : {error}"
    
def inventory(request):
    db_sync_status = cdn_discovery() # db sync
    data = Inventory.objects.all().values()
    return render(request, "inventory_page.html", {'data': data})

def add_distribution(request):
    
    query_params = request.GET.dict()
    
    if request.method == "POST":       
        origin_source = request.POST.get("origin_source")
        origin_name = request.POST.get("origin_name")
        origin_domain = request.POST.get("origin_domain")
        allowed_http_methods = request.POST.get("allowed_http_methods")
        allowed_http_methods = allowed_http_methods.split(", ")
        price_class = request.POST.get("price_class")
        price_class_map = {
            "Use all edge locations (best performance)":"PriceClass_All",
            "Use North America, Europe, Asia, Middle East, and Africa":"PriceClass_100",
            "Use only North America and Europe":"PriceClass_200"
        }
        price_class_tag = price_class_map[str(price_class)]
        supported_http_versions = request.POST.getlist('supported_http_versions[]')
        cache_policy = request.POST.get("cache_policy")
        if cache_policy == "assign_cache_policy":
            cache_policy_set = request.POST.get("cache_policy_set")
            cloudfront_response_status, cloudfront_response = Cloudfront_object.create_distribution(
                origin_source=origin_source, 
                origin_name=origin_name, 
                origin_domain=origin_domain,
                allowed_http_methods=allowed_http_methods,
                price_class=price_class_tag,                
                supported_http_versions=supported_http_versions,
                cache_policy=cache_policy_set
                )            
        else:
            default_ttl = int(request.POST.get("default_ttl")) if request.POST.get("default_ttl") else 60
            min_ttl = int(request.POST.get("min_ttl")) if request.POST.get("min_ttl") else 30
            max_ttl = int(request.POST.get("max_ttl")) if request.POST.get("max_ttl") else 90
            cloudfront_response_status, cloudfront_response = Cloudfront_object.create_distribution(
                origin_source=origin_source, 
                origin_name=origin_name, 
                origin_domain=origin_domain,
                allowed_http_methods=allowed_http_methods,
                price_class=price_class_tag,                
                supported_http_versions=supported_http_versions,
                default_ttl=default_ttl,
                min_ttl=min_ttl,
                max_ttl=max_ttl
                )  
            
        if cloudfront_response_status:
            price_class = cloudfront_response["Distribution"]["DistributionConfig"]["PriceClass"]
            price_class_region_map = {
                "PriceClass_All":["North America", "Europe", "Israel", "South Africa", "Kenya", "MiddleEast", "South America", "Japan", "Australia", "New Zealand", "Hong Kong", "Indonesia", "Philippines", "Singapore", "South Korea", "Taiwan", "Thailand", "India"],
                "PriceClass_100":["North America", "Europe", "Israel", "South Africa", "Kenya", "MiddleEast", "Japan", "Hong Kong", "Indonesia", "Philippines", "Singapore", "South Korea", "Taiwan", "Thailand", "India"],
                "PriceClass_200":["North America", "Europe", "Israel"]
                }             
            # db sync        
            inventory_object = Inventory(id=cloudfront_response["Distribution"]["Id"],
                                vendor="CloudFront",
                                description=cloudfront_response["Distribution"]["DistributionConfig"]["Comment"],
                                domain_name=cloudfront_response["Distribution"]["DomainName"],
                                regions=price_class_region_map[str(price_class)],
                                origins=cloudfront_response["Distribution"]["DistributionConfig"]["Origins"]["Items"][0]["DomainName"],
                                state=Cloudfront_object.fetch_distribution_state_by_domain(cloudfront_response["Distribution"]["DomainName"]),
                                status=cloudfront_response["Distribution"]["Status"],
                                last_modified=cloudfront_response["Distribution"]["LastModifiedTime"]
                            )
            inventory_object.save()

    # Pass each query parameter separately to the template context
    context = {
        **query_params,
    }

    return render(request,"add_distribution.html", context)

def enable_distribution(request, domain_name):
    cloudfront_response, msg = Cloudfront_object.enable_distribution_by_domain(domain_name=domain_name)
    if cloudfront_response:
        db_sync_status = cdn_discovery() # db sync
        return redirect('inventory')
    else:
        return render(request, 'inventory_page.html', {'alert_message': msg})
    
def domain_name_region_link(domain_name):
    try:
        InventoryData = Inventory.objects.get(domain_name=domain_name)
        region_associated_str = InventoryData.regions
        return region_associated_str.split(", ")
    except Inventory.DoesNotExist:
        return []
    
def get_distribution_by_domain(domain_name):
    try:
        InventoryData = Inventory.objects.get(domain_name=domain_name)
        return InventoryData.id
    except Inventory.DoesNotExist:
        return False
    
def show_map(request, domain_name):
    template = loader.get_template('map.html')

    if not domain_name:
        return HttpResponse(template.render())
    
    regions_mapped = domain_name_region_link(domain_name=domain_name)

    page_data = []
    region_marker_mapping = {
                                "Europe": "marker-eur", 
                                "Australia": "marker-au", 
                                "South Africa": "marker-sa", 
                                "MiddleEast": "marker-me",
                                "North America": "marker-usa",
                                "India": "marker-in"
                                }
    for each_region in regions_mapped:

        if region_marker_mapping.get(each_region.strip()):
            temp_dict = {}
            temp_dict['marker'] = region_marker_mapping.get(each_region.strip())
            temp_dict['domain_name'] = domain_name
            page_data.append(temp_dict)

    # page_data = [{"marker":"marker-usa", "domain_name":domain_name}]
    context = {
        "data": page_data
    }
    print(page_data)
    return HttpResponse(template.render(context, request))

def disable_distribution(request, domain_name):  
    cloudfront_response, msg = Cloudfront_object.disable_distribution_by_domain(domain_name=domain_name)
    if cloudfront_response:
        db_sync_status = cdn_discovery() # db sync
        return redirect('inventory')
    else:
        return render(request, 'inventory_page.html', {'alert_message': msg})

def delete_distribution(request, domain_name):       
    cloudfront_response, msg = Cloudfront_object.delete_distribution_by_domain(domain_name=domain_name)
    if cloudfront_response:
        db_sync_status = cdn_discovery() # db sync
        return redirect('inventory')
    else:        
        return render(request, 'inventory_page.html', {'alert_message': msg})

def multi_form(request):
    # users = DBTable.objects.all().values()
    template = loader.get_template('tab_form.html')
    
    return HttpResponse(template.render())

def dashboard(request):
    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render())

def cdn_inventory(request):
    template = loader.get_template('cdn_inventory_vendors.html')
    return HttpResponse(template.render())

def dns(request):
    users = DBTable.objects.all().values()
    template = loader.get_template('dns.html')
    
    context = {
        "mymembers": users
    }
    return HttpResponse(template.render(context, request))

def edit_item(request, firstName):
    messages.success(request, 'Item edited successfully.')
    content = '<p>dummy content</p>'
    return HttpResponse(content)

def delete_item(request, firstName):
    messages.success(request, 'Item deleted successfully.')
    content = '<p>dummy content</p>'
    return HttpResponse(content)

class DistributionView(View):
    template_name = 'distribution_form.html'

    def get(self, request, *args, **kwargs):
        form = CdnForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CdnForm(request.POST)
        print('Got the form')
        if form.is_valid():
            print('Processing the form')
            # Process the form data here
            aws_access_key = form.cleaned_data['aws_access_key']
            aws_secret_access_key = form.cleaned_data['aws_secret_access_key']
            aws_region = form.cleaned_data['aws_region']

            vendor_config = {
                "vendor_config": {
                    "cloudfront": {
                        "aws_access_key": aws_access_key,
                        "aws_secret_access_key": aws_secret_access_key,
                        "aws_region": aws_region
                    }
                }
            }
            current_path = os.getcwd()
            file_path = os.path.join(current_path, 'vendor_config.json')

            with open(file_path, 'w') as fw:
                fw.write(json.dumps(vendor_config, indent=4))
            # You can perform further actions here, such as saving to the database
            # For demonstration purposes, let's just print the data
            print(f"Name: {aws_access_key}, Email: {aws_secret_access_key}, Message: {aws_region}")

            messages.success(request, 'Form submitted successfully.')
            return redirect('distribution')

        return render(request, self.template_name, {'form': form})

def fetch_dns():
    # Fetch data from GoDaddy DNS
    go_daddy_dns = GoDaddy()  # Replace with the actual initialization logic
    cname_records = go_daddy_dns.get_cname_list_all()

    # Process and create Cname entries
    for cname_data in cname_records:
        cname = cname_data['cname']
        associated_distribution = get_distribution_by_domain(cname)
        if associated_distribution:
            cname_data['associated_distribution'] = "Available"
        serializer = CnameSerializer(data=cname_data)
        if serializer.is_valid():
            # Save the data to the Cname model
            Cname.objects.create(**serializer.validated_data)

    return True

def dns_table_data(request):
    Cname.objects.all().delete()
    sync_the_data = fetch_dns()

    cname_objects = Cname.objects.all().values()
    template = loader.get_template('dns.html')
    context = {
        "cname_objects": cname_objects
    }
    return HttpResponse(template.render(context, request))

def insights_base(request):
    template = loader.get_template('insights_base.html')
    return HttpResponse(template.render())

def insight_usage(request):
    template = loader.get_template('insight_usage.html')
    return HttpResponse(template.render())

def insight_monitoring(request):
    template = loader.get_template('insight_monitoring.html')
    return HttpResponse(template.render())

def insight_stats(request):
    template = loader.get_template('insight_cache_statistics.html')
    return HttpResponse(template.render())
