import boto3
import os
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

#Load in AWS Access Key from dotenv
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

#AWS DynamoDB Setup
dynamodb = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-west-1')
db = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-west-1')
tables = {"contestants": db.Table('CONTESTANTS'), "scoreboard": db.Table('SCOREBOARD')}

app = FastAPI()

@app.get("/")
def greetings():
    return {"Nathaniel Iskandar": "WDB Technical Interview"}

# POST /contestants/ - Register Contestant/Husband
@app.post("/contestants")
async def register_contestant(contestantName: str, husbandName: str, vocalRange: int,  location: int, background_tasks: BackgroundTasks) -> Dict[str, str]:
    '''Register a contestant and associate them with their husband. 
       Every contestant also has a "vocalRange" field (which represents how many meters their voice will go). 
       Lastly, the husband has a "location" which represents their distance (in meters) from the contestant zone.'''
    
    #Defining the structure for CONTESTANTS table
    #============================================
    item = {
        "contestantName": contestantName, #partition key
        "husbandName": husbandName,
        "vocalRange": vocalRange,
        "location": location
    }

    table = tables['contestants']
    response1 = table.put_item(Item = item)



    #Defining the structure for SCOREBOARD Table
    #===========================================
    if vocalRange == location:
        score = location
    elif vocalRange > location:
        score = vocalRange - location
    else:
        score = -1
    

    item = {
        "score": score, #partition key
        "contestantName": contestantName #sort key
    }

    table = tables['scoreboard']
    response2 = table.put_item(Item = item)


    if response1['ResponseMetadata']['HTTPStatusCode'] == 200 and response2['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f"Item added to the database successfully")
        return {"status" : "Item added to the database successfully"}
    else:
        print("Error adding item to the database")
        return {"status" : "Error adding item to the database"}
    #background_tasks.add_task(create_new_contestant, contestantName, husbandName, vocalRange, location)
    #return {"status": "New Role written to the database"}
    
# GET /contestants - Get all contestants
@app.get("/contestants/")
async def get_contestants(sorted_by_name: bool = Query(default=False)):
    '''Return a list of all Contestants and the husband they are paired with'''
    
    table = tables["contestants"]

    response = table.scan(
        ProjectionExpression="contestantName, husbandName"
    )

    items = response.get("Items", [])

    if sorted_by_name:
        items = sorted(items, key=lambda item: item.get("contestantName", ""))

    pairs = [{"contestantName": item["contestantName"], "husbandName": item["husbandName"]} for item in items]

    return {"pairs": pairs}

# GET /husbandCall/{contestantName} - Perform Husband Call and Score It
@app.get("/husbandCall/{contestantName}/")
async def husband_call_and_score(contestantName: str):
    '''We determine the score of a husband call based on the husband's location and the contestant's vocalRange. 
       If the vocalRange is exactly equal to the location, the score is equal to the location. 
       If the vocal range is greater, the score is the absolute difference between the location and the vocalRange. 
       In both these cases, return the score.
       If the vocalRange is less, we should raise an error with a descriptive message.'''
    
    table = tables["contestants"]

    response = table.get_item(
        Key={"contestantName": contestantName},
        ProjectionExpression="#loc, vocalRange",   #"location" is a reserved word for ProjectionExpression, so we use an alias called "#loc"
        ExpressionAttributeNames={"#loc": "location"}  #Using ExpressionAttributeNames to make the alias
    )

    item = response.get('Item')

    if not item:
        raise HTTPException(status_code=404, detail="Contestant not found")

    location_attr = item.get('location')
    vocalRange_attr = item.get('vocalRange')

    if vocalRange_attr == location_attr:
        return {"score": location_attr}
    elif vocalRange_attr > location_attr:
        return {"score": vocalRange_attr - location_attr}
    else:
        raise HTTPException(status_code=400, detail="vocalRange is less than location")
    

#GET /bestShout - Get Highest Score Shout
@app.get("/bestShout")
def get_highest_score_shout():
    table = tables["scoreboard"]

    response = table.scan(
        ProjectionExpression="score, contestantName"
    )

    items = response.get("Items", [])

    if not items:
        return {"message": "No shouts in the scoreboard"}

    #ASSUMPTION: NO TIES
    highest_score = max(items, key=lambda item: item.get("score", 0))
    return {
        "score": highest_score.get("score", ""),
        "contestantName": highest_score.get("contestantName", ""),
    }


