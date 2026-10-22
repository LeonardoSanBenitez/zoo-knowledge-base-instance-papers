"""Read the authors' .rds (an R data.frame with some matrix-valued columns, e.g. from scale()) into a
pandas DataFrame without R. pyreadr cannot parse the file; the `rdata` package can, once the
data.frame constructor is told to flatten (n, 1) matrix columns. Factor columns arrive as pandas
Categoricals, labelled columns keep their values.
"""
import site, sys
sys.path.append(site.getusersitepackages())
import numpy as np
import pandas as pd
import rdata


SKIPPED = []


def _arr(v):
    if hasattr(v, 'value') and not isinstance(v, (np.ndarray, pd.Series, pd.Categorical)):
        v = v.value                      # raw R object (e.g. POSIXct without a constructor)
    if isinstance(v, (pd.Series, pd.Categorical)):
        return v
    a = np.asarray(v)
    # TRAP (found 2026-10-23): rdata returns R's NA_integer_ as the raw int32 bit pattern -2147483648
    # (INT_MIN), not as a missing value. Any comparison like `x <= 3` then counts every NA as a 1.
    if a.dtype.kind == 'i' and (a == np.iinfo(np.int32).min).any():
        a = a.astype(float)
        a[a == np.iinfo(np.int32).min] = np.nan
    return a


def _df(obj, attrs):
    items = obj.items() if isinstance(obj, dict) else zip(attrs['names'], obj)
    arrs = [(nm, _arr(v)) for nm, v in items]
    lens = [len(a) for _, a in arrs if getattr(a, 'ndim', 1) >= 1 and len(np.shape(a)) >= 1]
    n = max(lens) if lens else 0
    cols = {}
    for nm, a in arrs:
        if isinstance(a, np.ndarray) and a.ndim == 2 and a.shape[0] == n:
            if a.shape[1] == 1:
                cols[nm] = a[:, 0]
            else:
                for j in range(a.shape[1]):
                    cols[f'{nm}.{j + 1}'] = a[:, j]
            continue
        if len(np.shape(a)) >= 1 and len(a) == n:
            cols[nm] = a
        else:
            SKIPPED.append((nm, np.shape(a)))
    return pd.DataFrame(cols)


def load(path):
    parsed = rdata.parser.parse_file(path)
    ctors = dict(rdata.conversion.DEFAULT_CLASS_MAP)
    ctors['data.frame'] = _df
    ctors['tbl_df'] = _df
    conv = rdata.conversion.SimpleConverter(constructor_dict=ctors, default_encoding='utf8')
    return conv.convert(parsed)


if __name__ == '__main__':
    d = load(sys.argv[1])
    print(type(d), getattr(d, 'shape', None))
    if isinstance(d, pd.DataFrame):
        for c in d.columns:
            print(c, d[c].dtype, d[c].nunique(dropna=True), d[c].isna().sum())
