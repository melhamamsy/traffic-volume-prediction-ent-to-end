if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from typing import Dict, List
from pandas import DataFrame
from utils.data_preparation.cleaning import correct_dtypes


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


@custom
def transform_custom(
    pipelines, *args, **kwargs
) -> Dict[str, List]:
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your custom logic here
    date_time_column = kwargs['DATE_TIME']
    model_version = str(kwargs['MODEL_VERSION'])


    data = kwargs.get(
        "INPUTS",
        default_inputs
    )



    data = DataFrame(data)
    data = correct_dtypes(data, date_time_column=date_time_column)

    
    
    pipeline = pipelines["register_models"][0][model_version]
    preds = list(pipeline.predict(data))

    print(f"Version {model_version}:")
    print(f"\tPredictions: {preds}")


    return preds


