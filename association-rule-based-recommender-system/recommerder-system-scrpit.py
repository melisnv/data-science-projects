# libraries
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mlxtend.frequent_patterns import apriori,association_rules

pd.set_option("display.max_columns",None)
pd.set_option("display.width",500)
sns.set(rc={"figure.figsize":(12,12)})


def outlier_threshold(dataframe, column_name: str):
    '''
    This function extracts upper and lower threshold limits in the specific column of the dataframe

    :param dataframe: the dataframe
    :param column_name: the name of the column
    :type dataframe: pandas DataFrame
    :type column_name: string

    :returns: the lower limit and upper limit
    '''

    quartile1 = dataframe[column_name].quantile(0.01)
    quartile3 = dataframe[column_name].quantile(0.99)

    interquartile_range = quartile3 - quartile1  # a wide range

    up_limit = quartile3 * 1.5 + interquartile_range
    low_limit = quartile1 * 1.5 - interquartile_range

    return low_limit, up_limit


def replace_with_threshold(dataframe, column_name: str):
    '''
    This function selects and alters the data according to calculated threshold and assigns new value
    in the specific column of the dataframe

    :param dataframe: the dataframe
    :param column_name: the name of the column
    :type dataframe: pandas DataFrame
    :type column_name: string

    :returns:
    '''

    low_limit, up_limit = outlier_threshold(dataframe, column_name)

    dataframe.loc[(dataframe[column_name] < low_limit), column_name] = low_limit
    dataframe.loc[(dataframe[column_name] > up_limit), column_name] = up_limit


def data_preperation(dataframe):
    '''
    This function drops missing values and filters specific columns of the dataframe

    :param dataframe: the dataframe
    :type dataframe: pandas DataFrame

    :returns: filtered dataframe
    '''

    dataframe.dropna(inplace=True)
    dataframe = dataframe[
        ~dataframe["Invoice"].astype(str).str.contains("C", na=False)]  # data which does not contain C in the Invoice
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]

    replace_with_threshold(dataframe, "Quantity")
    replace_with_threshold(dataframe, "Price")

    return dataframe


def create_invoice_product(dataframe, id=False):
    '''
    This function creates invoice product by grouping and selecting specific columns

    :param dataframe: the dataframe
    :param id: the id of the product
    :type dataframe: pandas DataFrame
    :type id: Boolean

    :returns: invoice product dataframe
    '''

    if id:
        return dataframe.groupby(["Invoice", "StockCode"])["Quantity"].sum().unstack().fillna(0). \
            applymap(lambda x: 1 if x > 0 else 0)

    else:
        return dataframe.groupby(["Invoice", "Description"])["Quantity"].sum().unstack().fillna(0). \
            applymap(lambda x: 1 if x > 0 else 0)


def check_id(dataframe, stock_code: int):
    '''
    This function prints the name of the product

    :param dataframe: the dataframe
    :param stock_code: the code of the product
    :type dataframe: pandas DataFrame
    :type stock_code: int

    :prints: the name of the product
    '''

    product_name = dataframe[dataframe["StockCode"] == stock_code][["Description"]].values[0].tolist()
    print(product_name)


def create_rules(dataframe, id=True, country="France"):
    '''
        This function creates associated rules based on the country and calculated
         apriori of the data

        :param dataframe: the dataframe
        :param id: the id of the product
        :param country: name of the country
        :type dataframe: pandas DataFrame
        :type id: int
        :type country: str

        :returns: rules
        '''

    dataframe = dataframe[dataframe["Country"] == country]
    dataframe = create_invoice_product(dataframe, id)
    frequent_itemsets = apriori(dataframe, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)

    return rules


def arl_recommender(rules_df, product_id, rec_count=1):
    '''
        This function creates a recommendation list based on the calculated rules dataframe

        :param rules_df: the rules dataframe
        :param product_id: the id of the product
        :param rec_count: end point for recommendation list
        :type rules_df: pandas DataFrame
        :type product_id: int
        :type rec_count: int

        :returns: list of recommendations
    '''

    sorted_rules = rules_df.sort_values("lift", ascending=False)
    recommendation_list = []

    for i, product in enumerate(sorted_rules["antecedents"]):
        for j in list(product):
            if j == product_id:
                recommendation_list.append(list(sorted_rules.iloc[i]["consequents"])[0])

    return recommendation_list[0:rec_count]


df = pd.read_excel("online_retail_II.xlsx",sheet_name="Year 2010-2011")
data = df.copy()
data = data_preperation(data)
rules = create_rules(data)
recommendation = arl_recommender(rules, 22492, 1)
