# Data Schemas / Models Organization and Structure
### Final Database Structure:
```python
Table Name: CONTESTANTS
Attributes:
    contestantName: str #partition key
    husbandName: str
    vocalRange: int
    location: int
    score: int
    inventory: Optional[List[str]]
```
I arrived at this decision following two iterations of database modeling, ultimately settling on the second iteration as the finalized database model. In the initial iteration, I used a separate table called "SCOREBOARD" for scorekeeping. However, during the implementation phase, I recognized opportunities for efficiency improvements in two key areas:

**Scoring**:
* I observed the potential for enhanced efficiency by introducing a "score" attribute during contestant registration. The approach I took in calculating the score is as follows:
    * if `vocalRange > location`, the `score = vocalRange - location`;
    * if `vocalRange == location`, the `score = location`;
    * and if `vocalRange < location`, the `score = -1`.
* This optimization greatly simplified the husbandCall route: If the retrieved score is -1, we simply return an error message describing that the vocalRange is less than the location. Otherwise, we return the retrieved score attribute value.

**Inventory List**:
* After recognizing the improvements in the scoring system, I identified a similar opportunity to enhance the Inventory List for the Buy A PowerUp Item functionality. This was achieved by simply introducing an "Inventory" attribute and storing all power-up items there.

The need for optimization and efficiency should be prioritized when working as an Industry Developer on Backend Projects. That said, it is important to realize that leveraging existing table structure(s) would be greatly effective instead of defining a whole new database table. I am glad I realized the opportunity for efficiency and improved the way I implement my project.  

### First Iteration Database Structure:
``` python
able Name: CONTESTANTS
Attributes:
    contestantName: str #partition key
    husbandName: str
    vocalRange: int
    location: int
    inventory: [List[str]]

Table Name: SCOREBOARD
Attributes:
    score: int #partition key
    contestantName: str #sort key
```
<br>

---

<br>

# DISCUSSION ON CHALLENGING ASPECTS
While most of this project's tasks were pretty straightforward, I discovered on the following challenges:

**Using Parameters Instead of Response Body (JSON)**:
* Issue: Initially, I set up the API routes to use Parameters to handle the data. This worked just fine in FastAPI, where I could easily define the parameters using the Text Entry Form provided. However, when I tested the routes in Postman, I realized they didn't match the project's specs. The project required using the Request Body for the API routes instead of Parameters. Example:
    * ```python
        @app.post("/contestants")
        async def register_contestant(contestantName: str, husbandName: str, vocalRange: int,  location: int)
          ...
      ```
* Solution: Drawing from a similar project I worked on during my internship and diving into FastAPI documentation, I implemented BaseModels in the Pydantic module. I created two BaseModels, `ContestantRegistration(BaseModel)` and `PowerUpItem(BaseModel)`, in a file called `models.py`. Using BaseModels allowed me to automatically get the required attributes from the project specs without explicitly defining them as parameters. Example:
    * ```python
        @app.post("/contestants")
        async def register_contestant(contestant: ContestantRegistration):
          contestantName = contestant.contestantName
          husbandName = contestant.husbandName
          vocalRange = contestant.vocalRange
          location = contestant.location
          ...
      ```
**Retrieving contestantName from the URL:**
* Issue: Initially, I am aware that the URL must reflect the accessed contestantName. However, once again I thought I could simply use contestantName as a parameter in the API routes. But I soon realized that wasn't the case. As a best practice, I reached out to the Web Development Team via email to double-check my understanding. After their confirmation, I realized I may not explicitly use contestantName as a parameter. Example:
    * ```python
        @app.get("/husbandCall/{contestantName}/")
        async def husband_call_and_score(contestantName: str):
          ...
      ```
* Solution: I remembered a similar task from my internship and did some more reading in the FastAPI documentation. That's when I figured out I needed to use the Request module from FastAPI to fetch the contestantName attribute from the URL. Example:
    * ```python
        @app.get("/husbandCall/{contestantName}")
        async def husband_call_and_score(request: Request):
          #Extracts the "contestantName" from the URL
          contestant_name  = request.path_params.get("contestantName")
          ...
      ```
<br>

---

<br>

# Decision On Response Codes or Errors
In terms of response codes and error handling, I made decisions based on a thorough analysis of the project specifications. My aim was to ensure that if something went awry, the error codes would provide meaningful information to assist with debugging and troubleshooting. As a general practice, after performing any database operations, it was crucial to validate the returned response.

For instance, in cases where everything went smoothly, a response like this was expected:
```python
  GET /husbandCall/Alice
  Response:
  {
    "score": 100
  }
```
Conversely, if a request was made for a contestant who didn't exist, the response needed to be informative, like this:
```python
  GET /husbandCall/Alice
  Response:
  {
    "score": 100
  }
```
Handling scenarios like the one above involved error-checking code similar to the following:
```python
  # Error check if contestant is not found
  if not items:
    raise HTTPException(status_code=404, detail="Contestant not found") 
````
<br>
---
<br>

# Pseudocode And Thought Process At A Glance
### Initial Setup and Environment Variables:
* Loaded AWS credentials from environment variables using dotenv.
* Set up AWS DynamoDB connections using boto3.
* Created tables dictionary for referencing DynamoDB tables.
* Created a basic FastAPI application.

### Registration Endpoint (/contestants):
* Created a POST endpoint to register contestants and their attributes.
* Utilized FastAPI's ContestantRegistration model for request validation.
* Extracted data from the request body.
* Calculated the score based on vocalRange and location.
* Inserted contestant data into the DynamoDB table.
* Implemented error handling for registration.

### Get Contestants Endpoint (/contestants):
* Created a GET endpoint to retrieve contestant data.
* Utilized a query parameter to enable sorting by contestant name.
* Accessed the DynamoDB table and used .scan() to retrieve data.
* Sorted data if requested and returned pairs of contestant and husband names.

### Husband Call and Score Endpoint (/husbandCall/{contestantName}):
* Created a GET endpoint to determine the score of a husband call.
* Extracted contestant name from the URL path.
* Accessed the DynamoDB table and queried the score attribute.
* Implemented error handling for contestant not found or vocalRange less than location.
* Returned the score or an error message.

### Best Shout Endpoint (/bestShout):
* Created a GET endpoint to find the contestant with the highest score.
* Accessed the DynamoDB table and used .scan() to retrieve contestant data.
* Calculated the contestant with the highest score based on the score attribute.
* Assumed there are no ties and returned the highest-scoring contestant's name and score.

### Buy Power-Up Item Endpoint (/buyItem/{contestantName}):
* Created a POST endpoint to allow contestants to buy power-up items.
* Utilized the PowerUpItem model for request validation.
* Extracted data from the request body.
* Modified the vocalRange and recalculated the score attribute.
* Updated the contestant's data in the DynamoDB table.
* Created or updated an inventory list attribute.
* Returned the updated inventory.
