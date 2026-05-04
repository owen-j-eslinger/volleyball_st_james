# volleyball_st_james
For processing data on the AES Event System website

## Environment Preparation
Ensure that you have Python 3.x installed along with the necessary data manipulation and geocoding libraries. You can install the dependencies via pip using the following command:

```bash```
pip install pandas geopy

## Steps

### Raw Data Placement

Place all raw tournament event JSON files into the source directory. 

- **Run This:**
    - Get_Owen.ipynb
- **Files Altered:** 
    - Data/raw/events/
- **To Know:** 
    - Will download and store JSON files that will be stored in this directory.
    - Naming convention is {event_id}.json
    
### Raw Data Processing - Events

The script is configured to iterate through every .json file found in this path:
- **Path:**
    - Data/raw/events/
- **Files Altered:** 
- **To Know:** 
    - Will download and store JSON files that will be stored in this directory.
    - Naming convention is {event_id}.json
