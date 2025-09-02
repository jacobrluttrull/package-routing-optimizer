## Author : Jacob Luttrull
## WGUPS Routing Program
## Student ID: 011218373

import csv
import datetime
from HashTable import HashTable
from package import Package
from trucks import Truck
from builtins import ValueError

# Load CSVs into memory for distances, addresses, and packages
with open('CSV/distance-matrix.csv', 'r') as csvfile:
    CSV_Distance = list(csv.reader(csvfile))

with open('CSV/address.csv', 'r') as csvfile:
    CSV_Address = list(csv.reader(csvfile))

with open('CSV/packages.csv', 'r') as csvfile:
    CSV_Package = list(csv.reader(csvfile))

# Hash table for storing all package objects
packageHashTable = HashTable()

# Load and parse each package into the hash table
def load_package_data(filename, packageHashTable):
    with open(filename, 'r', encoding='utf-8-sig') as packageFile:
        package_data = csv.reader(packageFile)
        for row in package_data:
            if len(row) < 7:
                continue
            try:
                package_id = int(row[0].strip())
                address = row[1].strip()
                city = row[2].strip()
                state = row[3].strip()
                zip_code = row[4].strip()
                deadline = row[5].strip()
                weight = row[6].strip()
                status = "At Hub"
                package = Package(package_id, address, city, state, zip_code, deadline, weight, status)
                packageHashTable.insert(package_id, package)
            except Exception as e:
                print(f"[ERROR] Failed to load package: {row} -> {e}")

# Get the address index used in the distance matrix
def get_address_data(address):
    for row in CSV_Address:
        if address == row[2]:
            return int(row[0])
    raise ValueError(f"Address not found: {address}")

# Look up distance between two addresses
def distance_between(address1, address2):
    index1 = get_address_data(address1)
    index2 = get_address_data(address2)
    distance = CSV_Distance[index1][index2]
    if distance == '':
        distance = CSV_Distance[index2][index1]
    return float(distance)

# Setup the three trucks with package assignments and start times
truck1 = Truck(1, 16, 18, None, [1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40], 0.0, "4001 South 700 East",
               datetime.timedelta(hours=8))
truck2 = Truck(2, 16, 18, None, [3, 12, 17, 18, 21, 22, 23, 24, 26, 27, 35, 36, 38, 39], 0.0,
               "4001 South 700 East", datetime.timedelta(hours=10, minutes=20))
truck3 = Truck(3, 16, 18, None, [2, 4, 5, 6, 7, 8, 9, 10, 11, 25, 28, 32, 33], 0.0, "4001 South 700 East",
               datetime.timedelta(hours=9, minutes=5))

load_package_data('CSV/packages.csv', packageHashTable)

# Nearest-neighbor delivery simulation per truck
def delivery(truck):
    packagesNotDelivered = []
    for packageID in truck.packages:
        package = packageHashTable.lookup(packageID)
        if not package:
            continue
        package.truck_id = truck.truck_id
        package.departure_time = truck.departure_time
        packagesNotDelivered.append(package)
    truck.packages.clear()
    truck.current_time = truck.departure_time

    while packagesNotDelivered:
        # Package 9 address correction after 10:20 AM
        if truck.truck_id == 3 and truck.current_time >= datetime.timedelta(hours=10, minutes=20):
            package9 = packageHashTable.lookup(9)
            if package9 and package9.address != "410 S State St":
                package9.address = "410 S State St"
                package9.city = "Salt Lake City"
                package9.state = "UT"
                package9.zip_code = "84111"

        # Select next closest package
        next_package = None
        shortest_distance = float('inf')
        for package in packagesNotDelivered:
            if package.package_id == 9 and truck.truck_id == 3 and truck.current_time < datetime.timedelta(hours=10, minutes=20):
                continue
            distance = distance_between(truck.address, package.address)
            if distance < shortest_distance:
                shortest_distance = distance
                next_package = package

        if not next_package:
            break

        travel_time = shortest_distance / truck.speed
        truck.current_time += datetime.timedelta(hours=travel_time)
        truck.mileage += shortest_distance
        truck.address = next_package.address
        next_package.delivery_time = truck.current_time
        next_package.status = "Delivered"
        truck.packages.append(next_package.package_id)
        packagesNotDelivered.remove(next_package)

# Run deliveries
delivery(truck1)
delivery(truck2)
truck3.departure_time = min(truck1.current_time, truck2.current_time)
delivery(truck3)

# Prompt user for time input and return as timedelta
def get_time_input():
    user_time = input("Enter a time (HH:MM:SS): ")
    try:
        h, m, s = map(int, user_time.split(":"))
        return datetime.timedelta(hours=h, minutes=m, seconds=s)
    except:
        print("Invalid format. Please use HH:MM:SS")
        return get_time_input()

# Show one package's status based on entered time
def print_single_package_at_time(package_id, target_time):
    pkg = packageHashTable.lookup(package_id)
    if pkg:
        pkg.update_status(target_time)
        # Show Package 9’s wrong address before 10:20 AM
        if pkg.package_id == 9 and target_time < datetime.timedelta(hours=10, minutes=20):
            print(f"Package ID: 9, Address: 300 State St, City: Salt Lake City, State: UT, Zip Code: 84103, "
                  f"Deadline: {pkg.deadline}, Weight: {pkg.weight}, Status: {pkg.status}, "
                  f"Departure Time: {pkg.departure_time}, Delivery Time: {pkg.delivery_time}, On Truck: {pkg.truck_id}")
        # Show delayed packages before 9:05 AM
        elif pkg.package_id in [6, 25, 28, 32] and target_time < datetime.timedelta(hours=9, minutes=5):
            print(f"Package ID: {pkg.package_id}, Address: {pkg.address}, City: {pkg.city}, State: {pkg.state}, "
                  f"Zip Code: {pkg.zip_code}, Deadline: {pkg.deadline}, Weight: {pkg.weight}, "
                  f"Status: Delayed, Departure Time: {pkg.departure_time}, Delivery Time: {pkg.delivery_time}, On Truck: {pkg.truck_id}")
        else:
            print(pkg)
    else:
        print(f"Package ID {package_id} not found.")

# Show all packages at a specific time
def print_all_packages_at_time(target_time):
    print(f"\n Package Statuses at {str(target_time)}")
    for i in range(1, 41):
        pkg = packageHashTable.lookup(i)
        if pkg:
            pkg.update_status(target_time)
            if pkg.package_id == 9 and target_time < datetime.timedelta(hours=10, minutes=20):
                print(f"Package ID: 9, Address: 300 State St, City: Salt Lake City, State: UT, Zip Code: 84103, "
                      f"Deadline: {pkg.deadline}, Weight: {pkg.weight}, Status: {pkg.status}, "
                      f"Departure Time: {pkg.departure_time}, Delivery Time: {pkg.delivery_time}, On Truck: {pkg.truck_id}")
            elif pkg.package_id in [6, 25, 28, 32] and target_time < datetime.timedelta(hours=9, minutes=5):
                print(f"Package ID: {pkg.package_id}, Address: {pkg.address}, City: {pkg.city}, State: {pkg.state}, "
                      f"Zip Code: {pkg.zip_code}, Deadline: {pkg.deadline}, Weight: {pkg.weight}, "
                      f"Status: Delayed, Departure Time: {pkg.departure_time}, Delivery Time: {pkg.delivery_time}, On Truck: {pkg.truck_id}")
            else:
                print(pkg)

# Menu interface
def main():
    print("Welcome to the WGUPS Routing Program!")
    while True:
        print("\n********* WGUPS Routing Menu *********")
        print("1. View all package statuses at end of day")
        print("2. Get status of a single package at a specific time")
        print("3. View all package statuses at a specific time")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            end_of_day = datetime.timedelta(hours=17)
            print_all_packages_at_time(end_of_day)
            total_miles = truck1.mileage + truck2.mileage + truck3.mileage
            print(f"\nTotal mileage: {total_miles:.2f} miles")
            print(f"Truck 1 Mileage: {truck1.mileage:.2f}")
            print(f"Truck 2 Mileage: {truck2.mileage:.2f}")
            print(f"Truck 3 Mileage: {truck3.mileage:.2f}")

        elif choice == "2":
            try:
                pkg_id = int(input("Enter package ID (1–40): "))
                time = get_time_input()
                print_single_package_at_time(pkg_id, time)
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        elif choice == "3":
            time = get_time_input()
            print_all_packages_at_time(time)

        elif choice == "4":
            print("Exiting WGUPS Routing Program.")
            break

        else:
            print("Invalid input. Please choose between 1–4.")

if __name__ == "__main__":
    main()
