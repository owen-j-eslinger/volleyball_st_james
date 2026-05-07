# volleyball_st_james
For processing data on the AES Event System website

## Environment Preparation
Ensure that you have Python 3.x installed along with the necessary data manipulation and geocoding libraries. You can install the dependencies via pip using the following command:

```bash```
pip install pandas geopy
pip install thefuzz
pip install networkx pyvis


## Links
- https://www.advancedeventsystems.com/events
    - Find events through GUI
- https://www.advancedeventsystems.com/events/44496
    - Shows information about individual events (here EventID = 44496
- https://results.advancedeventsystems.com/event/PTAwMDAwNDEzNzk90/home
    - Results for a particular event
- https://advancedeventsystems.com/rankings/3472
    - Shows particular club
    https://advancedeventsystems.com/rank/185651

https://advancedeventsystems.com/api/ranking/185651

https://advancedeventsystems.com/api/ranking/185651/events

https://advancedeventsystems.com/api/ranking/185651/finishes

https://advancedeventsystems.com/api/ranking/185651/members

https://advancedeventsystems.com/api/ranking/185651/events/40917/matches

## Steps

### Raw Data Placement

Place all raw tournament event JSON files into the source directory. 

- Get_Owen.ipynb
- Data/raw/events/
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
