import numpy as np
from numpy.testing import assert_almost_equal, assert_array_equal
from numpy.testing import assert_raises
from sysidentpy.model_structure_selection import UOFR
from sysidentpy.basis_function import Polynomial
from sysidentpy.parameter_estimation.estimators import (
    LeastSquares,
    RecursiveLeastSquares,
)
from sysidentpy.tests.test_narmax_base import create_test_data

x, y, _ = create_test_data()
train_percentage = 90
split_data = int(len(x) * (train_percentage / 100))
X_train = x[0:split_data, 0]
X_test = x[split_data::, 0]
y1 = y[0:split_data, 0]
y_test = y[split_data::, 0]
y_train = y1.copy()
y_train = np.reshape(y_train, (len(y_train), 1))
X_train = np.reshape(X_train, (len(X_train), 1))
y_test = np.reshape(y_test, (len(y_test), 1))
X_test = np.reshape(X_test, (len(X_test), 1))


def test_error_reduction_ratio():
    # piv = np.array([4, 2, 7, 11, 5])
    model_code = np.array(
        [[2002, 0], [1002, 0], [2001, 1001], [2002, 1002], [1001, 1001]]
    )
    basis_function = Polynomial(degree=2)
    x, y, _ = create_test_data()
    model = UOFR(
        n_terms=5,
        order_selection=True,
        n_info_values=5,
        info_criteria="aic",
        err_tol=None,
        ylag=[1, 2],
        xlag=2,
        estimator=LeastSquares(),
        basis_function=basis_function,
    )
    model.fit(X=x, y=y)
    assert_array_equal(model.final_model, model_code)


def test_fit_with_information_criteria():
    basis_function = Polynomial(degree=2)
    model = UOFR(
        n_terms=15,
        order_selection=True,
        basis_function=basis_function,
    )
    model.fit(X=x, y=y)
    assert "info_values" in dir(model)


def test_fit_without_information_criteria():
    basis_function = Polynomial(degree=2)
    model = UOFR(n_terms=15, basis_function=basis_function, order_selection=False)
    model.fit(X=x, y=y)
    assert model.info_values is None


def test_default_values():
    default = {
        "ylag": 2,
        "xlag": 2,
        "order_selection": True,
        "info_criteria": "aic",
        "n_terms": None,
        "n_info_values": 15,
        "eps": np.finfo(np.float64).eps,
        "alpha": 0,
        "model_type": "NARMAX",
        "err_tol": None,
    }
    model = UOFR(basis_function=Polynomial(degree=2))
    model_values = [
        model.ylag,
        model.xlag,
        model.order_selection,
        model.info_criteria,
        model.n_terms,
        model.n_info_values,
        model.eps,
        model.alpha,
        model.model_type,
        model.err_tol,
    ]
    assert list(default.values()) == model_values
    assert isinstance(model.estimator, RecursiveLeastSquares)
    assert isinstance(model.basis_function, Polynomial)


def test_validate_ylag():
    assert_raises(ValueError, UOFR, ylag=-1, basis_function=Polynomial(degree=2))
    assert_raises(ValueError, UOFR, ylag=1.3, basis_function=Polynomial(degree=2))


def test_validate_xlag():
    assert_raises(ValueError, UOFR, xlag=-1, basis_function=Polynomial(degree=2))
    assert_raises(ValueError, UOFR, xlag=1.3, basis_function=Polynomial(degree=2))


def test_model_order_selection():
    assert_raises(
        TypeError, UOFR, order_selection=1, basis_function=Polynomial(degree=2)
    )
    assert_raises(
        TypeError, UOFR, order_selection="True", basis_function=Polynomial(degree=2)
    )
    assert_raises(
        TypeError, UOFR, order_selection=None, basis_function=Polynomial(degree=2)
    )


def test_n_terms():
    assert_raises(ValueError, UOFR, n_terms=1.2, basis_function=Polynomial(degree=2))
    assert_raises(ValueError, UOFR, n_terms=-1, basis_function=Polynomial(degree=2))


def test_n_info_values():
    assert_raises(
        ValueError, UOFR, n_info_values=1.2, basis_function=Polynomial(degree=2)
    )
    assert_raises(
        ValueError, UOFR, n_info_values=-1, basis_function=Polynomial(degree=2)
    )


def test_info_criteria():
    assert_raises(
        ValueError, UOFR, info_criteria="AIC", basis_function=Polynomial(degree=2)
    )


def test_predict():
    basis_function = Polynomial(degree=2)
    model = UOFR(
        err_tol=None,
        ylag=[1, 2],
        xlag=2,
        estimator=LeastSquares(),
        basis_function=basis_function,
    )
    model.fit(X=X_train, y=y_train)
    yhat = model.predict(X=X_test, y=y_test)
    assert_almost_equal(yhat, y_test, decimal=10)


def test_model_prediction():
    basis_function = Polynomial(degree=2)
    model = UOFR(
        n_terms=5,
        ylag=[1, 2],
        xlag=2,
        estimator=LeastSquares(),
        basis_function=basis_function,
    )
    model.fit(X=X_train, y=y_train)
    assert_raises(Exception, model.predict, X=X_test, y=y_test[:1])


def test_information_criteria_bic():
    basis_function = Polynomial(degree=2)
    model = UOFR(
        n_terms=5,
        order_selection=True,
        info_criteria="bic",
        n_info_values=5,
        ylag=[1, 2],
        xlag=2,
        estimator=LeastSquares(),
        basis_function=basis_function,
    )
    model.fit(X=x, y=y)
    info_values = np.array([-1764.885, -2320.101, -2976.391, -4461.908, -72845.768])
    assert_almost_equal(model.info_values[:4], info_values[:4], decimal=3)


def test_information_criteria_aicc():
    basis_function = Polynomial(degree=2)
    model = UOFR(
        n_terms=5,
        order_selection=True,
        info_criteria="aicc",
        n_info_values=5,
        ylag=[1, 2],
        xlag=2,
        estimator=LeastSquares(),
        basis_function=basis_function,
    )
    model.fit(X=x, y=y)
    info_values = np.array([-1769.787, -2329.901, -2991.084, -4481.490])
    assert_almost_equal(model.info_values[:4], info_values[:4], decimal=3)


def test_information_criteria_fpe():
    basis_function = Polynomial(degree=2)
    model = UOFR(
        n_terms=5,
        order_selection=True,
        info_criteria="fpe",
        n_info_values=5,
        ylag=[1, 2],
        xlag=2,
        estimator=LeastSquares(),
        basis_function=basis_function,
    )
    model.fit(X=x, y=y)
    info_values = np.array(
        [-1769.7907932, -2329.9129013, -2991.1078281, -4481.5306067, -72870.296884]
    )
    assert_almost_equal(model.info_values[:4], info_values[:4], decimal=3)


def test_information_criteria_lilc():
    basis_function = Polynomial(degree=2)
    model = UOFR(
        n_terms=5,
        order_selection=True,
        info_criteria="lilc",
        n_info_values=5,
        ylag=[1, 2],
        xlag=2,
        estimator=LeastSquares(),
        basis_function=basis_function,
    )
    model.fit(X=x, y=y)
    info_values = np.array([-1767.926, -2326.183, -2985.514, -4474.072, -72860.973])
    assert_almost_equal(model.info_values[:4], info_values[:4], decimal=3)
