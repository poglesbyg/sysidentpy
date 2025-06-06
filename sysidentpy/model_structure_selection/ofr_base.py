"""Base methods for Orthogonal Forward Regression algorithm."""

# Authors:
#           Wilson Rocha Lacerda Junior <wilsonrljr@outlook.com>
# License: BSD 3 clause

import warnings
from abc import ABCMeta, abstractmethod
from typing import Union, Tuple, Optional

import numpy as np

from sysidentpy.narmax_base import house, rowhouse
from sysidentpy.utils.information_matrix import build_lagged_matrix
from sysidentpy.utils.check_arrays import check_positive_int, num_features

from ..basis_function import Fourier, Polynomial
from ..narmax_base import BaseMSS
from ..parameter_estimation.estimators import (
    LeastSquares,
    RidgeRegression,
    RecursiveLeastSquares,
    TotalLeastSquares,
    LeastMeanSquareMixedNorm,
    LeastMeanSquares,
    LeastMeanSquaresFourth,
    LeastMeanSquaresLeaky,
    LeastMeanSquaresNormalizedLeaky,
    LeastMeanSquaresNormalizedSignRegressor,
    LeastMeanSquaresNormalizedSignSign,
    LeastMeanSquaresSignError,
    LeastMeanSquaresSignSign,
    AffineLeastMeanSquares,
    NormalizedLeastMeanSquares,
    NormalizedLeastMeanSquaresSignError,
    LeastMeanSquaresSignRegressor,
)

Estimators = Union[
    LeastSquares,
    RidgeRegression,
    RecursiveLeastSquares,
    TotalLeastSquares,
    LeastMeanSquareMixedNorm,
    LeastMeanSquares,
    LeastMeanSquaresFourth,
    LeastMeanSquaresLeaky,
    LeastMeanSquaresNormalizedLeaky,
    LeastMeanSquaresNormalizedSignRegressor,
    LeastMeanSquaresNormalizedSignSign,
    LeastMeanSquaresSignError,
    LeastMeanSquaresSignSign,
    AffineLeastMeanSquares,
    NormalizedLeastMeanSquares,
    NormalizedLeastMeanSquaresSignError,
    LeastMeanSquaresSignRegressor,
]


def fpe(n_theta: int, n_samples: int, e_var: float) -> float:
    """Compute the Final Error Prediction value.

    Parameters
    ----------
    n_theta : int
        Number of parameters of the model.
    n_samples : int
        Number of samples given the maximum lag.
    e_var : float
        Variance of the residues

    Returns
    -------
    info_criteria_value : float
        The computed value given the information criteria selected by the
        user.

    """
    model_factor = n_samples * np.log((n_samples + n_theta) / (n_samples - n_theta))
    e_factor = n_samples * np.log(e_var)
    info_criteria_value = e_factor + model_factor

    return info_criteria_value


def lilc(n_theta: int, n_samples: int, e_var: float) -> float:
    """Compute the Lilc information criteria value.

    Parameters
    ----------
    n_theta : int
        Number of parameters of the model.
    n_samples : int
        Number of samples given the maximum lag.
    e_var : float
        Variance of the residues

    Returns
    -------
    info_criteria_value : float
        The computed value given the information criteria selected by the
        user.

    """
    model_factor = 2 * n_theta * np.log(np.log(n_samples))
    e_factor = n_samples * np.log(e_var)
    info_criteria_value = e_factor + model_factor

    return info_criteria_value


def get_min_info_value(info_values):
    """Find the index of the first increasing value in an array.

    Parameters
    ----------
    info_values : array-like
        A sequence of numeric values to be analyzed.

    Returns
    -------
    int
        The index of the first element where the values start to increase
        monotonically. If no such element exists, the length of
        `info_values` is returned.

    Notes
    -----
    - The function assumes that `info_values` is a 1-dimensional array-like
    structure.
    - The function uses `np.diff` to compute the difference between consecutive
    elements in the sequence.
    - The function checks if any differences are positive, indicating an increase
    in value.

    Examples
    --------
    >>> class MyClass:
    ...     def __init__(self, values):
    ...         self.info_values = values
    ...     def get_min_info_value(self):
    ...         is_monotonique = np.diff(self.info_values) > 0
    ...         if any(is_monotonique):
    ...             return np.where(is_monotonique)[0][0] + 1
    ...         return len(self.info_values)
    >>> instance = MyClass([3, 2, 1, 4, 5])
    >>> instance.get_min_info_value()
    3
    """
    is_monotonique = np.diff(info_values) > 0
    if any(is_monotonique):
        return np.where(is_monotonique)[0][0] + 1
    return len(info_values)


def aic(n_theta: int, n_samples: int, e_var: float) -> float:
    """Compute the Akaike information criteria value.

    Parameters
    ----------
    n_theta : int
        Number of parameters of the model.
    n_samples : int
        Number of samples given the maximum lag.
    e_var : float
        Variance of the residues

    Returns
    -------
    info_criteria_value : float
        The computed value given the information criteria selected by the
        user.

    """
    model_factor = 2 * n_theta
    e_factor = n_samples * np.log(e_var)
    info_criteria_value = e_factor + model_factor

    return info_criteria_value


def aicc(n_theta: int, n_samples: int, e_var: float) -> float:
    """Compute the Akaike information Criteria corrected value.

    Parameters
    ----------
    n_theta : int
        Number of parameters of the model.
    n_samples : int
        Number of samples given the maximum lag.
    e_var : float
        Variance of the residues

    Returns
    -------
    aicc : float
        The computed aicc value.

    References
    ----------
    - https://www.mathworks.com/help/ident/ref/idmodel.aic.html

    """
    aic_values = aic(n_theta, n_samples, e_var)
    aicc_values = aic_values + (2 * n_theta * (n_theta + 1) / (n_samples - n_theta - 1))

    return aicc_values


def bic(n_theta: int, n_samples: int, e_var: float) -> float:
    """Compute the Bayesian information criteria value.

    Parameters
    ----------
    n_theta : int
        Number of parameters of the model.
    n_samples : int
        Number of samples given the maximum lag.
    e_var : float
        Variance of the residues

    Returns
    -------
    info_criteria_value : float
        The computed value given the information criteria selected by the
        user.

    """
    model_factor = n_theta * np.log(n_samples)
    e_factor = n_samples * np.log(e_var)
    info_criteria_value = e_factor + model_factor

    return info_criteria_value


def get_info_criteria(info_criteria: str):
    """Get info criteria."""
    info_criteria_options = {
        "aic": aic,
        "aicc": aicc,
        "bic": bic,
        "fpe": fpe,
        "lilc": lilc,
    }
    return info_criteria_options.get(info_criteria)


class OFRBase(BaseMSS, metaclass=ABCMeta):
    """Base class for Model Structure Selection."""

    @abstractmethod
    def __init__(
        self,
        *,
        ylag: Union[int, list] = 2,
        xlag: Union[int, list] = 2,
        elag: Union[int, list] = 2,
        order_selection: bool = True,
        info_criteria: str = "aic",
        n_terms: Union[int, None] = None,
        n_info_values: int = 15,
        estimator: Estimators = RecursiveLeastSquares(),
        basis_function: Union[Polynomial, Fourier] = Polynomial(),
        model_type: str = "NARMAX",
        eps: np.float64 = np.finfo(np.float64).eps,
        alpha: float = 0,
        err_tol: Optional[float] = None,
    ):
        self.order_selection = order_selection
        self.ylag = ylag
        self.xlag = xlag
        self.max_lag = self._get_max_lag()
        self.info_criteria = info_criteria
        self.info_criteria_function = get_info_criteria(info_criteria)
        self.n_info_values = n_info_values
        self.n_terms = n_terms
        self.estimator = estimator
        self.elag = elag
        self.model_type = model_type
        self.basis_function = basis_function
        self.eps = eps
        if isinstance(self.estimator, RidgeRegression):
            self.alpha = self.estimator.alpha
        else:
            self.alpha = alpha

        self.err_tol = err_tol
        self._validate_params()
        self.n_inputs = None
        self.regressor_code = None
        self.info_values = None
        self.err = None
        self.final_model = None
        self.theta = None
        self.pivv = None

    def _validate_params(self):
        """Validate input params."""
        if not isinstance(self.n_info_values, int) or self.n_info_values < 1:
            raise ValueError(
                f"n_info_values must be integer and > zero. Got {self.n_info_values}"
            )

        if isinstance(self.ylag, int) and self.ylag < 1:
            raise ValueError(f"ylag must be integer and > zero. Got {self.ylag}")

        if isinstance(self.xlag, int) and self.xlag < 1:
            raise ValueError(f"xlag must be integer and > zero. Got {self.xlag}")

        if not isinstance(self.xlag, (int, list)):
            raise ValueError(f"xlag must be integer and > zero. Got {self.xlag}")

        if not isinstance(self.ylag, (int, list)):
            raise ValueError(f"ylag must be integer and > zero. Got {self.ylag}")

        if not isinstance(self.order_selection, bool):
            raise TypeError(
                f"order_selection must be False or True. Got {self.order_selection}"
            )

        if self.info_criteria not in ["aic", "aicc", "bic", "fpe", "lilc"]:
            raise ValueError(
                f"info_criteria must be aic, bic, fpe or lilc. Got {self.info_criteria}"
            )

        if self.model_type not in ["NARMAX", "NAR", "NFIR"]:
            raise ValueError(
                f"model_type must be NARMAX, NAR or NFIR. Got {self.model_type}"
            )

        if (
            not isinstance(self.n_terms, int) or self.n_terms < 1
        ) and self.n_terms is not None:
            raise ValueError(f"n_terms must be integer and > zero. Got {self.n_terms}")

        if not isinstance(self.eps, float) or self.eps < 0:
            raise ValueError(f"eps must be float and > zero. Got {self.eps}")

    @abstractmethod
    def run_mss_algorithm(
        self, psi: np.ndarray, y: np.ndarray, process_term_number: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.error_reduction_ratio(psi, y, process_term_number)

    def error_reduction_ratio(
        self, psi: np.ndarray, y: np.ndarray, process_term_number: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Perform the Error Reduction Ration algorithm.

        Parameters
        ----------
        y : array-like of shape = n_samples
            The target data used in the identification process.
        psi : ndarray of floats
            The information matrix of the model.
        process_term_number : int
            Number of Process Terms defined by the user.

        Returns
        -------
        err : array-like of shape = number_of_model_elements
            The respective ERR calculated for each regressor.
        piv : array-like of shape = number_of_model_elements
            Contains the index to put the regressors in the correct order
            based on err values.
        psi_orthogonal : ndarray of floats
            The updated and orthogonal information matrix.

        References
        ----------
        - Manuscript: Orthogonal least squares methods and their application
           to non-linear system identification
           https://eprints.soton.ac.uk/251147/1/778742007_content.pdf
        - Manuscript (portuguese): Identificação de Sistemas não Lineares
           Utilizando Modelos NARMAX Polinomiais - Uma Revisão
           e Novos Resultados

        """
        squared_y = np.dot(y[self.max_lag :].T, y[self.max_lag :])
        tmp_psi = psi.copy()
        y = y[self.max_lag :, 0].reshape(-1, 1)
        tmp_y = y.copy()
        dimension = tmp_psi.shape[1]
        piv = np.arange(dimension)
        tmp_err = np.zeros(dimension)
        err = np.zeros(dimension)

        for i in np.arange(0, dimension):
            for j in np.arange(i, dimension):
                # Add `eps` in the denominator to omit division by zero if
                # denominator is zero
                # To implement regularized regression (ridge regression), add
                # alpha to psi.T @ psi.   See S. Chen, Local regularization assisted
                # orthogonal least squares regression, Neurocomputing 69 (2006) 559-585.
                # The version implemented below uses the same regularization for every
                # feature, # What Chen refers to Uniform regularized orthogonal least
                # squares (UROLS) Set to tiny (self.eps) when you are not regularizing.
                # alpha = eps is the default.
                tmp_err[j] = (
                    (np.dot(tmp_psi[i:, j].T, tmp_y[i:]) ** 2)
                    / (
                        (np.dot(tmp_psi[i:, j].T, tmp_psi[i:, j]) + self.alpha)
                        * squared_y
                    )
                    + self.eps
                )[0, 0]

            piv_index = np.argmax(tmp_err[i:]) + i
            err[i] = tmp_err[piv_index]
            if i == process_term_number:
                break

            if (self.err_tol is not None) and (err.cumsum()[i] >= self.err_tol):
                self.n_terms = i + 1
                process_term_number = i + 1
                break

            tmp_psi[:, [piv_index, i]] = tmp_psi[:, [i, piv_index]]
            piv[[piv_index, i]] = piv[[i, piv_index]]
            v = house(tmp_psi[i:, i])
            row_result = rowhouse(tmp_psi[i:, i:], v)
            tmp_y[i:] = rowhouse(tmp_y[i:], v)
            tmp_psi[i:, i:] = np.copy(row_result)

        tmp_piv = piv[0:process_term_number]
        psi_orthogonal = psi[:, tmp_piv]
        return err, tmp_piv, psi_orthogonal

    def information_criterion(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Determine the model order.

        This function uses a information criterion to determine the model size.
        'Akaike'-  Akaike's Information Criterion with
                   critical value 2 (AIC) (default).
        'Bayes' -  Bayes Information Criterion (BIC).
        'FPE'   -  Final Prediction Error (FPE).
        'LILC'  -  Khundrin's law ofiterated logarithm criterion (LILC).

        Parameters
        ----------
        y : array-like of shape = n_samples
            Target values of the system.
        x : array-like of shape = n_samples
            Input system values measured by the user.

        Returns
        -------
        output_vector : array-like of shape = n_regressor
            Vector with values of akaike's information criterion
            for models with N terms (where N is the
            vector position + 1).

        """
        if self.n_info_values is not None and self.n_info_values > x.shape[1]:
            self.n_info_values = x.shape[1]
            warnings.warn(
                "n_info_values is greater than the maximum number of all"
                " regressors space considering the chosen y_lag, u_lag, and"
                f" non_degree. We set as {x.shape[1]}",
                stacklevel=2,
            )

        output_vector = np.zeros(self.n_info_values)
        output_vector[:] = np.nan

        n_samples = len(y) - self.max_lag

        for i in range(self.n_info_values):
            n_theta = i + 1
            regressor_matrix = self.run_mss_algorithm(x, y, n_theta)[2]

            tmp_theta = self.estimator.optimize(
                regressor_matrix, y[self.max_lag :, 0].reshape(-1, 1)
            )

            tmp_yhat = np.dot(regressor_matrix, tmp_theta)
            tmp_residual = y[self.max_lag :] - tmp_yhat
            e_var = np.var(tmp_residual, ddof=1)
            output_vector[i] = self.info_criteria_function(n_theta, n_samples, e_var)

        return output_vector

    def fit(self, *, X: Optional[np.ndarray] = None, y: np.ndarray):
        """Fit polynomial NARMAX model.

        This is an 'alpha' version of the 'fit' function which allows
        a friendly usage by the user. Given two arguments, x and y, fit
        training data.

        Parameters
        ----------
        X : ndarray of floats
            The input data to be used in the training process.
        y : ndarray of floats
            The output data to be used in the training process.

        Returns
        -------
        model : ndarray of int
            The model code representation.
        piv : array-like of shape = number_of_model_elements
            Contains the index to put the regressors in the correct order
            based on err values.
        theta : array-like of shape = number_of_model_elements
            The estimated parameters of the model.
        err : array-like of shape = number_of_model_elements
            The respective ERR calculated for each regressor.
        info_values : array-like of shape = n_regressor
            Vector with values of akaike's information criterion
            for models with N terms (where N is the
            vector position + 1).

        """
        if y is None:
            raise ValueError("y cannot be None")

        self.max_lag = self._get_max_lag()
        lagged_data = build_lagged_matrix(X, y, self.xlag, self.ylag, self.model_type)

        reg_matrix = self.basis_function.fit(
            lagged_data,
            self.max_lag,
            self.ylag,
            self.xlag,
            self.model_type,
            predefined_regressors=None,
        )

        if X is not None:
            self.n_inputs = num_features(X)
        else:
            self.n_inputs = 1  # just to create the regressor space base

        self.regressor_code = self.regressor_space(self.n_inputs)

        if self.order_selection is True:
            self.info_values = self.information_criterion(reg_matrix, y)

        if self.n_terms is None and self.order_selection is True:
            model_length = get_min_info_value(self.info_values)
            self.n_terms = model_length
        elif self.n_terms is None and self.order_selection is not True:
            raise ValueError(
                "If order_selection is False, you must define n_terms value."
            )
        else:
            model_length = self.n_terms

        (self.err, self.pivv, psi) = self.run_mss_algorithm(reg_matrix, y, model_length)

        tmp_piv = self.pivv[0:model_length]
        repetition = len(reg_matrix)
        if isinstance(self.basis_function, Polynomial):
            self.final_model = self.regressor_code[tmp_piv, :].copy()
        else:
            self.regressor_code = np.sort(
                np.tile(self.regressor_code[1:, :], (repetition, 1)),
                axis=0,
            )
            self.final_model = self.regressor_code[tmp_piv, :].copy()

        self.theta = self.estimator.optimize(psi, y[self.max_lag :, 0].reshape(-1, 1))
        if self.estimator.unbiased is True:
            self.theta = self.estimator.unbiased_estimator(
                psi,
                y[self.max_lag :, 0].reshape(-1, 1),
                self.theta,
                self.elag,
                self.max_lag,
                self.estimator,
                self.basis_function,
                self.estimator.uiter,
            )
        return self

    def predict(
        self,
        *,
        X: Optional[np.ndarray] = None,
        y: np.ndarray,
        steps_ahead: Optional[int] = None,
        forecast_horizon: Optional[int] = None,
    ) -> np.ndarray:
        """Return the predicted values given an input.

        The predict function allows a friendly usage by the user.
        Given a previously trained model, predict values given
        a new set of data.

        This method accept y values mainly for prediction n-steps ahead
        (to be implemented in the future)

        Parameters
        ----------
        X : ndarray of floats
            The input data to be used in the prediction process.
        y : ndarray of floats
            The output data to be used in the prediction process.
        steps_ahead : int (default = None)
            The user can use free run simulation, one-step ahead prediction
            and n-step ahead prediction.
        forecast_horizon : int, default=None
            The number of predictions over the time.

        Returns
        -------
        yhat : ndarray of floats
            The predicted values of the model.

        """
        if isinstance(self.basis_function, Polynomial):
            if steps_ahead is None:
                yhat = self._model_prediction(X, y, forecast_horizon=forecast_horizon)
                yhat = np.concatenate([y[: self.max_lag], yhat], axis=0)
                return yhat
            if steps_ahead == 1:
                yhat = self._one_step_ahead_prediction(X, y)
                yhat = np.concatenate([y[: self.max_lag], yhat], axis=0)
                return yhat

            check_positive_int(steps_ahead, "steps_ahead")
            yhat = self._n_step_ahead_prediction(X, y, steps_ahead=steps_ahead)
            yhat = np.concatenate([y[: self.max_lag], yhat], axis=0)
            return yhat

        if steps_ahead is None:
            yhat = self._basis_function_predict(X, y, forecast_horizon)
            yhat = np.concatenate([y[: self.max_lag], yhat], axis=0)
            return yhat
        if steps_ahead == 1:
            yhat = self._one_step_ahead_prediction(X, y)
            yhat = np.concatenate([y[: self.max_lag], yhat], axis=0)
            return yhat

        yhat = self._basis_function_n_step_prediction(
            X, y, steps_ahead, forecast_horizon
        )
        yhat = np.concatenate([y[: self.max_lag], yhat], axis=0)
        return yhat

    def _one_step_ahead_prediction(
        self, x: Optional[np.ndarray], y: Optional[np.ndarray]
    ) -> np.ndarray:
        """Perform the 1-step-ahead prediction of a model.

        Parameters
        ----------
        y : array-like of shape = max_lag
            Initial conditions values of the model
            to start recursive process.
        x : ndarray of floats of shape = n_samples
            Vector with input values to be used in model simulation.

        Returns
        -------
        yhat : ndarray of floats
               The 1-step-ahead predicted values of the model.

        """
        lagged_data = build_lagged_matrix(x, y, self.xlag, self.ylag, self.model_type)

        x_base = self.basis_function.transform(
            lagged_data,
            self.max_lag,
            self.ylag,
            self.xlag,
            self.model_type,
            predefined_regressors=self.pivv[: len(self.final_model)],
        )

        yhat = super()._one_step_ahead_prediction(x_base)
        return yhat.reshape(-1, 1)

    def _n_step_ahead_prediction(
        self, x: Optional[np.ndarray], y: Optional[np.ndarray], steps_ahead: int
    ) -> float:
        """Perform the n-steps-ahead prediction of a model.

        Parameters
        ----------
        y : array-like of shape = max_lag
            Initial conditions values of the model
            to start recursive process.
        x : ndarray of floats of shape = n_samples
            Vector with input values to be used in model simulation.

        Returns
        -------
        yhat : ndarray of floats
               The n-steps-ahead predicted values of the model.

        """
        yhat = super()._n_step_ahead_prediction(x, y, steps_ahead)
        return yhat

    def _model_prediction(
        self,
        x: Optional[np.ndarray],
        y_initial: np.ndarray,
        forecast_horizon: int = 0,
    ) -> np.ndarray:
        """Perform the infinity steps-ahead simulation of a model.

        Parameters
        ----------
        y_initial : array-like of shape = max_lag
            Number of initial conditions values of output
            to start recursive process.
        x : ndarray of floats of shape = n_samples
            Vector with input values to be used in model simulation.

        Returns
        -------
        yhat : ndarray of floats
               The predicted values of the model.

        """
        if self.model_type in ["NARMAX", "NAR"]:
            return self._narmax_predict(x, y_initial, forecast_horizon)

        if self.model_type == "NFIR":
            return self._nfir_predict(x, y_initial)

        raise ValueError(
            f"model_type must be NARMAX, NAR or NFIR. Got {self.model_type}"
        )

    def _narmax_predict(
        self,
        x: Optional[np.ndarray],
        y_initial: np.ndarray,
        forecast_horizon: int = 0,
    ) -> np.ndarray:
        if len(y_initial) < self.max_lag:
            raise ValueError(
                "Insufficient initial condition elements! Expected at least"
                f" {self.max_lag} elements."
            )

        if x is not None:
            forecast_horizon = x.shape[0]
        else:
            forecast_horizon = forecast_horizon + self.max_lag

        if self.model_type == "NAR":
            self.n_inputs = 0

        y_output = super()._narmax_predict(x, y_initial, forecast_horizon)
        return y_output

    def _nfir_predict(
        self, x: Optional[np.ndarray], y_initial: Optional[np.ndarray]
    ) -> np.ndarray:
        y_output = super()._nfir_predict(x, y_initial)
        return y_output

    def _basis_function_predict(
        self,
        x: Optional[np.ndarray],
        y_initial: Optional[np.ndarray],
        forecast_horizon: int = 0,
    ) -> np.ndarray:
        if x is not None:
            forecast_horizon = x.shape[0]
        else:
            forecast_horizon = forecast_horizon + self.max_lag

        if self.model_type == "NAR":
            self.n_inputs = 0

        yhat = super()._basis_function_predict(x, y_initial, forecast_horizon)
        return yhat.reshape(-1, 1)

    def _basis_function_n_step_prediction(
        self,
        x: Optional[np.ndarray],
        y: np.ndarray,
        steps_ahead: Optional[int],
        forecast_horizon: int,
    ) -> np.ndarray:
        """Perform the n-steps-ahead prediction of a model.

        Parameters
        ----------
        y : array-like of shape = max_lag
            Initial conditions values of the model
            to start recursive process.
        x : ndarray of floats of shape = n_samples
            Vector with input values to be used in model simulation.

        Returns
        -------
        yhat : ndarray of floats
               The n-steps-ahead predicted values of the model.

        """
        if len(y) < self.max_lag:
            raise ValueError(
                "Insufficient initial condition elements! Expected at least"
                f" {self.max_lag} elements."
            )

        if x is not None:
            forecast_horizon = x.shape[0]
        else:
            forecast_horizon = forecast_horizon + self.max_lag

        yhat = super()._basis_function_n_step_prediction(
            x, y, steps_ahead, forecast_horizon
        )
        return yhat.reshape(-1, 1)

    def _basis_function_n_steps_horizon(
        self,
        x: Optional[np.ndarray],
        y: Optional[np.ndarray],
        steps_ahead: Optional[int],
        forecast_horizon: int,
    ) -> np.ndarray:
        yhat = super()._basis_function_n_steps_horizon(
            x, y, steps_ahead, forecast_horizon
        )
        return yhat.reshape(-1, 1)
