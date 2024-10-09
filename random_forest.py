from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from sklearn.metrics import mean_squared_log_error, root_mean_squared_error
from config import config
from data import get_data


def train(model, x_train, y_train) -> None:
    model.fit(x_train, y_train)


def test(model, x_test, y_test) -> None:
    y_pred = model.predict(x_test)
    print(f"MSLE: {mean_squared_log_error(y_true=y_test, y_pred=y_pred)}")
    print(f"RMSE: {root_mean_squared_error(y_true=y_test, y_pred=y_pred)}")
    print(f"MAPE: {mean_absolute_percentage_error(y_true=y_test, y_pred=y_pred)}")
    print(f"MAE: {mean_absolute_error(y_true=y_test, y_pred=y_pred)}")
    print(f"MSE:  {mean_squared_error(y_true=y_test, y_pred=y_pred)}")


if __name__ == "__main__":
    forest = RandomForestRegressor()

    data = get_data()
    train(logistic_regression_model, data["x_train"], data["y_train"])
    test(logistic_regression_model, data["x_test"], data["y_test"])
