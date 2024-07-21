from pandas import DataFrame, Series
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction import DictVectorizer


class DictVectorizerTransformer(BaseEstimator, TransformerMixin):
    """
    A class to one-hot-encode the string columns, used as a step in the pipeline

    Attributes:
    -----------
    vectorizer : DictVectorizer
        Scikit-learn dict-vectorizer

    sparse : bool
        A boolean to decide whether or not to produce a sparse output
    """

    def __init__(self, sparse=False):
        """
        Initialize the DictVectorizerTransformer with the vectorizer and sparse bool.

        Parameters:
        -----------
        sparse : bool
            A boolean to decide whether or not to produce a sparse output
        """
        self.sparse = sparse
        self.vectorizer = DictVectorizer(sparse=self.sparse)

    def fit(self, X: DataFrame, y: Series = None) -> "DictVectorizerTransformer":
        """
        Fit the vectorizer to the training data

        Parameters:
        -----------
        X : DataFrame
            X features

        y : Series
            y features

        Returns:
        --------
        DictVectorizerTransformer
            The DictVectorizerTransformer object itself
        """
        self.vectorizer.fit(X[["weather_main"]].to_dict(orient="records"))

        return self

    def transform(self, X: DataFrame, y: Series = None) -> DataFrame:
        """
        Transform data using the pre-fit vectorizer

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
        weather_main_transformed = self.vectorizer.transform(
            X[["weather_main"]].to_dict(orient="records")
        )
        weather_main_df = DataFrame(
            weather_main_transformed,
            columns=self.vectorizer.get_feature_names_out(),
            index=X.index,
        )
        X_transformed = X.join(weather_main_df).drop(columns=["weather_main"])
        return X_transformed
