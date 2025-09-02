class Truck:
    def __init__(self,truck_id, capacity, speed, load, packages, mileage, address, departure_time ):
        self.truck_id = truck_id
        self.capacity = capacity
        self.speed = speed
        self.load = load
        self.packages = packages
        self.mileage = mileage
        self.address = address
        self.departure_time = departure_time
        self.current_time = departure_time
    def __str__(self):
        return f" Truck ID: {self.truck_id}, Truck Capacity: {self.capacity}, Speed: {self.speed}, Load: {self.load}, Mileage: {self.mileage}, Address: {self.address}, Departure Time: {self.departure_time}"
