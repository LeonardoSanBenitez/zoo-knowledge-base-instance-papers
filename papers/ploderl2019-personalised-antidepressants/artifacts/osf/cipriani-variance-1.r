library(foreign)
library(effsize)
library(rms) 
library(ggplot2,ggExtra)
library(metafor)

# See R-code of Winkelbeiner et al. (2019) for replication https://osf.io/k4zw3/
# Winkelbeiner paper https://jamanetwork.com/journals/jamapsychiatry/fullarticle/2735440


setwd("/media/ploederl/ssdata/data/artikel/meine/cipriani-antidepressant-variance-analysis")

data2 <- read.csv2("data2.csv",header=T,sep=";") # only placebo-controlled trials (see data1.csv for all trials)

# function for correlation coefficients in plots
r_value <- function(x,y){ m <- cor.test(x,y,method="pearson"); r = paste("r = ",round(as.numeric(m$estimate),digits=2),", p = ",round(m$p.value,digits=2),sep="")  }

# Specify outcome 
analysis.out="post" # only those studies reporting post-values of depression
analysis.out="diff" # only those studies reporting pre-post differences 

# Specify analysis
analysis = "CVR" # coefficient of variance - to be used in meta-analyses
analysis = "VR"  # variance ratio - to be used in meta-analyses


#######################
## Meta-Analysis
######################

# All AD
dat.all = subset(data2, is.na(all.sd)==F & is.na(all.m)==F & is.na(all.n)==F & outcome==analysis.out) # remove trials with missing data for outcome variables in drug-arms
sum(dat.all$all.n); sum(dat.all$placebo.n) # total sample sizes for drug- and placebo-arms
# calculate variables manually for double-checking and additional analysis
vardiff=dat.all$all.sd-dat.all$placebo.sd # to have an approxmiate impression of the differences (are results of meta-analysis comparable/plausible?)
vr=log(dat.all$all.sd/dat.all$placebo.sd) + 1/(2*(dat.all$all.n-1)) - 1/(2*(dat.all$placebo.n-1)) # Equation 9 in Nakagawa 2015
summary(exp(vr));hist(exp(vr))
cvr = log( (dat.all$all.sd/dat.all$all.m) / (dat.all$placebo.sd/dat.all$placebo.m)) + 1/(2*(dat.all$all.n-1)) - 1/(2*(dat.all$placebo.n-1))  # Equation 11 in Nakagawa 2015
summary(exp(cvr));hist(exp(cvr))
# if SD correlates with pre-post differences, than CVR is recommended instead of VR, see Nakagawa 2015
cor.test(dat.all$all.m,dat.all$all.sd,method="p") 
cor.test(dat.all$placebo.m,dat.all$placebo.sd,method="p")
# visualize correlations
ggplot(dat.all, aes(all.m,all.sd)) + geom_jitter(color="magenta",alpha=1/5,size=3) + geom_smooth(method = "loess",color="darkgray") + geom_smooth(alpha=1/5,color="gray",method='lm',se=FALSE) +
   labs(subtitle = r_value(dat.all$all.m,dat.all$all.sd))
ggplot(dat.all, aes(placebo.m,placebo.sd)) + geom_jitter(color="magenta",alpha=1/5,size=3) + geom_smooth(method = "loess",color="darkgray") + geom_smooth(alpha=1/5,color="gray",method='lm',se=FALSE)+
labs(subtitle = r_value(dat.all$placebo.m,dat.all$placebo.sd))
# create data for meta-analysis
rdat <- escalc(measure = analysis, 
               m1i = all.m, n1i = all.n, sd1i = all.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.all)
m.all  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE) # same parameters as in Winkelbauer et al. 2019
summary(m.all); plot(m.all)
exp(coef(summary(m.all)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.all, transf = exp, refline = 1, order = "obs", showweights = TRUE)




# SSRI
dat.ssri = subset(data2, is.na(ssri.sd)==F & is.na(ssri.m)==F & outcome==analysis.out & Study!="Dube2010 (NCT00420004)") # use this data to remove the Dube 2010 outlier
dat.ssri = subset(data2, is.na(ssri.sd)==F & is.na(ssri.m)==F & outcome==analysis.out )
cor.test(dat.ssri$ssri.m,dat.ssri$ssri.sd,method="p")
cor.test(dat.ssri$placebo.m,dat.ssri$placebo.sd,method="p")
sum(dat.ssri$ssri.n); sum(dat.ssri$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = ssri.m, n1i = ssri.n, sd1i = ssri.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.ssri)
m.ssri  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.ssri$Study, weighted = TRUE)
summary(m.ssri); plot(m.ssri)
coef(summary(m.ssri))
exp(coef(summary(m.ssri)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.ssri, transf = exp, refline = 1, order = "obs", showweights = TRUE)



# SNRI
dat.snri = subset(data2, is.na(snri.sd)==F & is.na(snri.m)==F & outcome==analysis.out)
cor.test(dat.snri$snri.m,dat.snri$snri.sd,method="p")
cor.test(dat.snri$placebo.m,dat.snri$placebo.sd,method="p")
sum(dat.snri$snri.n); sum(dat.snri$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = snri.m, n1i = snri.n, sd1i = snri.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.snri)
m.snri  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.snri$Study, weighted = TRUE)
summary(m.snri)
coef(summary(m.snri)) 
exp(coef(summary(m.snri)) )
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.snri, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Atypicals
dat.atyp = subset(data2, is.na(atyp.sd)==F & is.na(atyp.m)==F & outcome==analysis.out ) # no studies with diffs
cor.test(dat.atyp$atyp.m,dat.atyp$atyp.sd,method="p")
cor.test(dat.atyp$placebo.m,dat.atyp$placebo.sd,method="p")
sum(dat.atyp$atyp.n); sum(dat.atyp$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = atyp.m, n1i = atyp.n, sd1i = atyp.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.atyp)
m.atyp  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.atyp$Study, weighted = TRUE)
summary(m.atyp)
coef(summary(m.atyp))
exp(coef(summary(m.atyp)) )
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.atyp, transf = exp, refline = 1, order = "obs", showweights = TRUE)



# Tricyclics
dat.tri = subset(data2, is.na(tri.sd)==F & is.na(tri.m)==F & outcome==analysis.out )
cor.test(dat.tri$tri.m,dat.tri$tri.sd,method="p")
cor.test(dat.tri$placebo.m,dat.tri$placebo.sd,method="p")
sum(dat.tri$tri.n); sum(dat.tri$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = tri.m, n1i = tri.n, sd1i = tri.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.tri)
m.tri  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.tri$Study, weighted = TRUE)
summary(m.tri)
coef(summary(m.tri)) 
exp(coef(summary(m.tri)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.tri, transf = exp, refline = 1, order = "obs", showweights = TRUE)





### Individual AD

# Agomelatine
dat.agomelatine = subset(data2, is.na(agomelatine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )  # no data with diff
cor.test(dat.agomelatine$agomelatine.m,dat.agomelatine$agomelatine.sd,method="p")
cor.test(dat.agomelatine$placebo.m,dat.agomelatine$placebo.sd,method="p")
sum(dat.agomelatine$agomelatine.n); sum(dat.agomelatine$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = agomelatine.m, n1i = agomelatine.n, sd1i = agomelatine.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.agomelatine)
m.agomelatine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.agomelatine$Study, weighted = TRUE)
summary(m.agomelatine)
coef(summary(m.agomelatine)) 
exp(coef(summary(m.agomelatine)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.agomelatine, transf = exp, refline = 1, order = "obs", showweights = TRUE)




# Amitriptyline
dat.amitriptyline = subset(data2, is.na(amitriptyline.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )  
cor.test(dat.amitriptyline$amitriptyline.m,dat.amitriptyline$amitriptyline.sd,method="p")
cor.test(dat.amitriptyline$placebo.m,dat.amitriptyline$placebo.sd,method="p")
sum(dat.amitriptyline$amitriptyline.n); sum(dat.amitriptyline$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = amitriptyline.m, n1i = amitriptyline.n, sd1i = amitriptyline.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.amitriptyline)
m.amitriptyline  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.amitriptyline$Study, weighted = TRUE)
summary(m.amitriptyline)
coef(summary(m.amitriptyline)) 
exp(coef(summary(m.amitriptyline)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.amitriptyline, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Bupropion
dat.bupropion = subset(data2, is.na(bupropion.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )  
cor.test(dat.bupropion$bupropion.m,dat.bupropion$bupropion.sd,method="p")
cor.test(dat.bupropion$placebo.m,dat.bupropion$placebo.sd,method="p")
sum(dat.bupropion$bupropion.n); sum(dat.bupropion$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = bupropion.m, n1i = bupropion.n, sd1i = bupropion.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.bupropion)
m.bupropion  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.bupropion$Study, weighted = TRUE)
summary(m.bupropion)
coef(summary(m.bupropion)) 
exp(coef(summary(m.bupropion)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.bupropion, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Citalopram
dat.citalopram = subset(data2, is.na(citalopram.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.citalopram$citalopram.m,dat.citalopram$citalopram.sd,method="p")
cor.test(dat.citalopram$placebo.m,dat.citalopram$placebo.sd,method="p")
sum(dat.citalopram$citalopram.n); sum(dat.citalopram$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = citalopram.m, n1i = citalopram.n, sd1i = citalopram.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.citalopram)
m.citalopram  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.citalopram$Study, weighted = TRUE)
summary(m.citalopram)
coef(summary(m.citalopram)) 
exp(coef(summary(m.citalopram)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.citalopram, transf = exp, refline = 1, order = "obs", showweights = TRUE)



# Clomipramine - no trials available!
#dat.clomipramine = subset(data2, is.na(clomipramine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  ) #  No "diff" and no "post" data
#cor.test(dat.clomipramine$clomipramine.m,dat.clomipramine$clomipramine.sd,method="p")
#cor.test(dat.clomipramine$placebo.m,dat.clomipramine$placebo.sd,method="p")
#sum(dat.clomipramine$clomipramine.n); sum(dat.clomipramine$placebo.n)
#rdat <- escalc(measure = analysis, 
#               m1i = clomipramine.m, n1i = clomipramine.n, sd1i = clomipramine.sd, 
#               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
#               data = dat.clomipramine)
#m.clomipramine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.clomipramine$Study, weighted = TRUE)
#summary(m.clomipramine)
#coef(summary(m.clomipramine)) 
#exp(coef(summary(m.clomipramine)))
#srdat <- summary(rdat, trans = exp, digits = 2)
#forest(m.clomipramine, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Desvenlafaxine
dat.desvenlafaxine = subset(data2, is.na(desvenlafaxine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.desvenlafaxine$desvenlafaxine.m,dat.desvenlafaxine$desvenlafaxine.sd,method="p")
cor.test(dat.desvenlafaxine$placebo.m,dat.desvenlafaxine$placebo.sd,method="p")
sum(dat.desvenlafaxine$desvenlafaxine.n); sum(dat.desvenlafaxine$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = desvenlafaxine.m, n1i = desvenlafaxine.n, sd1i = desvenlafaxine.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.desvenlafaxine)
m.desvenlafaxine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.desvenlafaxine$Study, weighted = TRUE)
summary(m.desvenlafaxine)
coef(summary(m.desvenlafaxine)) 
exp(coef(summary(m.desvenlafaxine)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.desvenlafaxine, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Duloxetine
dat.duloxetine = subset(data2, is.na(duloxetine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.duloxetine$duloxetine.m,dat.duloxetine$duloxetine.sd,method="p")
cor.test(dat.duloxetine$placebo.m,dat.duloxetine$placebo.sd,method="p")
sum(dat.duloxetine$duloxetine.n); sum(dat.duloxetine$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = duloxetine.m, n1i = duloxetine.n, sd1i = duloxetine.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.duloxetine)
m.duloxetine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.duloxetine$Study, weighted = TRUE)
summary(m.duloxetine)
coef(summary(m.duloxetine)) 
exp(coef(summary(m.duloxetine)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.duloxetine, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Escitalopram
dat.escitalopram = subset(data2, is.na(escitalopram.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  & Study!="Dube2010 (NCT00420004)") # use this data to remove the Dube 2010 outlier
dat.escitalopram = subset(data2, is.na(escitalopram.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.escitalopram$escitalopram.m,dat.escitalopram$escitalopram.sd,method="p")
cor.test(dat.escitalopram$placebo.m,dat.escitalopram$placebo.sd,method="p")
sum(dat.escitalopram$escitalopram.n); sum(dat.escitalopram$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = escitalopram.m, n1i = escitalopram.n, sd1i = escitalopram.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.escitalopram)
m.escitalopram  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.escitalopram$Study, weighted = TRUE)
summary(m.escitalopram)
coef(summary(m.escitalopram)) 
exp(coef(summary(m.escitalopram)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.escitalopram, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Fluoxetine
dat.fluoxetine = subset(data2, is.na(fluoxetine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.fluoxetine$fluoxetine.m,dat.fluoxetine$fluoxetine.sd,method="p")
cor.test(dat.fluoxetine$placebo.m,dat.fluoxetine$placebo.sd,method="p")
sum(dat.fluoxetine$fluoxetine.n); sum(dat.fluoxetine$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = fluoxetine.m, n1i = fluoxetine.n, sd1i = fluoxetine.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.fluoxetine)
m.fluoxetine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.fluoxetine$Study, weighted = TRUE)
summary(m.fluoxetine)
coef(summary(m.fluoxetine)) 
exp(coef(summary(m.fluoxetine)) )
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.fluoxetine, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Fluvoxamine
dat.fluvoxamine = subset(data2, is.na(fluvoxamine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )  # no "diff" data
cor.test(dat.fluvoxamine$fluvoxamine.m,dat.fluvoxamine$fluvoxamine.sd,method="p")
cor.test(dat.fluvoxamine$placebo.m,dat.fluvoxamine$placebo.sd,method="p")
 sum(dat.fluvoxamine$fluvoxamine.n); sum(dat.fluvoxamine$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = fluvoxamine.m, n1i = fluvoxamine.n, sd1i = fluvoxamine.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.fluvoxamine)
m.fluvoxamine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.fluvoxamine$Study, weighted = TRUE)
summary(m.fluvoxamine)
coef(summary(m.fluvoxamine)) 
exp(coef(summary(m.fluvoxamine)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.fluvoxamine, transf = exp, refline = 1, order = "obs", showweights = TRUE)



# Levomilnacipran
dat.levomilnacipran = subset(data2, is.na(levomilnacipran.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.levomilnacipran$levomilnacipran.m,dat.levomilnacipran$levomilnacipran.sd,method="p")
cor.test(dat.levomilnacipran$placebo.m,dat.levomilnacipran$placebo.sd,method="p")
sum(dat.levomilnacipran$levomilnacipran.n); sum(dat.levomilnacipran$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = levomilnacipran.m, n1i = levomilnacipran.n, sd1i = levomilnacipran.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.levomilnacipran)
m.levomilnacipran  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.levomilnacipran$Study, weighted = TRUE)
summary(m.levomilnacipran)
coef(summary(m.levomilnacipran)) 
exp(coef(summary(m.levomilnacipran)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.levomilnacipran, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Milnacipran - no trials available!
#dat.milnacipran = subset(data2, is.na(milnacipran.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )  # no diff data
#cor.test(dat.milnacipran$milnacipran.m,dat.milnacipran$milnacipran.sd,method="p")
#cor.test(dat.milnacipran$placebo.m,dat.milnacipran$placebo.sd,method="p")
# sum(dat.milnacipran$milnacipran.n); sum(dat.milnacipran$placebo.n)
#rdat <- escalc(measure = analysis, 
#               m1i = milnacipran.m, n1i = milnacipran.n, sd1i = milnacipran.sd, 
#               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
#               data = dat.milnacipran)
#m.milnacipran  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.milnacipran$Study, weighted = TRUE)
#summary(m.milnacipran)
#coef(summary(m.milnacipran)) 
#exp(coef(summary(m.milnacipran)))
#srdat <- summary(rdat, trans = exp, digits = 2)
#forest(m.milnacipran, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Mirtazapine
dat.mirtazapine = subset(data2, is.na(mirtazapine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.mirtazapine$mirtazapine.m,dat.mirtazapine$mirtazapine.sd,method="p")
cor.test(dat.mirtazapine$placebo.m,dat.mirtazapine$placebo.sd,method="p")
sum(dat.mirtazapine$mirtazapine.n); sum(dat.mirtazapine$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = mirtazapine.m, n1i = mirtazapine.n, sd1i = mirtazapine.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.mirtazapine)
m.mirtazapine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.mirtazapine$Study, weighted = TRUE)
summary(m.mirtazapine)
coef(summary(m.mirtazapine)) 
exp(coef(summary(m.mirtazapine)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.mirtazapine, transf = exp, refline = 1, order = "obs", showweights = TRUE)



# Nefazodone
dat.nefazodone = subset(data2, is.na(nefazodone.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.nefazodone$nefazodone.m,dat.nefazodone$nefazodone.sd,method="p")
cor.test(dat.nefazodone$placebo.m,dat.nefazodone$placebo.sd,method="p")
sum(dat.nefazodone$nefazodone.n); sum(dat.nefazodone$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = nefazodone.m, n1i = nefazodone.n, sd1i = nefazodone.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.nefazodone)
m.nefazodone  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.nefazodone$Study, weighted = TRUE)
summary(m.nefazodone)
coef(summary(m.nefazodone)) 
exp(coef(summary(m.nefazodone)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.nefazodone, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Paroxetine
dat.paroxetine = subset(data2, is.na(paroxetine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  ) 
cor.test(dat.paroxetine$paroxetine.m,dat.paroxetine$paroxetine.sd,method="p")
cor.test(dat.paroxetine$placebo.m,dat.paroxetine$placebo.sd,method="p")
sum(dat.paroxetine$paroxetine.n); sum(dat.paroxetine$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = paroxetine.m, n1i = paroxetine.n, sd1i = paroxetine.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.paroxetine)
m.paroxetine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.paroxetine$Study, weighted = TRUE)
summary(m.paroxetine)
coef(summary(m.paroxetine)) 
exp(coef(summary(m.paroxetine)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.paroxetine, transf = exp, refline = 1, order = "obs", showweights = TRUE)



# Reboxetine
dat.reboxetine = subset(data2, is.na(reboxetine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.reboxetine$reboxetine.m,dat.reboxetine$reboxetine.sd,method="p")
cor.test(dat.reboxetine$placebo.m,dat.reboxetine$placebo.sd,method="p")
sum(dat.reboxetine$reboxetine.n); sum(dat.reboxetine$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = reboxetine.m, n1i = reboxetine.n, sd1i = reboxetine.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.reboxetine)
m.reboxetine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.reboxetine$Study, weighted = TRUE)
summary(m.reboxetine)
coef(summary(m.reboxetine)) 
exp(coef(summary(m.reboxetine)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.reboxetine, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Sertraline
dat.sertraline = subset(data2, is.na(sertraline.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.sertraline$sertraline.m,dat.sertraline$sertraline.sd,method="p")
cor.test(dat.sertraline$placebo.m,dat.sertraline$placebo.sd,method="p")
sum(dat.sertraline$sertraline.n); sum(dat.sertraline$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = sertraline.m, n1i = sertraline.n, sd1i = sertraline.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.sertraline)
m.sertraline  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.sertraline$Study, weighted = TRUE)
summary(m.sertraline)
coef(summary(m.sertraline)) 
exp(coef(summary(m.sertraline)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.sertraline, transf = exp, refline = 1, order = "obs", showweights = TRUE)



# Trazodone
dat.trazodone = subset(data2, is.na(trazodone.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  ) # no diff data
cor.test(dat.trazodone$trazodone.m,dat.trazodone$trazodone.sd,method="p")
cor.test(dat.trazodone$placebo.m,dat.trazodone$placebo.sd,method="p")
sum(dat.trazodone$trazodone.n); sum(dat.trazodone$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = trazodone.m, n1i = trazodone.n, sd1i = trazodone.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.trazodone)
m.trazodone  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.trazodone$Study, weighted = TRUE)
summary(m.trazodone)
coef(summary(m.trazodone)) 
exp(coef(summary(m.trazodone)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.trazodone, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Venlafaxine
dat.venlafaxine = subset(data2, is.na(venlafaxine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  ) 
cor.test(dat.venlafaxine$venlafaxine.m,dat.venlafaxine$venlafaxine.sd,method="p")
cor.test(dat.venlafaxine$placebo.m,dat.venlafaxine$placebo.sd,method="p")
sum(dat.venlafaxine$venlafaxine.n); sum(dat.venlafaxine$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = venlafaxine.m, n1i = venlafaxine.n, sd1i = venlafaxine.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.venlafaxine)
m.venlafaxine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.venlafaxine$Study, weighted = TRUE)
summary(m.venlafaxine)
coef(summary(m.venlafaxine)) 
exp(coef(summary(m.venlafaxine)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.venlafaxine, transf = exp, refline = 1, order = "obs", showweights = TRUE)


# Vilazodone
dat.vilazodone = subset(data2, is.na(vilazodone.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.vilazodone$vilazodone.m,dat.vilazodone$vilazodone.sd,method="p")
cor.test(dat.vilazodone$placebo.m,dat.vilazodone$placebo.sd,method="p")
sum(dat.vilazodone$vilazodone.n); sum(dat.vilazodone$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = vilazodone.m, n1i = vilazodone.n, sd1i = vilazodone.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.vilazodone)
m.vilazodone  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.vilazodone$Study, weighted = TRUE)
summary(m.vilazodone)
coef(summary(m.vilazodone)) 
exp(coef(summary(m.vilazodone)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.vilazodone, transf = exp, refline = 1, order = "obs", showweights = TRUE)



# Vortioxetine
dat.vortioxetine = subset(data2, is.na(vortioxetine.sd)==F & is.na(placebo.sd)==F & outcome==analysis.out  )
cor.test(dat.vortioxetine$vortioxetine.m,dat.vortioxetine$vortioxetine.sd,method="p")
cor.test(dat.vortioxetine$placebo.m,dat.vortioxetine$placebo.sd,method="p")
sum(dat.vortioxetine$vortioxetine.n); sum(dat.vortioxetine$placebo.n)
rdat <- escalc(measure = analysis, 
               m1i = vortioxetine.m, n1i = vortioxetine.n, sd1i = vortioxetine.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.vortioxetine)
m.vortioxetine  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.vortioxetine$Study, weighted = TRUE)
summary(m.vortioxetine)
coef(summary(m.vortioxetine)) 
exp(coef(summary(m.vortioxetine)))
srdat <- summary(rdat, trans = exp, digits = 2)
forest(m.vortioxetine, transf = exp, refline = 1, order = "obs", showweights = TRUE)









#########################
## Sensitivity Analysis
########################

# Specify outcome 
analysis.out="post"
analysis.out="diff"

# Specify analysis
analysis = "CVR"
analysis = "VR"


# All studies (both outcomes, i.e., pre-post differences and post-values, all in one)
dat.all = subset(data2, is.na(all.sd)==F & is.na(all.m)==F & is.na(all.n)==F)
rdat <- escalc(measure = analysis, 
               m1i = all.m, n1i = all.n, sd1i = all.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.all)
m  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods = ~outcome)
summary(m); plot(m)
exp(coef(summary(m)))


# Data for different sensitivity analysis below - but check which outcome variable you want
dat.all = subset(data2, is.na(all.sd)==F & is.na(all.m)==F & is.na(all.n)==F  & outcome==analysis.out )
rdat <- escalc(measure = analysis, 
               m1i = all.m, n1i = all.n, sd1i = all.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.all)


########################
### Sensitivity Analysis


# Assessment instrument
m  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods = ~instrument )
summary(m); plot(m)
exp(coef(summary(m)))


# Publication year
m  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods = ~Year )
summary(m); plot(m)
exp(coef(summary(m)))


# Type of publication (unpublished or published)
m  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods = ~published )
summary(m); plot(m)
exp(coef(summary(m)))


# Sample size
m  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods = ~size )
summary(m); plot(m)
exp(coef(summary(m)))


# Placebo drop-out rate makes a difference
m  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods = ~ placebo.do )
summary(m); plot(m)
exp(coef(summary(m)))

ggplot(dat.all, aes(placebo.do,placebo.sd)) + xlab("Drop-Out-Rate Placebo") + geom_jitter(color="magenta",alpha=1/5,size=3) + geom_smooth(method = "loess",color="darkgray") + geom_smooth(alpha=1/5,color="gray",method='lm',se=FALSE)+
  labs(subtitle = r_value(dat.all$placebo.do,dat.all$placebo.sd))


# Drug drop-out
m  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods = ~ all.do)
summary(m); plot(m)
exp(coef(summary(m)))

ggplot(dat.all, aes(all.do,all.sd)) + xlab("Drop-Out-Rate AD") + geom_jitter(color="magenta",alpha=1/5,size=3) + geom_smooth(method = "loess",color="darkgray") + geom_smooth(alpha=1/5,color="gray",method='lm',se=FALSE)+
  labs(subtitle = r_value(dat.all$all.do,dat.all$all.sd))


# Placebo-Drop-Out over the years - impressive!
ggplot(dat.all, aes(Year,all.do)) + ylab("Drop-Out-Rate AD") + geom_jitter(color="magenta",alpha=1/5,size=3) + geom_smooth(method = "loess",color="darkgray") + geom_smooth(alpha=1/5,color="gray",method='lm',se=FALSE) +
  labs(subtitle = r_value(dat.all$Year,dat.all$all.do))
ggplot(dat.all, aes(Year,placebo.do)) + ylab("Drop-Out-Rate Placebo") + geom_jitter(color="magenta",alpha=1/5,size=3) + geom_smooth(method = "loess",color="darkgray") + geom_smooth(alpha=1/5,color="gray",method='lm',se=FALSE)+
  labs(subtitle = r_value(dat.all$Year,dat.all$placebo.do))
ggplot(dat.all, aes(Year,all.do-placebo.do)) + ylab("Drop-Out-Rate-Difference Drug-Placebo") + geom_jitter(color="magenta",alpha=1/5,size=3) + geom_smooth(method = "loess",color="darkgray") + geom_smooth(alpha=1/5,color="gray",method='lm',se=FALSE)+
  labs(subtitle = r_value(dat.all$Year,(dat.all$all.do-dat.all$placebo.do)))






##########################
## Efficacy Meta-Analysis
## Just for fun
##########################

# Specify outcome 
analysis.out="post"
analysis.out="diff"

# Model for all ADs

dat.all = subset(data2, is.na(all.sd)==F & is.na(all.m)==F & is.na(all.n)==F & outcome==analysis.out)

rdat <- escalc(measure = "SMD", 
               m1i = all.m, n1i = all.n, sd1i = all.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.all)

# Meta-regressions, different moderator variables
m.all  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE)
m1.all  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods= ~Year+size)
m2.all  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods= ~placebo.do)
m3.all  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods= ~all.do)
m4.all  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE, mods= ~published)

summary(m.all); plot(m.all)
summary(m1.all); plot(m1.all)
summary(m2.all); plot(m2.all)
summary(m3.all); plot(m3.all)
summary(m4.all); plot(m4.all)

srdat <- summary(rdat,digits = 2)
forest(m.all, transf = exp, refline = 1, at = seq(0.5, 3, 0.5),
       order = "obs", # alim = c(0.5, 1.5), # xlim = c(-0.5,3), 
       ilab = m.all$ni.f, ilab.xpos = -10, width = 0.5, 
       showweights = TRUE)

# Visalizaation Meta-Regression 
ggplot(rdat, aes(Year,yi)) + geom_jitter(color="magenta",alpha=1/5,size=3) + ylab("SMD") + geom_smooth(method = "loess",color="darkgray") + geom_smooth(alpha=1/5,color="gray",method='lm',se=FALSE)+
  labs(subtitle = r_value(rdat$Year,rdat$yi))
ggplot(rdat, aes(placebo.do,yi)) + geom_jitter(color="magenta",alpha=1/5,size=3)  + ylab("SMD") + geom_smooth(method = "loess",color="darkgray") + geom_smooth(alpha=1/5,color="gray",method='lm',se=FALSE)+
  labs(subtitle = r_value(rdat$placebo.do,rdat$yi))
ggplot(rdat, aes(all.do,yi)) + geom_jitter(color="magenta",alpha=1/5,size=3) + ylab("SMD") + geom_smooth(method = "loess",color="darkgray") + geom_smooth(alpha=1/5,color="gray",method='lm',se=FALSE)+
  labs(subtitle = r_value(rdat$all.do,rdat$yi))
t.test(rdat$yi~rdat$published)


