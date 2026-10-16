"""Does the binary forced choice ('which difference is greater?') hide 'equal / cannot compare' answers?"""
import pandas as pd
for st in ['2a','2b']:
    d=pd.read_csv(f'work/s{st}.csv',low_memory=False); ok=d[d.rank_ok & d.main.notna()].copy(); ok['free']=ok.free.fillna('').astype(str)
    has=ok.free.str.len()>3
    pat=r"\b(equal|equally|same|both (are|equally)|no difference|can'?t (compare|choose|decide)|cannot (compare|choose|decide)|impossible to|neither|hard to (say|choose|decide))\b"
    eq=ok.free.str.contains(pat,case=False,regex=True)
    print(f'{st}: texts {has.sum()} of {len(ok)} ranked; "equal/cannot compare" signals {eq.sum()} ({eq.sum()/max(has.sum(),1):.1%}); by condition {ok[eq].groupby("condition").size().to_dict()}')
