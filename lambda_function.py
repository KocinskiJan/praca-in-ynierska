import json
import subprocess
import boto3
import os
import tempfile
import logging
from pathlib import Path

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Initialize S3 client
s3 = boto3.client("s3")

# Allowed scripts for security
ALLOWED_SCRIPTS = ["inf.py", "lddt-lambda.py", "mcq.py", "rmsd.py", "tm_score_lambda.py", "torsion.py"]

# USalign path for AWS Lambda Layer
USALIGN_PATH = "/opt/bin/USalign"

def download_from_s3(bucket, key):
    """Downloads a file from S3 to a temporary location."""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        s3.download_file(bucket, key, temp_file.name)
        return temp_file.name
    except Exception as e:
        logger.error(f"Error downloading {key} from S3: {e}")
        return None

def run_script(script, pdb1, pdb2):
    try:
        script_path = f"/var/task/{script}"
        if not Path(script_path).is_file():
            return {"statusCode": 400, "error": f"Script {script} not found."}

        result = subprocess.run(
            ["/var/lang/bin/python3.12", script_path, pdb1, pdb2],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Log both stdout and stderr
        logger.info(f"[DEBUG] STDOUT for {script}:\n{result.stdout}")
        logger.error(f"[DEBUG] STDERR for {script}:\n{result.stderr}")

        if result.returncode != 0:
            return {"statusCode": 500, "error": f"Script {script} failed: {result.stderr.strip()}"}

        return {"statusCode": 200, "output": result.stdout.strip()}

    except Exception as e:
        logger.exception("Unexpected error during script run")
        return {"statusCode": 500, "error": str(e)}

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Obsługa różnych formatów wejściowych (API Gateway, lokalne testy itp.)
        if isinstance(event, dict):
            if "body" in event and isinstance(event["body"], str):
                body = json.loads(event["body"])
            else:
                body = event
        else:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Invalid event format."})
            }

        script = body.get("script")
        s3_bucket = body.get("s3_bucket")
        pdb1_key = body.get("pdb1_key")
        pdb2_key = body.get("pdb2_key")

        if not script or not s3_bucket or not pdb1_key or not pdb2_key:
            return {"statusCode": 400, "headers": {"Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": "Missing required parameters."})}

        if script not in ALLOWED_SCRIPTS:
            return {"statusCode": 400, "headers": {"Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": f"Invalid script: {script}. Allowed: {ALLOWED_SCRIPTS}"})}

        # Download PDB files from S3
        pdb1_path = download_from_s3(s3_bucket, pdb1_key)
        pdb2_path = download_from_s3(s3_bucket, pdb2_key)

        if not pdb1_path or not pdb2_path:
            return {"statusCode": 500, "headers": {"Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": "Failed to download files from S3."})}

        # Run script
        result = run_script(script, pdb1_path, pdb2_path)

        # Return API Gateway-compatible response
        return {
            "statusCode": result["statusCode"],
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps(result)
        }
    except Exception as e:
        logger.exception("Error in lambda_handler")
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
