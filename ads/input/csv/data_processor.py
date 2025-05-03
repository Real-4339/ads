import os
import pandas as pd


class DataProcessor:
    exist = False

    def __init__(self, filename, blg: bool = False):
        self.root = os.getcwd() + "/ads/input/csv/files/"
        self.file = self.root + filename

        if self._check_file_existence(filename):
            return

        if blg:
            self._get_bgl_data(self.file)
        else:
            self._get_access_data(self.file)

        self.df = self.df.sort_values(by="raw_datetime")

        self.df["date"] = self.df["raw_datetime"].dt.date
        self.grouped = self.df.groupby("date")

        self._compute_all_formats()

    def _check_file_existence(self, filename):
        if os.path.exists(self.file + "_train_data.pkl"):
            print(filename, "exist")
            self.exist = True
            return True

    def _get_bgl_data(self, file):
        self.df = pd.read_csv(
            file + ".log",
            sep="\s+",
            header=None,
            encoding="latin1",
            usecols=[4],
            on_bad_lines="skip",
            names=["raw_datetime"],
        )

        self.df["raw_datetime"] = pd.to_datetime(
            self.df["raw_datetime"], format="%Y-%m-%d-%H.%M.%S.%f"
        )

    def _get_access_data(self, file):
        self.df = pd.read_csv(
            file + ".log",
            sep="\s+",
            header=None,
            encoding="latin1",
            usecols=[3],
            on_bad_lines="skip",
            names=["raw_datetime"],
        )

        self.df["raw_datetime"] = pd.to_datetime(
            self.df["raw_datetime"].str.strip("[]"), format="%d/%b/%Y:%H:%M:%S"
        )

    def _compute_all_formats(self):

        self.df["epoch"] = self.df["raw_datetime"].apply(
            lambda x: float(int(x.timestamp()))
        )

        min_epoch = self.df["epoch"].min()
        self.df["relative_time"] = self.df["epoch"] - min_epoch

        self.df["time_diff"] = (
            self.df["raw_datetime"].diff().dt.total_seconds().fillna(0)
        )

        self._create_train_val_test_sets()

    def _create_train_val_test_sets(self):
        not_to_include = ["date", "raw_datetime"]

        def extract_data(column):
            return [
                self.grouped.get_group(group)[column]
                for group in list(self.grouped.groups.keys())
            ]

        self.train_data = {
            col: pd.concat(extract_data(col)[:7])
            for col in self.df.columns
            if col not in not_to_include
        }
        self.val_data = {
            col: pd.concat(extract_data(col)[7:14])
            for col in self.df.columns
            if col not in not_to_include
        }
        self.test_data = {
            col: pd.concat(extract_data(col)[14:21])
            for col in self.df.columns
            if col not in not_to_include
        }

    def save_to_files(self):
        train_file = os.path.join(self.root, self.file + "_train_data.pkl")
        val_file = os.path.join(self.root, self.file + "_val_data.pkl")
        test_file = os.path.join(self.root, self.file + "_test_data.pkl")

        train_df = pd.DataFrame(self.train_data)
        val_df = pd.DataFrame(self.val_data)
        test_df = pd.DataFrame(self.test_data)

        # Save as pickle
        train_df.to_pickle(train_file)
        val_df.to_pickle(val_file)
        test_df.to_pickle(test_file)
