from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError


def check_connection(ip,bucket,org,api_token):
    try:


        client = InfluxDBClient(url=f"http://{ip}:8086",token=api_token,org=org)
        orgs_api = client.organizations_api()
        organizations = orgs_api.find_organizations()

        # Check if the provided organization exists
        org_exists = any(o.name == org for o in organizations)
        if not org_exists:
            return False, f"Organization '{org}' does not exist."

        buckets_api = client.buckets_api()
        buckets = buckets_api.find_buckets().buckets


        if buckets:
            for b in buckets:
                if b.name == bucket:
                    return True, "Connected successfully to the database and bucket exists."
            return False, f"Bucket '{bucket}' does not exist in organization '{org}'."
        else:
            return False, "No buckets found. Check your organization name or permissions."

    except InfluxDBError as e:
        # Handle InfluxDB-specific errors
        return False, f"InfluxDB Error: {e}"
    except Exception as e:
        # Handle other unexpected exceptions
        return False, f"Connection failed: {e}"