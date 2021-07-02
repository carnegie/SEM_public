# -*- coding: utf-8 -*-
"""

General utility functions for SEM

Created on Sat Jul 27 08:30:50 2019

@author: kcaldeira
"""

#%%  Convert dictionary of lists to list of dictionaries

def dict_of_lists_to_list_of_dicts(dict_of_lists):
    #Now case_dic is a dictionary of lists. We want to turn it into a list
    # of dictionaries.  The method for doing this is taken from:
    # https://stackoverflow.com/questions/5558418/list-of-dicts-to-from-dict-of-lists
    
    # case_dic_list = [dict(zip(case_list_dic,t)) for t in zip(*case_list_dic.values())]
    
    # The fancy thing didn't work for me so I will brute force it.
    #
    keywords = list(dict_of_lists)
    num_cases = len(dict_of_lists[keywords[0]])  # assume all the same length
    list_of_dicts = [ {} for  case in range(num_cases)]
    for i in range(num_cases):
        dic = {}
        for keyword in keywords:
            dic[keyword] = dict_of_lists[keyword][i]
        list_of_dicts[i] = dic
    return list_of_dicts

#%%  Convert list of dictionaries to dictionary of lists

def list_of_dicts_to_dict_of_lists(list_of_dicts):
  #
    keywords = list(list_of_dicts[0]) # assume same keys in all
    num_cases = len(list_of_dicts)  # assume all the same length
    dict_of_lists = {}
    for key in keywords:
        values = []
        for i in range(num_cases):
            values.append((list_of_dicts[i])[key])
        dict_of_lists[key] = values
    return dict_of_lists

#%%  Get unique elements from list of lists

def unique_list_of_lists(lol):
    return set(x for item in lol for x in item)