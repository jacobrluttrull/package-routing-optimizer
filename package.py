class Package:
    def __init__(self, package_id, address, city, state, zip_code, deadline, weight, status):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.status = status
        self.departure_time = None
        self.delivery_time = None
        self.truck_id = None

    def __str__(self):
        return f"Package ID: {self.package_id}, Address: {self.address}, City: {self.city}, State: {self.state}, Zip Code: {self.zip_code}, Deadline: {self.deadline}, Weight: {self.weight}, Status: {self.status}, Departure Time: {self.departure_time}, Delivery Time: {self.delivery_time}, On Truck: {self.truck_id}"

    def update_status (self, current_time):
        if self.delivery_time and current_time >= self.delivery_time:
            self.status = "Delivered"
        elif self.departure_time and current_time >= self.departure_time:
            self.status = "En Route"
        else:
            self.status = "At Hub"
