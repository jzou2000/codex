import re


def expand(s, d):
    p = r'\$\((.*?)\)'
    m = re.search(p, s, re.I)