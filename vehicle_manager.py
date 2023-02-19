from __future__ import annotations
from typing import Union, Optional
from math import radians, cos, sin, asin, sqrt

import requests


class VehicleManager:
    def __init__(self, url: str, name='/vehicles') -> None:
        self.url = url + name

    def get_vehicles(self) -> list[Vehicle]:
        url = self.url
        req_vehicles = self._get_vehicles(url)
        result = [Vehicle(**vehicle) for vehicle in req_vehicles]
        return result

    def filter_vehicles(self, params: dict) -> list:
        url = self.url
        req_vehicles = self._get_vehicles(url)
        result = []
        for vehicle in req_vehicles:
            if tuple(*params.items()) in vehicle.items():
                result.append(Vehicle(**vehicle))
        return result

    def get_vehicle(self, vehicle_id=1) -> Vehicle:
        url = self.url + '/' + str(vehicle_id)
        res = self._get_vehicles(url=url)
        return Vehicle(**res)

    def add_vehicle(self, vehicle: Vehicle = None) -> Optional[str, Vehicle]:
        try:
            response = requests.post(url=self.url, data=vehicle.__dict__)
            response.raise_for_status()
            return vehicle
        except requests.exceptions.HTTPError as e:
            return print("Error: {}".format(e))
        except requests.exceptions.RequestException as e:
            return print("Error: {}".format(e))

    def update_vehicle(self, vehicle: Vehicle = None) -> Optional[str, Vehicle]:
        v_id = vehicle.__dict__.pop('id')
        data = vehicle.__dict__
        try:
            response = requests.put(url=f'{self.url}/{str(v_id)}', data=data)
            response.raise_for_status()
            return vehicle
        except requests.exceptions.HTTPError as e:
            return print("Error: {}".format(e))
        except requests.exceptions.RequestException as e:
            return print("Error: {}".format(e))

    def delete_vehicle(self, id=0) -> Optional[str]:
        try:
            response = requests.delete(url=f'{self.url}/{str(id)}')
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return print("Error: {}".format(e))
        except requests.exceptions.RequestException as e:
            return print("Error: {}".format(e))

    def get_distance(self, id1: int, id2: int) -> float:
        vehicle1 = self.get_vehicle(id1)
        vehicle2 = self.get_vehicle(id2)
        v1_lat = radians(vehicle1.latitude)
        v1_long = radians(vehicle1.longitude)
        v2_lat = radians(vehicle2.latitude)
        v2_long = radians(vehicle2.longitude)
        result = VehicleManager._get_distance(v1_lat, v1_long, v2_lat, v2_long)
        return result

    def get_nearest_vehicle(self, id=1) -> Vehicle:
        main_vehicle = self.get_vehicle(id)
        vehicles = self.get_vehicles()
        min_dist = 0
        near_vehicle = None
        for vehicle in vehicles:
            if id == vehicle.id:
                continue
            distance = VehicleManager._get_distance(radians(main_vehicle.latitude),
                                                    radians(main_vehicle.longitude),
                                                    radians(vehicle.latitude),
                                                    radians(vehicle.longitude)
                                                    )
            if near_vehicle is None:
                min_dist = distance
                near_vehicle = vehicle
            if min_dist > distance:
                min_dist = distance
                near_vehicle = vehicle

        return near_vehicle

    @staticmethod
    def _get_vehicles(url: str) -> Union[list, dict, str]:
        try:
            response = requests.get(url=url)
            response.raise_for_status()
            json_obj = response.json()
            return json_obj
        except requests.exceptions.HTTPError as e:
            return f"Error: {e}"
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"

    @staticmethod
    def _get_distance(v1_lat: float, v1_long: float, v2_lat: float, v2_long: float) -> float:
        d_long = v2_long - v1_long
        d_lat = v2_lat - v1_lat
        p = sin(d_lat / 2) ** 2 + cos(v1_lat) * cos(v2_lat) * sin(d_long / 2) ** 2
        q = 2 * asin(sqrt(p))
        r_km = 6371000
        return q * r_km


class Vehicle:
    def __init__(self, id=None, name=None, model=None, year=None, color=None,
                 price=None, latitude=None, longitude=None) -> None:
        if id:
            self.id = id
        self.name = name
        self.model = model
        self.year = year
        self.color = color
        self.price = price
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f'<Vehicle: {self.name} {self.model} {self.year} {self.color} {self.price}>'
