    # gcs_uploader.py
    # A simple command-line tool to upload, download, list, and rename files in Google Cloud Storage.

    import os
    import argparse
    from google.cloud import storage
    from google.api_core import exceptions

    # --- KONFIGURASI UTAMA ---
    # Ganti nilai di bawah ini dengan nama bucket dan path ke file kunci JSON Anda.
    GCS_BUCKET_NAME = 'ganti-dengan-nama-bucket-anda'
    GCS_KEYFILE_PATH = 'ganti-dengan-path-keyfile-anda.json'
    # -------------------------

    # --- UTILITY FUNCTION TO GET THE CLIENT ---
    def get_storage_client(key_file_path: str):
        """Authenticates with GCP and returns a storage client object."""
        if not os.path.exists(key_file_path):
            print(f"❌ Error: Service account key file not found at '{key_file_path}'")
            return None
        try:
            return storage.Client.from_service_account_json(key_file_path)
        except Exception as e:
            print(f"❌ Error: Failed to create storage client. Check your key file. Details: {e}")
            return None

    # --- CORE FUNCTIONS ---

    def list_files_in_gcs(key_file_path: str, bucket_name: str):
        """Lists all the files in the specified GCS bucket."""
        storage_client = get_storage_client(key_file_path)
        if not storage_client:
            return

        print(f"📄 Fetching file list from bucket '{bucket_name}'...")
        try:
            blobs = storage_client.list_blobs(bucket_name)
            file_list = [blob.name for blob in blobs]

            if not file_list:
                print("Bucket is empty or does not exist.")
            else:
                print("--- Files in bucket ---")
                for file_name in file_list:
                    print(f"- {file_name}")
                print("-----------------------")

        except exceptions.Forbidden:
            print(f"❌ Error: Permission denied. Ensure your service account has the 'Storage Object Viewer' or 'Storage Object Admin' role on the bucket '{bucket_name}'.")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")


    def upload_to_gcs(key_file_path: str, bucket_name: str, source_file_path: str, destination_blob_name: str):
        """Uploads a file to the specified GCS bucket."""
        if not os.path.exists(source_file_path):
            print(f"❌ Error: Source file not found at '{source_file_path}'")
            return

        storage_client = get_storage_client(key_file_path)
        if not storage_client:
            return

        try:
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)

            print(f"⏳ Uploading '{source_file_path}' to bucket '{bucket_name}' as '{destination_blob_name}'...")
            blob.upload_from_filename(source_file_path)

            public_url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
            print("\n✅ Success! File uploaded.")
            print(f"🔗 Public URL: {public_url}")

        except exceptions.NotFound:
            print(f"❌ Error: Bucket '{bucket_name}' not found.")
        except exceptions.Forbidden as e:
            print(f"❌ Error: Permission denied. Ensure your service account has the 'Storage Object Admin' or 'Storage Object Creator' role on the bucket '{bucket_name}'. Details: {e}")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")

    def download_from_gcs(key_file_path: str, bucket_name: str, source_blob_name: str, destination_file_path: str):
        """Downloads a file from the specified GCS bucket."""
        storage_client = get_storage_client(key_file_path)
        if not storage_client:
            return

        try:
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)

            if not blob.exists():
                print(f"❌ Error: File '{source_blob_name}' not found in bucket '{bucket_name}'.")
                return

            print(f"⏳ Downloading '{source_blob_name}' from bucket '{bucket_name}' to '{destination_file_path}'...")
            blob.download_to_filename(destination_file_path)
            print(f"\n✅ Success! File downloaded to '{destination_file_path}'.")

        except exceptions.NotFound:
            print(f"❌ Error: Bucket '{bucket_name}' not found.")
        except exceptions.Forbidden as e:
            print(f"❌ Error: Permission denied. Ensure your service account has the 'Storage Object Viewer' or 'Storage Object Admin' role on the bucket '{bucket_name}'. Details: {e}")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")

    def rename_gcs_file(key_file_path: str, bucket_name: str, blob_name: str, new_blob_name: str):
        """Renames a file in the specified GCS bucket by copying and deleting."""
        storage_client = get_storage_client(key_file_path)
        if not storage_client:
            return

        try:
            bucket = storage_client.bucket(bucket_name)
            source_blob = bucket.blob(blob_name)

            if not source_blob.exists():
                print(f"❌ Error: Source file '{blob_name}' not found in bucket '{bucket_name}'.")
                return

            print(f"⏳ Renaming '{blob_name}' to '{new_blob_name}' in bucket '{bucket_name}'...")
            
            # Copy the blob to a new destination with the new name
            bucket.copy_blob(source_blob, bucket, new_blob_name)
            
            # Delete the original blob
            source_blob.delete()

            print(f"\n✅ Success! File renamed to '{new_blob_name}'.")

        except exceptions.NotFound:
            print(f"❌ Error: Bucket '{bucket_name}' not found.")
        except exceptions.Forbidden as e:
            print(f"❌ Error: Permission denied. Ensure your service account has the 'Storage Object Admin' role on the bucket '{bucket_name}'. Details: {e}")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")


    if __name__ == "__main__":
        # --- Main Argument Parser ---
        parser = argparse.ArgumentParser(
            description="A CLI tool to manage files in Google Cloud Storage.",
            formatter_class=argparse.RawTextHelpFormatter
        )
        subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

        # --- Parser for the "list" command ---
        parser_list = subparsers.add_parser("list", help="List all files in a bucket.")

        # --- Parser for the "upload" command ---
        parser_upload = subparsers.add_parser("upload", help="Upload a file to a bucket.")
        parser_upload.add_argument("source_file", help="The local path of the file to upload.")
        parser_upload.add_argument("destination_name", help="The name to give the uploaded file in the bucket.")

        # --- Parser for the "download" command ---
        parser_download = subparsers.add_parser("download", help="Download a file from a bucket.")
        parser_download.add_argument("source_name", help="The name of the file in the bucket to download.")
        parser_download.add_argument("destination_file", help="The local path to save the downloaded file.")

        # --- Parser for the "rename" command ---
        parser_rename = subparsers.add_parser("rename", help="Rename a file in a bucket.")
        parser_rename.add_argument("source_name", help="The current name of the file in the bucket.")
        parser_rename.add_argument("new_name", help="The new name for the file in the bucket.")

        # --- Execute the corresponding function based on the command ---
        args = parser.parse_args()
        
        # Validasi bahwa konfigurasi telah diisi
        if GCS_BUCKET_NAME == 'ganti-dengan-nama-bucket-anda' or GCS_KEYFILE_PATH == 'ganti-dengan-path-keyfile-anda.json':
            print("✋ Please configure GCS_BUCKET_NAME and GCS_KEYFILE_PATH inside the script before running.")
        elif args.command == "list":
            list_files_in_gcs(GCS_KEYFILE_PATH, GCS_BUCKET_NAME)
        elif args.command == "upload":
            upload_to_gcs(GCS_KEYFILE_PATH, GCS_BUCKET_NAME, args.source_file, args.destination_name)
        elif args.command == "download":
            download_from_gcs(GCS_KEYFILE_PATH, GCS_BUCKET_NAME, args.source_name, args.destination_file)
        elif args.command == "rename":
            rename_gcs_file(GCS_KEYFILE_PATH, GCS_BUCKET_NAME, args.source_name, args.new_name)

