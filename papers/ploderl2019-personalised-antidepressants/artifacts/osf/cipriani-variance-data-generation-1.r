library(foreign)
library(effsize)
library(rms) 
library(metafor)



# Cipriani et al. (2018) data available here: 
# http://dx.doi.org/10.17632/83rthbp8ys.2#file-4d1c8675-f445-49be-8a0a-1b8d1fdd60c8

# Original file modified for use in this project: https://osf.io/98kex/files/
# The following changes included:
# # # Replaced missings ("*") with blank cells
# # # Some decimals had "." instead of "," and this was corrected
# # # For multiple dosages of medications, the data was aggregated, using mean values outcome (Mean, SD) and the sum of the sample sizes (see additional entries in red)
# # # for the calculations of CVR, it was necessary to use the absolute values of the pre-post differences
# # # The data file was translated to  CSV file using ";" as delimiters, and deleting the first two lines


setwd("/media/ploederl/ssdata/data/artikel/meine/cipriani-antidepressant-variance-analysis")

x <- read.csv("Cipriani et al_GRISELDA_Lancet 2018_Open data_averaged_doses.csv",header=T,sep=";",dec=",") 

attach(x)

n = length(StudyID)
ns = 522 # Number different trials


Study = rep("NA",ns) # Variable for Study ID


# drug.sd: standard deviation of outcome
# drug.m: mean value of outcome
# drug.n: sample size of drug-arm
# drug.do: drop-out rate
agomelatine.sd = rep(NA,ns); agomelatine.n = rep(NA,ns); agomelatine.m=rep(NA,ns); agomelatine.do=rep(NA,ns)
amitriptyline.sd = rep(NA,ns); amitriptyline.n = rep(NA,ns); amitriptyline.m = rep(NA,ns); amitriptyline.do = rep(NA,ns)
bupropion.sd = rep(NA,ns); bupropion.n = rep(NA,ns); bupropion.m = rep(NA,ns); bupropion.do = rep(NA,ns)
citalopram.sd = rep(NA,ns); citalopram.n = rep(NA,ns); citalopram.m = rep(NA,ns); citalopram.do = rep(NA,ns)
clomipramine.sd = rep(NA,ns); clomipramine.n = rep(NA,ns); clomipramine.m = rep(NA,ns); clomipramine.do= rep(NA,ns) 
desvenlafaxine.sd = rep(NA,ns); desvenlafaxine.n = rep(NA,ns); desvenlafaxine.m = rep(NA,ns); desvenlafaxine.do = rep(NA,ns)
duloxetine.sd = rep(NA,ns); duloxetine.n = rep(NA,ns); duloxetine.m = rep(NA,ns); duloxetine.do = rep(NA,ns)
escitalopram.sd = rep(NA,ns); escitalopram.n = rep(NA,ns); escitalopram.m = rep(NA,ns); escitalopram.do = rep(NA,ns)
fluoxetine.sd = rep(NA,ns); fluoxetine.n = rep(NA,ns); fluoxetine.m = rep(NA,ns); fluoxetine.do= rep(NA,ns)
fluvoxamine.sd = rep(NA,ns); fluvoxamine.n = rep(NA,ns); fluvoxamine.m= rep(NA,ns); fluvoxamine.do= rep(NA,ns)
levomilnacipran.sd = rep(NA,ns); levomilnacipran.n = rep(NA,ns); levomilnacipran.m = rep(NA,ns); levomilnacipran.do = rep(NA,ns)
milnacipran.sd = rep(NA,ns); milnacipran.n = rep(NA,ns); milnacipran.m = rep(NA,ns); milnacipran.do=rep(NA,ns)
mirtazapine.sd = rep(NA,ns); mirtazapine.n = rep(NA,ns); mirtazapine.m = rep(NA,ns); mirtazapine.do= rep(NA,ns)
nefazodone.sd = rep(NA,ns); nefazodone.n = rep(NA,ns);  nefazodone.m = rep(NA,ns); nefazodone.do = rep(NA,ns)
paroxetine.sd = rep(NA,ns); paroxetine.n = rep(NA,ns); paroxetine.m = rep(NA,ns); paroxetine.do = rep(NA,ns)
reboxetine.sd = rep(NA,ns); reboxetine.n = rep(NA,ns); reboxetine.m = rep(NA,ns); reboxetine.do = rep(NA,ns)
sertraline.sd = rep(NA,ns); sertraline.n = rep(NA,ns); sertraline.m = rep(NA,ns); sertraline.do = rep(NA,ns)
trazodone.sd = rep(NA,ns); trazodone.n = rep(NA,ns);  trazodone.m= rep(NA,ns);  trazodone.do= rep(NA,ns)
venlafaxine.sd = rep(NA,ns); venlafaxine.n = rep(NA,ns); venlafaxine.m = rep(NA,ns); venlafaxine.do = rep(NA,ns)
vilazodone.sd = rep(NA,ns); vilazodone.n = rep(NA,ns); vilazodone.m = rep(NA,ns); vilazodone.do= rep(NA,ns)
vortioxetine.sd = rep(NA,ns); vortioxetine.n = rep(NA,ns); vortioxetine.m = rep(NA,ns); vortioxetine.do = rep(NA,ns)
placebo.sd = rep(NA,ns); placebo.n = rep(NA,ns); placebo.m = rep(NA,ns); placebo.do=rep(NA,ns)
outcome=rep("NA",ns) # pre-post-difference (diff) or post-depression-values (post)
instrument=rep("NA",ns) # which assessment instrument
Year=rep(NA,ns) # year of publication
published = rep("NA",ns) # publication status (published vs. not published)
size=rep(NA,ns) # sample size


# Creating data matrix

s = 1 # counter for study
study=StudyID[1] # First Study
for (i in 1:n){
  if(StudyID[i]!=study) {s=s+1; study=StudyID[i]} # incrase counter in case of new study
    if(Drug[i]=="agomelatine"){agomelatine.sd[s]=SD[i];      agomelatine.n[s]=N.comp.imputed.1[i];       agomelatine.m[s]=abs(Mean.1[i]);    agomelatine.do[s]=Dropouts_total[i]/No_randomised[i];   Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="amitriptyline"){amitriptyline.sd[s]=SD[i];  amitriptyline.n[s]=N.comp.imputed.1[i];     amitriptyline.m[s]=abs(Mean.1[i]);  amitriptyline.do[s]=Dropouts_total[i]/No_randomised[i]; Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="bupropion"){bupropion.sd[s]=SD[i];          bupropion.n[s]=N.comp.imputed.1[i];         bupropion.m[s]=abs(Mean.1[i]);      bupropion.do[s]=Dropouts_total[i]/No_randomised[i];     Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="citalopram"){citalopram.sd[s]=SD[i];        citalopram.n[s]=N.comp.imputed.1[i];        citalopram.m[s]=abs(Mean.1[i]);     citalopram.do[s]=Dropouts_total[i]/No_randomised[i];    Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="clomipramine"){clomipramine.sd[s]=SD[i];    clomipramine.n[s]=N.comp.imputed.1[i];      clomipramine.m[s]=abs(Mean.1[i]);   clomipramine.do[s]=Dropouts_total[i]/No_randomised[i];  Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="desvenlafaxine"){desvenlafaxine.sd[s]=SD[i];desvenlafaxine.n[s]=N.comp.imputed.1[i];    desvenlafaxine.m[s]=abs(Mean.1[i]); desvenlafaxine.do[s]=Dropouts_total[i]/No_randomised[i];Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="duloxetine"){duloxetine.sd[s]=SD[i];        duloxetine.n[s]=N.comp.imputed.1[i];        duloxetine.m[s]=abs(Mean.1[i]);     duloxetine.do[s]=Dropouts_total[i]/No_randomised[i];    Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="escitalopram"){escitalopram.sd[s]=SD[i];    escitalopram.n[s]=N.comp.imputed.1[i];      escitalopram.m[s]=abs(Mean.1[i]);   escitalopram.do[s]=Dropouts_total[i]/No_randomised[i];  Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="fluoxetine"){fluoxetine.sd[s]=SD[i];        fluoxetine.n[s]=N.comp.imputed.1[i];        fluoxetine.m[s]=abs(Mean.1[i]);     fluoxetine.do[s]=Dropouts_total[i]/No_randomised[i];    Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="fluvoxamine"){fluvoxamine.sd[s]=SD[i];      fluvoxamine.n[s]=N.comp.imputed.1[i];       fluvoxamine.m[s]=abs(Mean.1[i]);    fluvoxamine.do[s]=Dropouts_total[i]/No_randomised[i];   Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="levomilnacipran"){levomilnacipran.sd[s]=SD[i];levomilnacipran.n[s]=N.comp.imputed.1[i]; levomilnacipran.m[s]=abs(Mean.1[i]);levomilnacipran.do[s]=Dropouts_total[i]/No_randomised[i];Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="milnacipran"){milnacipran.sd[s]=SD[i];      milnacipran.n[s]=N.comp.imputed.1[i];       milnacipran.m[s]=abs(Mean.1[i]);    milnacipran.do[s]=Dropouts_total[i]/No_randomised[i];   Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="mirtazapine"){mirtazapine.sd[s]=SD[i];      mirtazapine.n[s]=N.comp.imputed.1[i];       mirtazapine.m[s]=abs(Mean.1[i]);    mirtazapine.do[s]=Dropouts_total[i]/No_randomised[i];   Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="nefazodone"){nefazodone.sd[s]=SD[i];        nefazodone.n[s]=N.comp.imputed.1[i];        nefazodone.m[s]=abs(Mean.1[i]);     nefazodone.do[s]=Dropouts_total[i]/No_randomised[i];    Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="paroxetine"){paroxetine.sd[s]=SD[i];        paroxetine.n[s]=N.comp.imputed.1[i];        paroxetine.m[s]=abs(Mean.1[i]);     paroxetine.do[s]=Dropouts_total[i]/No_randomised[i];    Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="reboxetine"){reboxetine.sd[s]=SD[i];        reboxetine.n[s]=N.comp.imputed.1[i];        reboxetine.m[s]=abs(Mean.1[i]);     reboxetine.do[s]=Dropouts_total[i]/No_randomised[i];    Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="sertraline"){sertraline.sd[s]=SD[i];        sertraline.n[s]=N.comp.imputed.1[i];        sertraline.m[s]=abs(Mean.1[i]);     sertraline.do[s]=Dropouts_total[i]/No_randomised[i];    Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="trazodone"){trazodone.sd[s]=SD[i];          trazodone.n[s]=N.comp.imputed.1[i];         trazodone.m[s]=abs(Mean.1[i]);      trazodone.do[s]=Dropouts_total[i]/No_randomised[i];     Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="venlafaxine"){venlafaxine.sd[s]=SD[i];      venlafaxine.n[s]=N.comp.imputed.1[i];       venlafaxine.m[s]=abs(Mean.1[i]);    venlafaxine.do[s]=Dropouts_total[i]/No_randomised[i];   Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="vilazodone"){vilazodone.sd[s]=SD[i];        vilazodone.n[s]=N.comp.imputed.1[i];        vilazodone.m[s]=abs(Mean.1[i]);     vilazodone.do[s]=Dropouts_total[i]/No_randomised[i];    Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="vortioxetine"){vortioxetine.sd[s]=SD[i];    vortioxetine.n[s]=N.comp.imputed.1[i];      vortioxetine.m[s]=abs(Mean.1[i]);   vortioxetine.do[s]=Dropouts_total[i]/No_randomised[i];  Study[s]=as.character(StudyID[i]) }
    if(Drug[i]=="placebo") {placebo.sd[s]=SD[i]; placebo.n[s]=N.comp.imputed.1[i]; placebo.m[s]=abs(Mean.1[i]); placebo.do[s]=Dropouts_total[i]/No_randomised[i];  Study[s]=as.character(StudyID[i])}
    if(is.na(Mean.1[i])== F) {
          if(sign(Mean.1[i])== -1) {outcome[s]="diff"} # pre-post-differences assumed to be always negative
          if(sign(Mean.1[i])== 1) {outcome[s]="post"}  # post-values of depression scores are always positive
    }
    instrument[s]=as.character(Scale[i])
    if(Year_Published[i]=="unpublished") {published[s]="unpublished"; Year[s]="NA"} else {
                                       published[s]="published"; Year[s]=as.numeric(as.character(Year_Published[i]))}
}
  

data1=data.frame(Study, agomelatine.sd,agomelatine.n, agomelatine.m, agomelatine.do,
                 amitriptyline.sd, amitriptyline.n, amitriptyline.m, amitriptyline.do,
                 bupropion.sd, bupropion.n, bupropion.m, bupropion.do,
                 citalopram.sd,citalopram.n,citalopram.m, citalopram.do,
                 clomipramine.sd, clomipramine.n,clomipramine.m, clomipramine.do,
                 desvenlafaxine.sd,desvenlafaxine.n,desvenlafaxine.m, desvenlafaxine.do,
                 duloxetine.sd,duloxetine.n,duloxetine.m, duloxetine.do,
                 escitalopram.sd, escitalopram.n,escitalopram.m, escitalopram.do,
                 fluoxetine.sd, fluoxetine.n,fluoxetine.m, fluoxetine.do,
                 fluvoxamine.sd,fluvoxamine.n,fluvoxamine.m, fluvoxamine.do,
                 levomilnacipran.sd,levomilnacipran.n,levomilnacipran.m, levomilnacipran.do,
                 milnacipran.sd,milnacipran.n,milnacipran.m,milnacipran.do,
                 mirtazapine.sd,mirtazapine.n,mirtazapine.m,mirtazapine.do,
                 nefazodone.sd,nefazodone.n,nefazodone.m, nefazodone.do,
                 paroxetine.sd, paroxetine.n,paroxetine.m,paroxetine.do,
                 reboxetine.sd,reboxetine.n,reboxetine.m, reboxetine.do,
                 sertraline.sd,sertraline.n,sertraline.m, sertraline.do,
                 trazodone.sd,trazodone.n,trazodone.m,trazodone.do,
                 venlafaxine.sd,venlafaxine.n,venlafaxine.m, venlafaxine.do,
                 vilazodone.sd,vilazodone.n,vilazodone.m, vilazodone.do,
                 vortioxetine.sd,vortioxetine.n,vortioxetine.m,vortioxetine.do,
                 placebo.sd, placebo.n,placebo.m,outcome,instrument,Year,published,size,placebo.do)

ssri.n=rep(NA,ns);ssri.sd=rep(NA,ns);ssri.m=rep(NA,ns); ssri.do=rep(NA,ns)
snri.n=rep(NA,ns);snri.sd=rep(NA,ns);snri.m=rep(NA,ns); snri.do=rep(NA,ns)
atyp.n=rep(NA,ns);atyp.sd=rep(NA,ns);atyp.m=rep(NA,ns); atyp.do=rep(NA,ns)
tri.n=rep(NA,ns);tri.sd=rep(NA,ns);tri.m=rep(NA,ns); tri.do=rep(NA,ns)
all.n=rep(NA,ns);all.sd=rep(NA,ns);all.m=rep(NA,ns); all.do=rep(NA,ns) # all antidepressants


# reclassification and aggregation for classes of antidepressants (using means for M, SD and drop-out-rates, and sums for n)
# Cave: R produces zeros (but not NA's) for sums of vectors exclusively including NA's, therefore necessary to replace zeros with NA's
for(i in 1:ns){
   ssri.n[i] = sum(c(data1$citalopram.n[i], data1$escitalopram.n[i], data1$fluoxetine.n[i], data1$fluvoxamine.n[i], data1$paroxetine.n[i], data1$sertraline.n[i]) ,na.rm=T); if(ssri.n[i]==0){ssri.n[i]=NA} # the latter if-condition is necessary because R produces a zero when it should be NA!
   ssri.sd[i] = mean(c(data1$citalopram.sd[i], data1$escitalopram.sd[i], data1$fluoxetine.sd[i], data1$fluvoxamine.sd[i], data1$paroxetine.sd[i], data1$sertraline.sd[i]) ,na.rm=T)
   ssri.m[i] = mean(c(data1$citalopram.m[i], data1$escitalopram.m[i], data1$fluoxetine.m[i], data1$fluvoxamine.m[i], data1$paroxetine.m[i], data1$sertraline.m[i]) ,na.rm=T)
   ssri.do[i] = mean(c(data1$citalopram.do[i], data1$escitalopram.do[i], data1$fluoxetine.do[i], data1$fluvoxamine.do[i], data1$paroxetine.do[i], data1$sertraline.do[i]) ,na.rm=T)
   
   snri.n[i] = sum(c(data1$desvenlafaxine.n[i], data1$duloxetine.n[i], data1$levomilnacipran.n[i], data1$milnacipran.n[i], data1$reboxetine.n[i], data1$venlafaxine.n[i]) ,na.rm=T); if(snri.n[i]==0){snri.n[i]=NA}
   snri.sd[i] = mean(c(data1$desvenlafaxine.sd[i], data1$duloxetine.sd[i], data1$levomilnacipran.sd[i], data1$milnacipran.sd[i], data1$reboxetine.sd[i], data1$venlafaxine.sd[i]) ,na.rm=T)
   snri.m[i] = mean(c(data1$desvenlafaxine.m[i], data1$duloxetine.m[i], data1$levomilnacipran.m[i], data1$milnacipran.m[i], data1$reboxetine.m[i], data1$venlafaxine.m[i]),na.rm=T)
   snri.do[i] = mean(c(data1$desvenlafaxine.do[i], data1$duloxetine.do[i], data1$levomilnacipran.do[i], data1$milnacipran.do[i], data1$reboxetine.do[i], data1$venlafaxine.do[i]),na.rm=T)
   
   atyp.n[i] = sum(c(data1$agomelatine.n[i], data1$bupropion.n[i], data1$mirtazapine.n[i], data1$nefazodone.n[i], data1$trazodone.n[i], data1$vilazodone.n[i], data1$vortioxetine.n[i] ) ,na.rm=T); if(atyp.n[i]==0){atyp.n[i]=NA}
   atyp.sd[i] = mean(c(data1$agomelatine.sd[i], data1$bupropion.sd[i], data1$mirtazapine.sd[i], data1$nefazodone.sd[i], data1$trazodone.sd[i], data1$vilazodone.sd[i], data1$vortioxetine.sd[i]) ,na.rm=T)
   atyp.m[i] = mean(c(data1$agomelatine.m[i], data1$bupropion.m[i], data1$mirtazapine.m[i], data1$nefazodone.m[i], data1$trazodone.m[i], data1$vilazodone.m[i], data1$vortioxetine.m[i]) ,na.rm=T)
   atyp.do[i] = mean(c(data1$agomelatine.do[i], data1$bupropion.do[i], data1$mirtazapine.do[i], data1$nefazodone.do[i], data1$trazodone.do[i], data1$vilazodone.do[i], data1$vortioxetine.do[i]) ,na.rm=T)
   
   tri.n[i] = sum(c(data1$amitriptyline.n[i], data1$clomipramine.n[i] ) ,na.rm=T); if(tri.n[i]==0){tri.n[i]=NA}
   tri.sd[i] = mean(c(data1$amitriptyline.sd[i], data1$clomipramine.sd[i]) ,na.rm=T)
   tri.m[i] = mean(c(data1$amitriptyline.m[i], data1$clomipramine.m[i]) ,na.rm=T)
   tri.do[i] = mean(c(data1$amitriptyline.do[i], data1$clomipramine.do[i]) ,na.rm=T)
   
 
   all.n[i] = sum(c(data1$citalopram.n[i], data1$escitalopram.n[i], data1$fluoxetine.n[i], data1$fluvoxamine.n[i], data1$paroxetine.n[i], data1$sertraline.n[i],  data1$desvenlafaxine.n[i], data1$duloxetine.n[i], data1$levomilnacipran.n[i], data1$milnacipran.n[i],              data1$reboxetine.n[i], data1$venlafaxine.n[i],  data1$agomelatine.n[i], data1$bupropion.n[i], data1$mirtazapine.n[i], data1$nefazodone.n[i], data1$trazodone.n[i], data1$vilazodone.n[i], data1$vortioxetine.n[i],  data1$amitriptyline.n[i], data1$clomipramine.n[i] ) ,na.rm=T); if(all.n[i]==0){all.n[i]=NA}
   all.sd[i] = mean(c(data1$citalopram.sd[i], data1$escitalopram.sd[i], data1$fluoxetine.sd[i], data1$fluvoxamine.sd[i], data1$paroxetine.sd[i], data1$sertraline.sd[i],   data1$desvenlafaxine.sd[i], data1$duloxetine.sd[i], data1$levomilnacipran.sd[i], data1$milnacipran.sd[i], data1$reboxetine.sd[i], data1$venlafaxine.sd[i],  data1$agomelatine.sd[i], data1$bupropion.sd[i], data1$mirtazapine.sd[i], data1$nefazodone.sd[i], data1$trazodone.sd[i], data1$vilazodone.sd[i], data1$vortioxetine.sd[i],  data1$amitriptyline.sd[i], data1$clomipramine.sd[i]) ,na.rm=T)
   all.m[i] = mean(c(data1$citalopram.m[i], data1$escitalopram.m[i], data1$fluoxetine.m[i], data1$fluvoxamine.m[i], data1$paroxetine.m[i], data1$sertraline.m[i],  data1$desvenlafaxine.m[i], data1$duloxetine.m[i], data1$levomilnacipran.m[i], data1$milnacipran.m[i],             data1$reboxetine.m[i], data1$venlafaxine.m[i],  data1$agomelatine.m[i], data1$bupropion.m[i], data1$mirtazapine.m[i], data1$nefazodone.m[i], data1$trazodone.m[i], data1$vilazodone.m[i], data1$vortioxetine.m[i],  data1$amitriptyline.m[i], data1$clomipramine.m[i]) ,na.rm=T)
   all.do[i] = mean(c(data1$citalopram.do[i], data1$escitalopram.do[i], data1$fluoxetine.do[i], data1$fluvoxamine.do[i], data1$paroxetine.do[i], data1$sertraline.do[i],  data1$desvenlafaxine.do[i], data1$duloxetine.do[i], data1$levomilnacipran.do[i], data1$milnacipran.do[i],  data1$reboxetine.do[i], data1$venlafaxine.do[i],  data1$agomelatine.do[i], data1$bupropion.do[i], data1$mirtazapine.do[i], data1$nefazodone.do[i], data1$trazodone.do[i], data1$vilazodone.do[i], data1$vortioxetine.do[i],  data1$amitriptyline.do[i], data1$clomipramine.do[i]) ,na.rm=T)
   
   size[i]=sum(all.n[i],data1$placebo.n[i] ,na.rm=T); if(size[i]==0){size[i]=NA} # size of study (AD + placebo arms)
  
 }

data1$ssri.n=ssri.n; data1$ssri.sd=ssri.sd; data1$ssri.m=ssri.m; data1$ssri.do=ssri.do
data1$snri.n=snri.n; data1$snri.sd=snri.sd; data1$snri.m=snri.m; data1$snri.do=snri.do
data1$atyp.n=atyp.n; data1$atyp.sd=atyp.sd; data1$atyp.m=atyp.m; data1$atyp.do=atyp.do
data1$tri.n=tri.n;   data1$tri.sd=tri.sd;   data1$tri.m=tri.m;   data1$tri.do=tri.do
data1$all.n=all.n;   data1$all.sd=all.sd;   data1$all.m=all.m;   data1$all.do=all.do
data1$size=size
data1$placebo.do=placebo.do

# excluding head-to-head trials, i.e., only including placebo-controlled trials with sufficient information of the placebo-trials (n,M,SD)
data2 = subset(data1,is.na(data1$placebo.sd)==F & is.na(data1$placebo.m)==F & is.na(data1$placebo.n)==F) # only studies with placebo arm

write.csv2(data1,file="data1.csv",row.names = F)
write.csv2(data2,file="data2.csv",row.names = F)

