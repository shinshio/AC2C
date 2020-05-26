# coding: utf-8
'''
Analyze scenario and, extract each items.
    items:cover, scenario, CAN, Relay information ...

TODO:
    No Item.

'''

# import from std
import sys
# import from pypi
import pandas as pd


def takeInCover(filename: str) -> list:
    """
    Take in cover information from scenario file

    Parameters
    ----------
        filename: str
            full path of scenario file
    Returns
    ----------
        lst_cover: list
            0: title, 1: author, 2:ECU type 3: ECU code,
            4: summary(1), 5: summary(2), 6: summary(3), 7: summary(4)
    """
    snHeader = 3
    snIndexCol = 0
    snSname = 'cover'
    df_cover = pd.read_excel(filename,header=snHeader,index_col=snIndexCol,sheet_name=snSname)
    lst_cover = sum(df_cover.fillna('').values.tolist(), [])
    return lst_cover


def takeInScenario(filename: str) -> list:
    """
    Take in scenario information from scenario file

    Parameters
    ----------
        filename: str
            full path of scenario file
    Returns
    ----------
        lst_scenario: list
            demension 1: scenarios
            demension 2:
                0: numbers, 1: scenario's items (orders and recipes) 2: judges
    """
    snHeader = 0
    snIndexCol = None
    snSname = 'scenario'
    df_scenario = pd.read_excel(filename,header=snHeader,index_col=snIndexCol,sheet_name=snSname)
    lst_scenario = df_scenario.fillna('').values.tolist()
    return lst_scenario


def takeInCanInfo(filename: str) -> list:
    """
    Take in CAN information from scenario file

    Parameters
    ----------
        filename: str
            full path of scenario file
    Returns
    ----------
        lst_can: list
            demension 1: keywords
                0: id for send, 1: id for response 2: message of dtc read
                3: message of dtc clear, 4: message of additional request
                5,6,7: reservation
            demension 2: value
                0: keywords, 1: value
    """
    snHeader = 0
    snIndexCol = None
    snSname = 'can'
    df_can = pd.read_excel(filename,header=snHeader,index_col=snIndexCol,sheet_name=snSname)
    lst_can = df_can.fillna('').values.tolist()
    return lst_can


def takeInRyDefInfo(filename: str) -> list:
    """
    Take in Relay default information from scenario file

    Parameters
    ----------
        filename: str
            full path of scenario file
    Returns
    ----------
        lst_can: list
            demension 1: number of relay
            demension 2: value
                0:number, 1: value (on, off, na)
    """
    snHeader = 0
    snIndexCol = None
    snSname = 'relay'
    df_ry = pd.read_excel(filename,header=snHeader,index_col=snIndexCol,sheet_name=snSname)
    lst_ry = df_ry.fillna('').values.tolist()
    return lst_ry


def sn2numZ3(scenario: list) -> str:
    """
    Convert scenario number to str (zero padding of 3)

    Parameters
    ----------
        scenario: list
            use only index 0
            0: number, 1: items (order and recipe), 2:judge
    Returns
    ----------
        str
            str of scenario number (zero padding of 3)
    """
    # return result
    return str(scenario[0]).zfill(3)


def sn2order(scenario: list) -> str:
    """
    Extract scenario item to order

    Parameters
    ----------
        scenario: list
            use only index 1
            0: number, 1: items (order and recipe), 2:judge
    Returns
    ----------
        str
            order of scenario
    """
    return str(scenario[1].split('<')[0])


def sn2recipe(scenario: list) -> list:
    """
    Extract scenario item to recipe

    Parameters
    ----------
        scenario: list
            use only index 1
            0: number, 1: items (order and recipe), 2:judge
    Returns
    ----------
        subOrder: list
            0: mainOrder, 1-end:subOrders
    """
    # slice main task
    allOrder = str(scenario[1].split('<')[1])
    mainOrder = allOrder.split('_')[0]
    subOrders = str(allOrder.split('_',1)[1]).replace('>','').split('_')
    subOrders.insert(0, mainOrder)
    # return result
    return subOrders


def sn2judge(scenario: list) -> str:
    """
    Extract scenario judge to recipe

    Parameters
    ----------
        scenario: list
            use only index 2
            0: number, 1: items (order and recipe), 2:judge
    Returns
    ----------
        str
            judge of scenario
    """
    # return result
    return str(scenario[2])


'''
----------
main
----------
'''
if __name__ == '__main__':
    pass
