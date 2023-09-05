import boto3
import os
from fastapi import FastAPI, HTTPException, Query, Request
from typing import Dict
from models import ContestantRegistration, PowerUpItem
from dotenv import load_dotenv
load_dotenv()

#Load in AWS Access Key from dotenv
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

#AWS DynamoDB Setup
dynamodb = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-west-1')
db = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-west-1')
tables = {"contestants": db.Table('CONTESTANTS')}

app = FastAPI()

@app.get("/")
def greetings():
    return {"Nathaniel Iskandar": "WDB Technical Interview Fall 2023"}

# POST /contestants/ - Register Contestant/Husband
@app.post("/contestants")
async def register_contestant(contestant: ContestantRegistration):
    '''Register a contestant and associate them with their husband. 
       Every contestant also has a "vocalRange" field (which represents how many meters their voice will go). 
       Lastly, the husband has a "location" which represents their distance (in meters) from the contestant zone.'''

    # Extract data from the "ContestantRegistration" BaseModel. 
    # Use BaseModel to use "Request Body (JSON)" instead of "Parameters"
    contestantName = contestant.contestantName
    husbandName = contestant.husbandName
    vocalRange = contestant.vocalRange
    location = contestant.location
    if vocalRange == location:
        score = location
    elif vocalRange > location:
        score = vocalRange - location
    else:
        score = -1

    #defining the structure of attributes for the 'CONTESTANT' table
    item = {
        "contestantName": contestantName, #partition key
        "husbandName": husbandName,
        "vocalRange": vocalRange,
        "location": location,
        "score": score
    }
    #Register the item to 'CONTESTANT' table
    table = tables['contestants']
    response = table.put_item(Item = item) 

    #Checks for Error
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f"Item added to the database successfully")
        return {"status" : "Item added to the database successfully"}
    else:
        print("Error adding item to the database")
        return {"status" : "Error adding item to the database"}
    
    
# GET /contestants - Get all contestants
@app.get("/contestants")
async def get_contestants(sortedByName: bool = Query(default=False)):
    '''Return a list of all Contestants and the husband they are paired with'''
    
    #Accesses the CONTESTANTS table using .scan() and queries the "contestantName" and "husbandCall" attributes
    table = tables["contestants"]
    response = table.scan(
        ProjectionExpression="contestantName, husbandName"
    )
    #Put the retrieved response object in a list
    items = response.get("Items", []) 

    #If sortedByName = true, use lambda function as the sorting key to sort the items list based on "contestantName" (ascending)
    if sortedByName:
        items = sorted(items, key=lambda item: item.get("contestantName", ""))
    pairs = [{"contestantName": item["contestantName"], "husbandName": item["husbandName"]} for item in items]
    return {"pairs": pairs}

# GET /husbandCall/{contestantName} - Perform Husband Call and Score It
@app.get("/husbandCall/{contestantName}")
async def husband_call_and_score(request: Request):
    '''We determine the score of a husband call based on the husband's location and the contestant's vocalRange. 
       If the vocalRange is exactly equal to the location, the score is equal to the location. 
       If the vocal range is greater, the score is the absolute difference between the location and the vocalRange. 
       In both these cases, return the score.
       If the vocalRange is less, we should raise an error with a descriptive message.'''
    
    #Extracts the "contestantName" from the URL
    contestant_name  = request.path_params.get("contestantName")

    #Accesses the CONTESTANTS table and queries the "score" attribute
    table = tables["contestants"]
    response = table.get_item(
        Key={"contestantName": contestant_name},
        ProjectionExpression="score",
    )
    item = response.get('Item')

    #Error check if contestant is not found
    if not item:
        raise HTTPException(status_code=404, detail="Contestant not found")

    #Extracts the "score" attribute and return the respective message
    score_attr = item.get('score')
    if score_attr == -1:
        raise HTTPException(status_code=400, detail="vocalRange is less than location")
    else:
        return {"score": score_attr}
    

#GET /bestShout - Get Highest Score Shout
@app.get("/bestShout")
def get_highest_score_shout():
    '''This route should return the score of the best shout across all contestants, as well as the contestant. 
        You can either assume no ties or break ties randomly, just make sure it is clear which option you go for.'''

    #Accesses the CONTESTANTS table using .scan() and queries the "contestantName" and "score" attributes
    table = tables["contestants"]
    response = table.scan(
        ProjectionExpression="contestantName, score"
    )
    #Put the retrieved response object in a list
    items = response.get("Items", [])

    #Error check if contestant is not found
    if not items:
        raise HTTPException(status_code=404, detail="Contestant not found")

    #===================
    #ASSUMPTION: NO TIES
    #===================

    #Use lambda function to extract the "score" value from each item. Use max() function to return the max value
    highest_score = max(items, key=lambda item: item.get("score", 0))
    return {
        "contestantName": highest_score.get("contestantName", ""),
        "score": highest_score.get("score", ""),
    }


#POST /buyItem/{contestantName} - Buy a Power-up Item
@app.post("/buyItem/{contestantName}") 
def buy_item(request: Request, powerup: PowerUpItem):
    '''Some contestants have said they want to be able to use the best and latest tech to improve their scores! 
        Implement an API route that lets contestants purchase an item and add it to their inventory. 
        The response should be a list of all the items in the user's inventory.
            - Each item has a "boost", which increases the vocalRange by that amount.
            - Items cannot be removed from the inventory.
            - All items in the inventory get used when a husbandCall is made.
        Note that completing this section will also involve modifying your existing husbandCall route!'''
    
    #Extracts the "contestantName" from the URL
    contestant_name  = request.path_params.get("contestantName")
    
    # Extract data from the "PowerUpItem" BaseModel. 
    # Use BaseModel to use "Request Body (JSON)" instead of "Parameters"
    item = powerup.item
    boost = powerup.boost
    

    #TASK 1: Modify the "VocalRange" and "Score" attribute
    #========================================================
    #get the "VocalRange" attribute from the CONTESTANT table
    table = tables["contestants"]
    response = table.get_item(
        Key={"contestantName": contestant_name },
        ProjectionExpression="#loc, vocalRange, score",   #"location" is a reserved word for ProjectionExpression, so we use an alias called "#loc"
        ExpressionAttributeNames={"#loc": "location"}  #Using ExpressionAttributeNames to make the alias
    )
    item_response = response.get('Item')

    # Check if the contestant exists
    if not item_response:
        raise HTTPException(status_code=404, detail="Contestant not found")

    #Extract the respective attributes
    vocalRange_attr = item_response.get('vocalRange')
    score_attr = item_response.get('score')
    location_attr = item_response.get('location')

    #Increase the "vocalRange" attribute by "boost" amount
    vocalRange_attr += boost

    #Update the value of score
    if vocalRange_attr == location_attr:
        score_attr = location_attr
    elif vocalRange_attr > location_attr:
        score_attr = vocalRange_attr - location_attr
    else:
        score_attr = -1

    #Update the CONTESTANT table with the changes made for the "VocalRange" and "score" for the specific contestantName
    table = tables["contestants"]
    response = table.update_item(
        Key = {"contestantName": contestant_name},
        UpdateExpression="SET vocalRange = :vocal_range, score = :score_",
        ExpressionAttributeValues={
            ":vocal_range": vocalRange_attr,
            ":score_" : score_attr
        },
    )
    

    #TASK 2: Create new/Update "Inventory (list)" attribute
    #===============================================
    #Retrieve the "inventory (list)" attribute from "CONTESTANT" table
    response = table.get_item(
        Key = {"contestantName": contestant_name},
        ProjectionExpression = "inventory"
    )
    item_response = response.get('Item')

    #If the contestant already has an "inventory (list)" attribute, get the list. Otherwise, create a new list inventory[]
    inventory = item_response.get("inventory", [])

    #Add the purchased item to the "inventory (list)"
    inventory.append(item)

    #Update the "inventory" attribute in the database
    table.update_item(
        Key={"contestantName": contestant_name},
        UpdateExpression="SET inventory = :inventory",
        ExpressionAttributeValues={":inventory": inventory},
    )
    return {"inventory": inventory}


