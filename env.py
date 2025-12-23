from rocketpy import Environment
import datetime
env = Environment(latitude=22.182484, longitude=120.890888, elevation=2)
env.set_date(datetime.datetime(2025, 12, 25, 12, 0, 0))
env.set_atmospheric_model(type="Forecast", file="GFS")
env.info()