# XtremIO Collector Script
Python code that queries a single XtremIO XMS to gather standard data about an XtremIO array.

Currently assumes a 1:1 relationship of XtremIO to XMS.

# Ways to run this code
### Stand-alone
./handler.py

*Ensure the following Env Vars are set*
- XMS_ADDRESS
- ARRAY_NAME
- USERNAME
- PASSWORD
- TARGET_API_URL

### Open FAAS
Once you have created a new python3 function, move the following files into the directory
- requirements.txt
- handler.py

The function is set to accept a json payload the looks like the below
```json
{"XMS_ADDRESS": "ip/dns", "ARRAY_NAME": "array_name", "USERNAME": "username", "PASSWORD": "password", "TARGET_API_URL": "https://api-endpoint.company.com"}
