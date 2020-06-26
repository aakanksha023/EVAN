# author: Jasmine Qin and Xinwen Wang
# date: 2020-06-24

"""
This script performs will train the best model

Usage: src/03_modelling/011_modeling.py \
--file_path1=<file_path1> --file_path2=<file_path2> --file_path3=<file_path3> \
--save_to1=<save_to1> --save_to2=<save_to2> --save_model=<save_model>

Options:
--file_path1=<file_path1>        This is the file path for training set
--file_path2=<file_path2>        This is the file path for validation set
--file_path3=<file_path3>        This is the file path for test set
--save_to1=<save_to1>            This is the file path
                                    for the model performance
--save_to2=<save_to2>            This is the file path
                                    for the important features
--save_model=<save_model>        This is the file path
                                    the model will be saved
"""

# import library
# Basics
from docopt import docopt
import pandas as pd
import matplotlib.pyplot as plt
from joblib import dump

# Preprocessing
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Models
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier

# Pipeline
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Evaluation
from sklearn.metrics import plot_confusion_matrix, f1_score
from sklearn.metrics import recall_score, precision_score
from sklearn.metrics import classification_report

# Model Explanation
import eli5


opt = docopt(__doc__)


def main(file_path1, file_path2, file_path3,
         save_to1, save_to2, save_model):
    train = pd.read_csv(file_path1, low_memory=False)
    validation = pd.read_csv(file_path2, low_memory=False)
    # test = pd.read_csv(file_path3, low_memory=False)

    def feature_engineering(df):
        df = df[df.LocalArea.notnull()]
        return df.drop(columns=label), df['label']

    # df_list = [train, validation, test]
    df_list = [train, validation]
    for df in df_list:
        df.drop(columns=['business_id', 'BusinessName',
                         'BusinessTradeName', 'Status',
                         'BusinessSubType', 'Geom',
                         'NextYearStatus', 'BusinessIndustry'], inplace=True)

    # list all categorical varibles and numeric variables
    cat_vars = ['FOLDERYEAR', 'BusinessType', 'LocalArea']
    label = ['label']
    num_vars = [i for i in train.columns
                if i not in cat_vars and i not in label]

    # preprocessing techniques
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant',
                                  fill_value='missing')),
        ('onehot', OneHotEncoder(
            handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_vars),
            ('cat', categorical_transformer, cat_vars)
        ])

    X_train, y_train = feature_engineering(train)
    X_valid, y_valid = feature_engineering(validation)
    # X_test, y_test = feature_engineering(test)

    def evaluate_model(model, X_train=X_train, X_test=X_valid,
                       y_train=y_train, y_test=y_valid, verbose=True):
        """
        This function prints train and test accuracies,
        classification report, and confusion matrix.
        """
        model.fit(X_train, y_train)
        train_acc = model.score(X_train, y_train)
        test_acc = model.score(X_test, y_test)

        if verbose:
            print("Train Accuracy:", train_acc)
            print("Validation Accuracy", test_acc, "\n")

            print(classification_report(y_test, model.predict(X_test)))
            print(plot_confusion_matrix(model, X_test, y_test,
                                        display_labels=[0, 1],
                                        cmap=plt.cm.Blues,
                                        values_format='d'))
        else:
            report = {}
            f1 = f1_score(y_test, model.predict(X_test))
            recall = recall_score(y_test, model.predict(X_test))
            precision = precision_score(y_test, model.predict(X_test))
            report['renewed'] = [f1, recall, precision]

            f1 = f1_score(y_test, model.predict(X_test), pos_label=0)
            recall = recall_score(y_test, model.predict(X_test), pos_label=0)
            precision = precision_score(
                y_test, model.predict(X_test), pos_label=0)
            report['not_renewed'] = [f1, recall, precision]

            report['accuracy'] = [train_acc, test_acc]

            return report

    def convert_for_output(df):
        """
        This function convert the output of evaluate model
        to more concise form. It will return a confusion matrix
        and an accuracy matrix
        """
        renew_df = pd.DataFrame.from_dict(df['renewed'])
        renew_df.columns = ['renwed']
        renew_df['label'] = ['f1', 'recall', 'precision']
        renew_df.set_index('label', inplace=True)

        no_df = pd.DataFrame.from_dict(df['not_renewed'])
        no_df.columns = ['not_renwed']
        no_df['label'] = ['f1', 'recall', 'precision']
        no_df.set_index('label', inplace=True)

        confusion = pd.concat([renew_df, no_df], axis=1)

        accu = pd.DataFrame(df['accuracy'])
        accu.columns = ['accuracy']
        accu['label'] = ['train', 'validation']
        accu.set_index('label', inplace=True)

        return confusion, accu

    def explain_model(pip, df, verbose=True):
        """
        This function will output a pandas dataframe to
        show the important features and their weights in a model
        """
        pp1_features = num_vars + \
            list(pip['preprocessor'].transformers_[
                1][1]['onehot'].get_feature_names())

        return eli5.formatters.as_dataframe.explain_weights_df(
            pip['classifier'],
            feature_names=pp1_features,
            top=30)

    lr = LogisticRegression(solver='saga', class_weight='balanced')
    lr_pip = Pipeline(steps=[('preprocessor', preprocessor),
                             ('classifier', lr)])
    lr_performance = evaluate_model(lr_pip, verbose=False)
    lr_confusion, lr_accuracy = convert_for_output(lr_performance)

    lgbm = LGBMClassifier(class_weight='balanced')
    lgbm_pip = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', lgbm)])
    lgbm_performance = evaluate_model(lgbm_pip, verbose=False)
    lgbm_confusion, lgbm_accuracy = convert_for_output(lgbm_performance)
    lgbm_top_features = explain_model(lgbm_pip, X_train)

    df_list = [lr_confusion, lr_accuracy, lgbm_confusion, lgbm_accuracy]
    df_name = ['lr_confusion', 'lr_accuracy',
               'lgbm_confusion', 'lgbm_accuracy']
    writer = pd.ExcelWriter(save_to1)
    for i, df in enumerate(df_list):
        df.to_excel(writer, df_name[i])
    writer.save()
    lgbm_top_features.to_csv(save_to2, index=False)

    ######################
    # Save model to file # - JQ
    ######################

    X_train_valid = pd.concat([X_train, X_valid], ignore_index=True)
    y_train_valid = pd.concat([y_train, y_valid], ignore_index=True)

    lgbm_pip.fit(X_train_valid, y_train_valid)
    dump(lgbm_pip, save_model)


if __name__ == "__main__":
    main(opt["--file_path1"], opt["--file_path2"],
         opt["--file_path3"], opt["--save_to1"],
         opt["--save_to2"], opt["--save_model"])
