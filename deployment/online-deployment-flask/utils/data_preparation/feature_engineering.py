from sklearn.base import BaseEstimator, TransformerMixin
from pandas import DataFrame, Series


class FeatureEngineeringTransformer(BaseEstimator, TransformerMixin):
    """
    A class to create new columns and manipulate existing ones,
    used as a step in the pipeline
    """
    def __init__(self):
        """
        Initializes the object with no attributes
        """
        pass

    def fit(
        self, 
        X: DataFrame,
        y: Series = None
    ) -> "FeatureEngineeringTransformer":
        """
        Required by the pipeline

        Parameters:
        -----------
        X : DataFrame
            X features

        y : Series
            y features

        Returns:
        --------
        FeatureEngineeringTransformer
            The FeatureEngineeringTransformer object itself
        """
        return self

    def transform(
        self, 
        X: DataFrame, 
        y: Series = None
    ) -> DataFrame:
        """
        Transform data by creating new columns and manipulating existing ones

        Parameters:
        -----------
        X : DataFrame
            X features

        y : Series
            y features

        Returns:
        --------
        DataFrame
            Transformed data
        """
        # Apply transformation
        X_transformed = X.copy()
        
        # Perform Feature engineering
        X_transformed['hour'] = X_transformed['date_time'].dt.hour
        X_transformed['month'] = X_transformed['date_time'].dt.month
        X_transformed['day_of_week'] = X_transformed['date_time'].dt.dayofweek

        # Transform holiday column to binary
        X_transformed['holiday'] = X_transformed['holiday'].map(
            lambda x: 0 if str(x) == 'None' else 1
        )

        # weather_main rare values handling:
        X_transformed['weather_main'] = X_transformed['weather_main'].map(
            lambda x: "Fog_Smoke_Squall" if x in ["Fog", "Smoke", "Squall"] else x
        )

 
        return X_transformed.drop("date_time", axis=1)