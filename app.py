from flask import Flask, request, render_template,jsonify  
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
import logging

# Loading environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Access the environment variables
DHL_API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL_SHIPMENT = os.getenv("BASE_URL_SHIPMENT")
BASE_URL_LOCATION = os.getenv("BASE_URL_LOCATION")

last_city = None
API_CALLS_LIMIT_LOCATION = 500  # Setting limit as per the documentation for location
api_calls_count_location = 0

API_CALLS_LIMIT_TRACKING = 250  # Setting limit as per the documentation for tracking
api_calls_count_tracking = 0

api_last_reset = datetime.now()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def reset_daily_limits():
    global api_last_reset , api_calls_count_location,api_calls_count_tracking
    now = datetime.now()
    
    # Reset API limits daily
    if (now - api_last_reset).days >= 1:
        api_calls_count_location = 0
        api_calls_count_tracking = 0
        api_last_reset = now



# Function to get the last tracking event
def get_last_tracking_event(tracking_number: str,api_key:str,limit: int = 10, offset: int = 0, retries:int = 3) -> dict:
   
    reset_daily_limits()
    headers = {'DHL-API-Key': api_key}
    params = {
        "trackingNumber": tracking_number,
        "limit": limit,
        "offset": offset
    }
    global api_calls_count_tracking
    if api_calls_count_tracking >= API_CALLS_LIMIT_TRACKING:
        return {"error": "Daily API limit reached. Please try again tomorrow."}

    try:
        # Make the GET request to the DHL API
        response = requests.get(BASE_URL_SHIPMENT+'/track/shipments', headers=headers, params=params)

        if response.status_code == 429:
            if retries > 0:
                print(f"Rate limit exceeded. Retrying after 5 seconds... ({retries} retries left)")
                time.sleep(5)  # Wait for 5 seconds before retrying as per the documentation
                return get_last_tracking_event(tracking_number,DHL_API_KEY, retries - 1)
            else:
                return {"error": "Rate limit exceeded. Please try again later."}

        api_calls_count_tracking += 1
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the response JSON
        tracking_data = response.json()

        last_events = []
        print("Tracking api limit counter: "+str(api_calls_count_tracking))
        # Iterate over shipments
        if 'shipments' in tracking_data and len(tracking_data['shipments']) > 0:
            for shipment in tracking_data['shipments']:
                events = shipment.get('events', [])
                if events:
                    sorted_events = sorted(events, key=lambda x: datetime.fromisoformat(x['timestamp']), reverse=True)
                    last_event = sorted_events[0]  # Get the most recent event                    
                    last_event_info = {
                        "trackingNumber": shipment.get("id"),
                        "timestamp": last_event.get("timestamp"),
                        "location": last_event.get("location", {}).get("address", {}).get("addressLocality", "Unknown"),
                        "countryCode": last_event.get("location", {}).get("address", {}).get("countryCode", "Unknown"),
                        "statusCode": last_event.get("statusCode", "Unknown"),
                        "status": last_event.get("status", "Unknown"),
                        "description": last_event.get("description", "No description available")
                    }
                    last_events.append(last_event_info)

                    global last_city
                    # Assuming the city is in the format "CITY-COUNTRY"
                    last_city_full = last_event_info['location']
                    last_city = last_city_full.split('-')[0] if '-' in last_city_full else last_city_full
                else:
                    last_events.append({"trackingNumber": shipment.get("id"), "error": "No events found for this shipment."})
        else:
            return {"error": "No shipments found for the given tracking number."}

        return last_events

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {str(e)}")
        if e.response.status_code == 404:
            return {"error": f"Tracking number {tracking_number} not found.", "status": "NOT_FOUND"}
        elif e.response.status_code == 400:
            return {"error": "Invalid request. Please check your input.", "status": "BAD_REQUEST"}
        elif e.response.status_code == 401:
            return {"error": "Unauthorized. Please check your API key.", "status": "UNAUTHORIZED"}
        elif e.response.status_code == 500:
            return {"error": "Internal server error. Please try again later.", "status": "SERVER_ERROR"}
        else:
            return {"error": f"An HTTP error occurred: {str(e)}", "status": "ERROR"}
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return {"error": f"A network error occurred: {str(e)}", "status": "NETWORK_ERROR"}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return {"error": "An unexpected error occurred. Please try again later.", "status": "UNEXPECTED_ERROR"}


def fetch_service_points(country_code: str, last_city: str, radius: int = 5000,limit: int=50) -> dict:
    # Check if last_city is None or empty
    global api_calls_count_location
    if not last_city:
        return {"error": "Please find a valid shipment using your tracking number."}
    if api_calls_count_location >= API_CALLS_LIMIT_LOCATION:
        return {"error": "API limit reached"}
    reset_daily_limits()
    headers = {'DHL-API-Key': DHL_API_KEY}
    params = {
        "countryCode": country_code,
        "addressLocality": last_city,  
        "radius": radius,  # Default radius
        "limit": limit  # Setting to 50 to get maximum number of service points as asked in task and the limitation set by DHL
    }

    try:
        # Make the GET request to the DHL Location Finder API
        response = requests.get(BASE_URL_LOCATION+'/location-finder/v1/find-by-address', headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the response JSON
        location_data = response.json()
        locations = location_data.get('locations', [])
        location_list = [{"name": location.get('name')} for location in locations if 'name' in location]
        api_calls_count_location += 1
        print("Location api limit counter: "+str(api_calls_count_location))
        return location_list
    
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {str(e)}")
        if e.response.status_code == 400:
            error_data = e.response.json()
            return {
                "error": f"Bad Request: {error_data.get('title', 'Unknown error')}",
                "detail": error_data.get('detail', 'No additional details provided'),
                "status": "BAD_REQUEST"
            }
        elif e.response.status_code == 401:
            return {"error": "Unauthorized: Invalid API key", "status": "UNAUTHORIZED"}
        elif e.response.status_code == 500:
            return {"error": "Internal Server Error: The DHL service is currently experiencing issues", "status": "SERVER_ERROR"}
        else:
            return {"error": f"An HTTP error occurred: {str(e)}"}

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return {"error": f"A network error occurred: {str(e)}"}
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return {"error": "An unexpected error occurred. Please try again later."}


@app.route('/')
def index():
    return render_template('index.html')  # Render the HTML template

@app.route('/track', methods=['POST'])
def track_shipment():
    tracking_number = request.json.get('tracking_number')  # Get the tracking number from the request, using post as tracking number should be secured in request
    if tracking_number:
        result = get_last_tracking_event(tracking_number, DHL_API_KEY)
        if 'error' in result:
            if result.get('status') == "NOT_FOUND":
                return jsonify(result), 404
            elif result.get('status') == 'BAD_REQUEST':
                return jsonify(result), 400
            elif result.get('status') == 'UNAUTHORIZED':
                return jsonify(result), 401
            elif result.get('status') == 'SERVER_ERROR':
                return jsonify(result), 500
            else:
                return jsonify(result), 500  # Default to 500 for other errors
        return jsonify(result)  # Return JSON response
    return jsonify({"error": "Tracking number is required."}), 400

@app.route('/service-points', methods=['GET'])
def get_service_points():
    global last_city  # Access the global last_city variable
    radius = request.args.get('radius', default=5000, type=int)  # Get radius from query parameters, default to 5000 if not provided
    country_code = request.args.get('countryCode', default='GB', type=str)  # Not hardcoded value but default value set to GB
    limit = request.args.get('limit',default=50,type=int)
    if last_city is None:
        return jsonify({"error": "Find a valid shipment using your tracking number."}), 400

    # Call the function to fetch service points
    service_points = fetch_service_points(country_code, last_city, radius,limit)
    if 'error' in service_points:
        if service_points.get('status') == 'BAD_REQUEST':
            return jsonify(service_points), 400
        elif service_points.get('status') == 'UNAUTHORIZED':
            return jsonify(service_points), 401
        elif service_points.get('status') == 'SERVER_ERROR':
            return jsonify(service_points), 500
        else:
            return jsonify(service_points), 500  # Default to 500 for other errors
    return jsonify(service_points)  # Return JSON response

if __name__ == '__main__':
    app.run(debug=True)