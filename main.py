import pandas as pd
import re
from collections import Counter


def get_result(q_only: object, data: object) -> object:
    q_only_issn = q_only.filter(["Full Journal Title", "ISSN", "Quartile"])
    q_only_issn.dropna(subset=["ISSN"], inplace=True)
    q_only_eissn = q_only.filter(["Full Journal Title", "E-ISSN", "Quartile"])
    q_only_eissn.dropna(subset=["E-ISSN"], inplace=True)

    q_data_wos_issn = pd.merge(left=q_only_issn, right=data, left_on="ISSN", right_on="ISSN")
    q_data_wos_eissn = pd.merge(left=q_only_eissn, right=data, left_on="E-ISSN", right_on="eISSN")
    q_only_result = pd.concat([q_data_wos_issn, q_data_wos_eissn])
    return q_only_result


def count_n(q: object) -> object:
    author_list = q["Addresses"].to_list()
    n_list = []
    for item in author_list:
        total = 0
        omstu_list = []
        all_list = []
        item_split = item.split("[")[1:]
        for elem in item_split:
            if elem.find("Omsk State Tech Univ") != -1:
                elem_split = elem.split("]")
                for i in elem_split[0].split(';'):
                    i = re.sub(r'[^A-Za-z]', '', i)
                    omstu_list.append(i)
                    all_list.append(i)
            else:
                elem_split = elem.split("]")
                for i in elem_split[0].split(';'):
                    i = re.sub(r'[^A-Za-z]', '', i)
                    all_list.append(i)
        all_dict = dict(Counter(all_list))
        n2 = len(all_dict.keys())
        for elem in omstu_list:
            total += 1 / all_dict[elem]
        n = total / n2
        n_list.append(n)
    q["N"] = n_list
    return q


def get_result_q_none(q1: object, q2: object, q3: object, q4: object, data: object) -> object:
    q_concat = pd.concat([q1, q2, q3, q4])
    result = pd.concat([data, q_concat])
    result.drop(["Full Journal Title", "Quartile", "E-ISSN"], axis=1, inplace=True)
    return result.drop_duplicates(keep=False)


def main():
    data_wos_df = pd.read_excel("data_WoS_2020.xls")
    journal_list = pd.read_excel("journal-list-jcr-2019_18122020.xlsx")

    journal_list_update = journal_list.filter(["Full Journal Title", "ISSN", "E-ISSN", "Quartile"])
    data_wos_update_df = data_wos_df.filter(["Article Title", "Addresses", "ISSN", "eISSN"])

    q1_only = journal_list_update[(journal_list_update["Quartile"] == "Q1")]
    q2_only = journal_list_update[(journal_list_update["Quartile"] == "Q2")]
    q3_only = journal_list_update[(journal_list_update["Quartile"] == "Q3")]
    q4_only = journal_list_update[(journal_list_update["Quartile"] == "Q4")]

    q1_only_result = get_result(q1_only, data_wos_update_df)
    q2_only_result = get_result(q2_only, data_wos_update_df)
    q3_only_result = get_result(q3_only, data_wos_update_df)
    q4_only_result = get_result(q4_only, data_wos_update_df)
    q_none = get_result_q_none(q1_only_result, q2_only_result, q3_only_result, q4_only_result, data_wos_update_df)

    q1_only_result = count_n(q1_only_result)
    q2_only_result = count_n(q2_only_result)
    q3_only_result = count_n(q3_only_result)
    q4_only_result = count_n(q4_only_result)
    q_none = count_n(q_none)

    q1_only_result.to_excel("w1.xlsx", index=False)
    q2_only_result.to_excel("w2.xlsx", index=False)
    q3_only_result.to_excel("w3.xlsx", index=False)
    q4_only_result.to_excel("w4.xlsx", index=False)
    q_none.to_excel("w_none.xlsx", index=False)
