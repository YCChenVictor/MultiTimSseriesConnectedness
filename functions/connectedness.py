"""
     1    2    3
1    a    b    c

2

3

b means volatility of 2 cause volatility of 1
"""


# import required modules
import numpy as np
import pandas as pd
import os
import functions.f_about_path as fap
import json


# load Prerequisite
file_dir = os.path.dirname(os.path.abspath(__file__))
parent_path = fap.f_parent_path(file_dir, 1)
with open(parent_path + '/docs' + '/Prerequisite.json') as f:
    prerequisite = json.load(f)
# print(prerequisite)
target_folder = prerequisite['target_folder']


# simple version for working with CWD
file_path = os.path.dirname(os.path.realpath(__file__))
parent_path = fap.f_parent_path(file_path, 1)
save_path = parent_path + '/docs/' + target_folder
n_instruments = sum([len(files) for r, d, files in os.walk(save_path)])
# print(n_instruments)


# connectedness
def var_p_to_var_1(ai_list):
    """
    :param ai_list: the Coef calculated
    :return: the coef of VAR1
    """
    ar1_coef = np.zeros((n_instruments, 1))
    for coef_i in ai_list:
        # print(coef_i.shape)
        ar1_coef = np.column_stack((ar1_coef, coef_i))
        # print(ar1_coef)
    ar1_coef = np.delete(ar1_coef, 0, 1)
    nrow = ar1_coef.shape[0]
    lag = len(ai_list)
    n = nrow * lag
    ar1_coef_down = np.identity(n)
    ar1_coef_down = np.delete(ar1_coef_down, np.s_[(n-nrow):n], 0)
    ar1_coef = np.vstack((ar1_coef, ar1_coef_down))
    return ar1_coef


def ar1_coef_to_psi(coef, h=1):
    """
    :param coef: the coef estimated
    :param h: the period of predicted future from now
    :return: The mechanism of periods to periods
    """
    n = coef.shape[0]
    lag = coef.shape[1]/n
    i_k = np.identity(n)
    zeros = np.zeros((n, coef.shape[1]-n))
    j = np.column_stack((i_k, zeros))
    ai_list = []
    for i in range(1, int(lag) + 1):
        ai_list.append(coef[:, 0:n])
        coef = np.delete(coef, np.s_[0:7], 1)
    ar1_coef = var_p_to_var_1(ai_list)
    psi = []
    psi.append(i_k)
    big_i = np.identity(ar1_coef.shape[1])
    for i in range(2, h+2):
        big_i = np.dot(big_i, ar1_coef)
        psi.append(np.dot(np.dot(j, big_i), j.transpose()))
    return psi


def theta(coef, sigma_hat, h=1):
    p = np.linalg.cholesky(sigma_hat)
    n = coef.shape[0]
    matrix = np.zeros(shape=(n, n))
    row, col = np.diag_indices(matrix.shape[0])
    matrix[row, col] = np.diagonal(p)
    inv = np.linalg.inv(matrix).transpose()
    psi = ar1_coef_to_psi(coef, h)
    theta_unit = []
    theta_std = []
    for i in range(0, (h+1)):  # must use append
        theta_std.append(np.dot(psi[i], p))
        theta_unit.append(np.dot(np.dot(psi[i], p), inv))
    return theta_unit, theta_std


def generalized_variance_decomp(m, coef, sigma_hat, h=1):
    n = coef.shape[0]
    i_k = np.identity(n)
    m_i = i_k[:, (m-1)]
    psi = ar1_coef_to_psi(coef, h)
    theta_value = theta(coef, sigma_hat, h)[1]
    diag = np.diagonal(sigma_hat)
    inv_sigma2 = 1/diag
    # i = 0
    den = []
    num = []
    decomp = []
    den_fill = (np.linalg.
                multi_dot((m_i, theta_value[0], theta_value[0].T,
                          m_i[np.newaxis].T)))
    den.append(den_fill)
    num_fill = np.square(np.linalg.multi_dot((m_i, psi[0], sigma_hat)))
    num.append(num_fill)
    decomp.append(num_fill * inv_sigma2 / den_fill)
    for l in range(1, h):
        den_fill = den[l-1] + (np.linalg.
                               multi_dot((m_i, theta_value[l], theta_value[l].T,
                                          m_i[np.newaxis].T)))
        den.append(den_fill)
        num_fill = (np.square(np.linalg.multi_dot((m_i, psi[l], sigma_hat))) +
                    num[l-1])
        num.append(num_fill)
        decomp.append(num_fill*inv_sigma2/den_fill)
    return decomp


class Connectedness:

    def __init__(self, coef, sigma_hat):

        # the varilables required to lauch this class
        self.Coef = coef
        self.Sigma_hat = sigma_hat

        # return the Full_Connectedness
        self.full_connectedness = None

        # restructure into flat shape
        self.flat_connectedness = None

    def f_full_connectedness(self, h=1):

        # input required variable
        coef = self.Coef
        sigma_hat = self.Sigma_hat

        # the number of time series data
        n = coef.shape[0]

        # start to calculate connectedness
        connectedness = []

        # obtain the generalized variance decomposition after 5 periods
        # each variable fluctuates one time
        for i in range(1, (n + 1)):
            GVD = generalized_variance_decomp(i, coef, sigma_hat, h)[h - 1]
            connectedness.append(GVD)

        # transpose
        connectedness = np.array(connectedness).T

        # rescale each row to summation of 1
        for i in range(len(connectedness)):
            connectedness[i] = connectedness[i]/np.sum(connectedness[i])

        # calculate from_other
        from_other = []
        for i in range(0, len(connectedness)):
            connectedness_value = connectedness[i]
            from_other_value = 1 - connectedness_value[i]
            from_other.append(from_other_value)

        # calculated to_other
        to_other = []
        connectedness_tran = np.array(connectedness).T
        for i in range(0, len(connectedness)):
            connectedness_value = connectedness_tran[i]
            to_other_value = np.sum(connectedness_value) - connectedness_value[i]
            to_other.append(to_other_value)

        # spill over index (total connectedness)
        spill_over = np.sum(from_other) / n
        np.matrix(from_other).transpose()
        up = np.concatenate((np.matrix(connectedness), np.matrix(from_other).transpose()), axis=1)
        down = np.concatenate((np.matrix(to_other), np.matrix(spill_over)), axis=1)
        connectedness_table = np.concatenate((up, down), axis=0)

        self.full_connectedness = pd.DataFrame(connectedness_table)

    def rename_table(self, names):
        full_connectedness = self.full_connectedness
        full_connectedness.columns = names
        full_connectedness.rename(index=dict(
                                  zip(full_connectedness.index, names)),
                                  inplace=True)

    def table_restructure(self):

        connectedness = self.full_connectedness

        # get the names specify the direction of a connectedness
        col_names = list(connectedness.columns.values)
        row_names = list(connectedness.index)

        name_list = []
        for col_name in col_names:
            for row_name in row_names:
                name = col_name + "->" + row_name
                name_list.append(name)

        # get the connectedness value
        connectedness_flat = pd.DataFrame(connectedness.values.flatten())
        connectedness_flat = connectedness_flat.transpose()
        connectedness_flat.columns = name_list

        self.flat_connectedness = connectedness_flat
