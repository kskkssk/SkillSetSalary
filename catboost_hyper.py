from catboost_hyper import CatBoostRegressor
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
    catboost = CatBoostRegressor()
    catboost_hyper = CatBoostRegressor(
        learning_rate=config['catboost_hyper']['learning_rate'],
        depth=config['catboost_hyper']['depth'],
        l2_leaf_reg=config['catboost_hyper']['depth'],
        min_child_samples=config['catboost_hyper']['min_child_samples'],
        iterations=config['catboost_hyper']['iterations'],
        early_stopping_rounds=config['catboost_hyper']['early_stopping_rounds'])
    data = get_data()
    train(catboost_hyper, data["x_train"], data["y_train"])
    test(catboost_hyper, data["x_test"], data["y_test"])
