import requests
# import predict 

# 5545, 929
default_inputs = [
    {
        "holiday": "None",
        "temp": "288.28",
        "rain_1h": "0",
        "snow_1h": "0",
        "clouds_all": "40",
        "weather_main": "Clouds",
        "date_time": "2024-10-02 09:00:00"
    },
    {
        "holiday": "Thanksgiving Day",
        "temp": "268.24",
        "rain_1h": "0",
        "snow_1h": "0",
        "clouds_all": "64",
        "weather_main": "Clouds",
        "date_time": "2024-11-28 00:00:00"
    }
]

# host = "localhost:9696"
host = "traffic-volume-prediction-env.eba-5ccpyhep.eu-north-1.elasticbeanstalk.com:80"
url = f'http://{host}/predict'

for traffic in default_inputs:
    pred = requests.post(
        url=url,
        json=traffic
    ).json()
    # features = predict.prepare_features(traffic)

    print(pred)