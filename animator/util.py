import argparse

def zip_adj(lst, adj, nones, wrap=False):
    '''Iterates over lst in tuples where each tuple has `adj` consecutive elements of lst
    `nones` will pad the list on both sides with that many nones

        >>> lst = list(range(6))
        >>> list(zip_adj(lst, adj=3, nones=0))
        [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5)]
        >>> list(zip_adj(lst, adj=3, nones=1))
        [(None, 0, 1), (0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, None)]
'''
    lst = [None] * nones + lst + [None] * nones
    lists = [lst[i:] for i in range(adj)]
    return zip(*lists)

class DotDict(argparse.Namespace):
    '''Acts like javascript dict, accessed solely through dot notation.
    Call vars(dotdict_obj) -> python dict'''
    def as_dict(self):
        return vars(self)

def clamp(v, min_v, max_v):
    '''Returns the closest real number to v in [min_v, max_v]'''
    return max(min(v, max_v), min_v)

def project_dict(dct, keys):
    return {k: v for k, v in dct.items() if k in keys}
