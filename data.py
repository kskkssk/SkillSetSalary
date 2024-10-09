from sklearn.model_selection import train_test_split
import pandas as pd
from config import config


def load_dataset() -> tuple[list]:
    dataset = pd.read_csv('for_split.csv')
    X = dataset.drop('salary')
    y = dataset.salary
    return X, y


def split_dataset(X, y) -> dict:
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config["data"]["test_size"],
        random_state=config["random_state"],
    )
    data = {
        "x_train": X_train,
        "x_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
    }
    return data


def get_data() -> dict:
    return split_dataset(*load_dataset())
