import time
from math import radians, sin, cos, sqrt, atan2

# --- Location Class ---
class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

# --- Location Provider (Fixed Position) ---
class LocationProvider:
    def __init__(self):
        self.latitude = 40.0  # Example starting latitude
        self.longitude = -74.0  # Example starting longitude

    def get_location(self):
        # Fixed location (no random movement, stays stationary)
        return Location(self.latitude, self.longitude)

# Use the location provider
location_provider = LocationProvider()

class LocationService:
    @staticmethod
    def get_location():
        return location_provider.get_location()

    @staticmethod
    def start_updating():
        print("Location updates started.")

    @staticmethod
    def stop_updating():
        print("Location updates stopped.")

# --- Step Tracker Logic ---
previous_location = None
total_steps = 0

def update_location():
    global previous_location, total_steps
    current_location = LocationService.get_location()

    if previous_location is not None:
        # Calculate distance only when location has changed
        distance = calculate_distance(previous_location, current_location)
        print(f"Moved {distance:.2f} meters")

        if distance >= 100:  # Only count a step if moved at least 100 meters
            total_steps += 1
            print(f"Steps: {total_steps}")
            previous_location = current_location  # Update previous location only after a step
    else:
        previous_location = current_location  # Set the initial location

def calculate_distance(loc1, loc2):
    R = 6371  # Earth radius in km
    lat1, lon1 = radians(loc1.latitude), radians(loc1.longitude)
    lat2, lon2 = radians(loc2.latitude), radians(loc2.longitude)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c * 1000  # Return distance in meters

def main():
    LocationService.start_updating()
    try:
        while True:
            update_location()
            time.sleep(1)  # Adjust this as needed for your simulation speed
    except KeyboardInterrupt:
        LocationService.stop_updating()
        print("Location tracking stopped.")

if __name__ == "__main__":
    main()
