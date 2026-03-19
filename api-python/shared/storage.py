import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

# Azure Storage connection - should be in Key Vault in production
STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', '')
CONTAINER_NAME = 'case-attachments'

def get_blob_service_client():
    """Get Azure Blob Storage client."""
    return BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

def upload_file(file_data: bytes, file_name: str, user_id: str) -> str:
    """Upload a file to blob storage and return its URL."""
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # Create container if it doesn't exist
    try:
        container_client.create_container()
    except:
        pass  # Container already exists

    # Create blob path: user_id/file_name
    blob_name = f"{user_id}/{file_name}"
    blob_client = container_client.get_blob_client(blob_name)

    # Upload file
    blob_client.upload_blob(file_data, overwrite=True)

    # Return blob URL
    return blob_client.url

def delete_file(blob_url: str) -> bool:
    """Delete a file from blob storage."""
    try:
        blob_service_client = get_blob_service_client()
        # Extract blob name from URL
        blob_name = blob_url.split(f"{CONTAINER_NAME}/")[1]
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
        return True
    except:
        return False

def generate_sas_url(blob_url: str, expiry_hours: int = 1) -> str:
    """Generate a SAS URL for secure file access."""
    blob_service_client = get_blob_service_client()
    blob_name = blob_url.split(f"{CONTAINER_NAME}/")[1]

    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=CONTAINER_NAME,
        blob_name=blob_name,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
    )

    return f"{blob_url}?{sas_token}"
