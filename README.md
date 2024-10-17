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
   API_KEY=[Your DHL API Key]
   API_SECRET=[Your DHL API Secret]
   BASE_URL_SHIPMENT=[DHL Shipment API Base URL]
   BASE_URL_LOCATION=[DHL Location API Base URL]

5. Run the application in main directory 
   flask run

# UI testing
1. The initally local endpoint '/' loads index.html which has UI components to test the application 

# API Testing
You can also test the functionalties by making use of any postman or API software and test the following endpoints

1. POST http://{localhost}:{port}/track 

# Headers - 

Content-type:application/json
Accept:application/json

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

404,400 Error codes possible


2. GET http://{localhost}:{port}/service-points


# Request params:-

radius(Optional) - Defaults to 5000
countryCode(Required) - Defaults to GB
limit is set to 50 by default


# Response:-

List of service points based on provided city and country code 
Example:-
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

404,400 Error codes possible