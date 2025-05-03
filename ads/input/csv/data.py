import os
import numpy as np
import pandas as pd


class Data:
    def __init__(self):
        self.root = os.getcwd() + "/ads/input/csv/files/"
        self.bgl_train: pd.DataFrame = None
        self.bgl_val: pd.DataFrame = None
        self.bgl_test: pd.DataFrame = None

        self.brute_train: pd.DataFrame = None
        self.brute_val: pd.DataFrame = None
        self.brute_test: pd.DataFrame = None

        self.secrepo_train: pd.DataFrame = None
        self.secrepo_val: pd.DataFrame = None
        self.secrepo_test: pd.DataFrame = None

    def _load_npy(self):
        """Deprecated"""
        self.bgl_train = np.load(self.root + "bgl_train_data.npy", allow_pickle=True)
        self.bgl_val = np.load(self.root + "bgl_val_data.npy", allow_pickle=True)
        self.bgl_test = np.load(self.root + "bgl_test_data.npy", allow_pickle=True)

        self.brute_train = np.load(
            self.root + "brute_forse_train_data.npy", allow_pickle=True
        )

        self.brute_val = np.load(
            self.root + "brute_forse_val_data.npy", allow_pickle=True
        )
        self.brute_test = np.load(
            self.root + "brute_forse_test_data.npy", allow_pickle=True
        )

        self.secrepo_train = np.load(
            self.root + "secrepo_access_train_data.npy", allow_pickle=True
        )
        self.secrepo_val = np.load(
            self.root + "secrepo_access_val_data.npy", allow_pickle=True
        )
        self.secrepo_test = np.load(
            self.root + "secrepo_access_test_data.npy", allow_pickle=True
        )

    def load(self):

        self.bgl_train = pd.read_pickle(self.root + "bgl_train_data.pkl")
        self.bgl_val = pd.read_pickle(self.root + "bgl_val_data.pkl")
        self.bgl_test = pd.read_pickle(self.root + "bgl_test_data.pkl")

        self.brute_train = pd.read_pickle(self.root + "brute_forse_train_data.pkl")
        self.brute_val = pd.read_pickle(self.root + "brute_forse_val_data.pkl")
        self.brute_test = pd.read_pickle(self.root + "brute_forse_test_data.pkl")

        self.secrepo_train = pd.read_pickle(self.root + "secrepo_access_train_data.pkl")
        self.secrepo_val = pd.read_pickle(self.root + "secrepo_access_val_data.pkl")
        self.secrepo_test = pd.read_pickle(self.root + "secrepo_access_test_data.pkl")

    def get_epoch(self, dataset) -> np.ndarray:
        return dataset["epoch"].values

    def get_relative(self, dataset) -> np.ndarray:
        return dataset["relative_time"].values

    def get_diff(self, dataset) -> np.ndarray:
        return dataset["time_diff"].values
