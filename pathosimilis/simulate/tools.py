import pandas as pd


def build_df(lst, what):
    if what == 'g':
        dct = {'code': [], 'type': [], 't-rate': [], 'size': []}

        for thing in lst:
            for tin in thing:
                dct['code'].append(tin.code)
                dct['type'].append(tin.type)
                dct['t-rate'].append(tin.transmission_rate)
                dct['size'].append(tin.size)

    else:
        dct = {'name': [], 'age': [], 'state': [], 'job': []}

        for thing in lst:
            for tin in thing:
                dct['name'].append(tin.name)
                dct['age'].append(tin.age)
                dct['state'].append(tin.state)
                dct['job'].append(tin.job)

    return pd.DataFrame(dct)
