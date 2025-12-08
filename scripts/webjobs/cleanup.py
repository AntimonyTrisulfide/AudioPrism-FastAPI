import os, datetime
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

RETENTION_MIN = int(os.getenv("RETENTION_MINUTES", "120"))
ACCOUNT_URL = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER", "audio-stems")

credential = DefaultAzureCredential()
blob_service = BlobServiceClient(account_url=ACCOUNT_URL, credential=credential)
container_client = blob_service.get_container_client(CONTAINER)

def main():
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=RETENTION_MIN)
    deleted = 0
    for blob in container_client.list_blobs(include=["metadata"]):
        created = blob.metadata.get("created_at")
        created_dt = datetime.datetime.fromisoformat(created) if created else blob.last_modified.replace(tzinfo=None)
        if created_dt < cutoff:
            container_client.delete_blob(blob.name, delete_snapshots="include")
            deleted += 1
    print(f"Deleted {deleted} blobs older than {RETENTION_MIN} minutes")

if __name__ == "__main__":
    main()
