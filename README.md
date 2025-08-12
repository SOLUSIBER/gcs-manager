# gcs-manager
1. Install python3 and pip
```
sudo apt install python3 python3-pip python3-venv
```

2. Buat virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

3. Install library google cloud storage
```
pip install google-cloud-storage
```

4. Jalankan script python
```
ubuntu@tuneful-glassfish:~$ python3 gcsmanager.py -h
usage: gcs_tools.py [-h] {list,upload,download,rename} ...

A CLI tool to manage files in Google Cloud Storage.

positional arguments:
  {list,upload,download,rename}
                        Available commands
    list                List all files in a bucket.
    upload              Upload a file to a bucket.
    download            Download a file from a bucket.
    rename              Rename a file in a bucket.

options:
  -h, --help            show this help message and exit
```
