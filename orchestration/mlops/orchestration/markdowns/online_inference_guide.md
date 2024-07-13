# Sample online inference

Use the following CURL command to get real-time predictions:

```curl
curl --location 'http://localhost:6789/api/runs' \
--header 'Authorization: Bearer 8c097d3f177344128bee40a66210ce3b' \
--header 'Content-Type: application/json' \
--header 'Cookie: lng=en' \
--data '{
    "run": {
        "pipeline_uuid": "predict",
        "block_uuid": "inference",
        "variables": {
            "inputs": [
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
        }
    }
}'
```

## Note

The `Authorization` header is using this pipeline’s API trigger’s token value.
The token value is set to `fire` for this project.
If you create a new trigger, that token will change.
Only use a fixed token for testing or demonstration purposes.

5545
929