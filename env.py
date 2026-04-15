from rocketpy import Environment
import datetime

env = Environment(latitude=22.17478, longitude=120.8927, elevation=4)
env.set_date(datetime.datetime(2025, 7, 26, 7, 0, 0))
env.set_atmospheric_model(type="Windy", file="GFS")



