# WDB Industry Developer (Backend) Technical Interview
WebDev at Berkeley Fall 2023 Technical Interview - Industry Developer Track (Backend Project)

# Iowa State Fair: Husband Calling
> The annual Husband Calling contest at the Iowa State Fair is an entertaining event that has seen more than 500 contestants and over 2000 spectators from around the country gather to share little moments of affection. Contestants take turns on stage in speaking to their partner, competing to be the dearest and most loving of all. It is a great way of strengthening relationships and fostering a community of love.

The Iowa State Fair is looking to bring their registration and contest-management system to the web and is seeking to build a backend service with the following features:
1. Register a contestant/husband pair
2. Get a list of all contestants
3. Perform a "husband call" and score it
4. Get the highest-score shout across all contestants (INDUSTRY ONLY)
5. Buy a power-up item (INDUSTRY ONLY)

In particular, they want you to build an API capable of handling all of the functionality mentioned above.


## Register Contestant/Husband
Register a contestant and associate them with their husband. Every contestant also has a "vocalRange" field (which represents how many meters their voice will go). Lastly, the husband has a "location" which represents their distance (in meters) from the contestant zone.

You can assume that all contestants and husbands have a unique name.

Example request: `POST /contestants`

Request body:
```
{
  "contestantName": "Alice",
  "husbandName": "Bob",
  "vocalRange": 100,
  "location": 500
}
```
The response can look like anything. You should raise an error if a field is missing, with a descriptive error message.


## Get All Contestants
Return a list of all contestants and the husband they are paired with.

Industry Checkpoint: Add additional functionality to this API route allowing you to include a query parameter sortedByName=true that determines if you should return by sorted order of contestantName. (ex: GET /contestants?sortedByName=true)

Example request:`GET /contestants`

Example response:

```{
  "pairs": [
    {
      "contestantName": "Alice",
      "husbandName": "Bob"
    },
    {
      "contestantName": "Cady",
      "husbandName": "Desmond"
    }
  ]
}
```


## Perform Husband Call and Score it
Of course, no husband calling is complete without, well, a husband call! This route should perform the call for a specific contestant.

We determine the score of a husband call based on the husband's location and the contestant's vocalRange. If the vocalRange is exactly equal to the location, the score is equal to the location. If the vocal range is greater, the score is the absolute difference between the location and the vocalRange. In both these cases, return the score.

If the vocalRange is less, we should raise an error with a descriptive message. If the contestant name passed in hasn't been registered, that should raise an error too.

Example request:`GET /husbandCall/Alice`

Example response:
```
{
  "score": 100
}
```

## Get Highest Score Shout (INDUSTRY ONLY)
This route should return the score of the best shout across all contestants, as well as the contestant. You can either assume no ties or break ties randomly, just make sure it is clear which option you go for.

Example request: `GET /bestShout`

Example response:
```
{
  "contestantName": "Alice",
  "score": 100
}
```

## Buy a Power-up Item (INDUSTRY ONLY)
Some contestants have said they want to be able to use the best and latest tech to improve their scores! Implement an API route that lets contestants purchase an item and add it to their inventory. The response should be a list of all the items in the user's inventory.

Each item has a "boost", which increases the vocalRange by that amount.
Items cannot be removed from the inventory.
All items in the inventory get used when a husbandCall is made.
Note that completing this section will also involve modifying your existing husbandCall route!

Example request (note the route has the contestantName in it!): `POST /buyItem/Alice`

Request body:
```
{
  "item": "megaphone",
  "boost": 150
}
```
Example response:
```
{
  "inventory": ["megaphone", "mysterious drugs"]
}
```
