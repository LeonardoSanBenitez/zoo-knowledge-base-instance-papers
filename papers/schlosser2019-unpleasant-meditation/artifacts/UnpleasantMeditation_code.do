*************************************************
*Analysis script for: Measuring unpleasant meditation-related experiences in regular meditators: prevalence, predictors, and conceptual considerations
*dofile: UnpleasantMeditation_code
*software: Stata/MP 13.0
*data and details available on the Open Science Framework: https://osf.io/gj7z2

destring (age - msens19), replace
drop if years<0.16
drop if negative==.

*** Prevalence of unpleasant meditation-related experiences ***

tab negative
tab negative , miss
ci negative

*** Descriptives ***

sum age
tab sex
tab sex , miss
tab edu 
tab edu , miss
tab rel 
tab rel , miss
tab resi 
tab resi , miss

sum ptq 
sum mindsens 
sum scs 

tabstat years, s(n, mean, sd , p25, p50, p75)
gen agestart = age - years
sum agestart
sum freq
sum dura
tab retreat
tab attentional
tab deconst
tab constr

gen medtype = cond(attentional==0 & constructive==0 & deconstructive==1, 1, cond(attentional==1 & constructive==1 & deconstructive==0, 0, cond(attentional==1 & constructive==0 & deconstructive==0, 0, cond(attentional==0 & constructive==1 & deconstructive==0, 0, .))))
tab medtype, miss

gen sumtype = attentional + constructive + deconstructive
tab sumtype

tab negative if sex== 0
tab negative if sex== 1

tab negative if edu== 0
tab negative if edu== 1

tab negative if rel== 0
tab negative if rel== 1

tab negative if medtype== 0
tab negative if medtype== 1

tab negative if retreat== 0
tab negative if retreat== 1

*** Logistic regression ***

logistic negative age 
logit negative c.age##c.age
logistic negative i.sex
logistic negative i.edu
logistic negative i.rel
logistic negative i.rel i.resi

logistic negative ptq
logit negative c.ptq##c.ptq
logistic negative mindsens
logit negative c.mindsens##c.mindsens
logistic negative scs
logit negative c.scs##c.scs

logistic negative years
logit negative years
logit negative c.years##c.years
logistic negative i.medtype
logistic negative frequency
logit negative c.freq##c.freq
gen dur10 = duration / 10
logistic negative dur10
logit negative c.dura##c.dura
logistic negative i.retreat

*******************************************************************


