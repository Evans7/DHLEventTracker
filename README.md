# DHL Integration Application

This application provides integration with DHL's REST APIs for shipment tracking and service point location.

# Features

Track shipments using DHL's Shipment Tracking-Unified REST API
Find DHL service points within a specified radius from a given address

# Pre-requisites 

1.Python
2.Pip

# Installation

1. Clone the repository:
  git clone [your-repo-url]
  cd [your-repo-name]

2. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate  # 
   On Windows, use `venv\Scripts\activate`

3. Install dependencies:
   pip install -r requirements.txt
   
4. Configuration

   Create a .env file in the project root and add the following variables: 
   DHL_API_KEY=[Your DHL API Key]
   DHL_API_SECRET=[Your DHL API Secret]
   BASE_URL_SHIPMENT=[DHL Shipment API Base URL]
   BASE_URL_LOCATION=[DHL Location API Base URL]
   APP_API_KEY=testing         //The app uses a key to verify from external resources, kindly use this
   API_CALLS_LIMIT_LOCATION=500         //Location API limit , can be changed if upgraded
   API_CALLS_LIMIT_TRACKING=250         //Tracker API limit, can be changed if upgraded

5. Run the application in main directory 
   flask run

# UI testing
1. The initial local endpoint '/' loads index.html which has UI components to test the application 

# API Testing
You can also test the functionalties by making use of any postman or API software and test the following endpoints

1. POST http://{localhost}:{port}/track 

# Headers - 

Content-type:application/json
Accept:application/json
X-API-key:testing
# Request body:-

{
    "tracking_number": "your tracking number",
    "limit": 10,  //optional
    "offset": 10  //optional
}

limit is set to 10 by default
Offset is set to 0 by default


# Response:-

List of last event for each shipment as objects
Example:-
200 code
[
    {
        "countryCode": "GB",
        "description": "Shipment information received",
        "location": "BIRMINGHAM - UK",
        "status": "SD",
        "statusCode": "unknown",
        "timestamp": "2024-08-01T11:40:00+02:00",
        "trackingNumber": "4112889060"
    }
]

Error codes:-
400 - Bad request
404 - Resource not found
500 - Server error


2. GET http://{localhost}:{port}/service-points

# Headers:-

X-API-key:testing

# Request params:-

radius(Optional) - Defaults to 5000
countryCode(Required) - Defaults to GB
limit is set to 50 by default


# Response:-

List of service points based on provided city and country code 
Example:-
200 code
[
    {
        "name": "Ryman Birmingham Temple St"
    },
    {
        "name": "3D News"
    },
    {
        "name": "Ryman Grand Central"
    },
    {
        "name": "WHSmith Birmingham"
    },
    {
        "name": "Newspoint"
    }
]

Error codes 

400 - Bad request
404 - Resource not found
500 - Server error