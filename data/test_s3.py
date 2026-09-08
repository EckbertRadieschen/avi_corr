import boto3
from dotenv import load_dotenv

load_dotenv()
AWS_REGION = "us-west-2"
AWS_BUCKET = "usgs-landcover"

KEY = (
    "annual-nlcd/c1/v2/cu/tile/h19v14/"
    "Annual_NLCD_H19V14_LndCov_1985_CU_C1V2.tif"
)

s3 = boto3.client("s3", region_name=AWS_REGION)

response = s3.get_object(
    Bucket=AWS_BUCKET,
    Key=KEY,
    RequestPayer="requester"
)

print("GET erfolgreich")
print(response["ContentLength"])