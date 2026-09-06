library(foreign)
library(effsize)
library(rms) 
library(ggplot2)
library(metafor)

options(digits=2)
setwd("/media/ploederl/ssdata/data/artikel/meine/cipriani-antidepressant-variance-analysis")


# Load data to extract some parameters for simulation from this data-set

data2 <- read.csv2("data2.csv",header=T,sep=";") # only placebo-controlled trials (see data1.csv for all trials)
# All AD, but select trials without missing data for outcome variables in drug-arms and only those with HAMD17 and pre-post-differences
dat.all = subset(data2, is.na(all.sd)==F & is.na(all.m)==F & is.na(all.n)==F  & outcome=="diff" & instrument=="HAMD17") 
mean(dat.all$all.m); mean(dat.all$all.sd) # M, SD drugs (depression score at end of treatment)
mean(dat.all$all.m)- mean(dat.all$placebo.m) # Difference
mean(dat.all$placebo.m); mean(dat.all$placebo.sd) # SD placebo (depression score at end of treatment)

# Meta-Analysis
rdat <- escalc(measure = "SMD", 
               m1i = all.m, n1i = all.n, sd1i = all.sd, 
               m2i =  placebo.m, n2i = placebo.n, sd2i = placebo.sd, 
               data = dat.all)
m.all  <- rma(yi = yi, vi = vi, data = rdat, method = "REML", slab = dat.all$Study, weighted = TRUE)
summary(m.all); plot(m.all)

# d = 0.28 # result from meta-analysis above
# d.hamd = abs(d*SD) # backtranslation into HAMD point-differences

d.hamd = 2 # from Munkolm et al. 2019, Table 1 (acutally 1.97, but rounded to 2.00)
options(digits=4)


##################################################################################################################
### Scenario 1, assuming that AD-placebo difference is composed of super-responders and rest.
### For non-super-responders, the efficacy is reduced so that the overall efficacy in the AD arm is guaranteed
### Figure 1 in paper

# m.ad = mean(dat.all$all.m) # mean diff-value AD is 11.11 
m.ad = 11
m.pl = m.ad-d.hamd # mean diff-value placebo
SD = 8    # rounded, nearly identical for AD and placebo
n = 5000000   # sample size arms

p.super=seq(from=0.05,to=0.50,length.out=10) # probability super responders (counter i below)
d.super=seq(from=5,to=10,length.out = 10) # super responder definition - points HAMD  (counter j below)
vr=matrix(data=NA,length(p.super),length(d.super))


for (i in 1:length(p.super)){            # counter for probability super-responder (y-axis)
  for(j in 1:length(d.super)){           # counter for different values of point-differences (x-axis)
  placebo = rnorm(n, mean=m.pl, sd=SD) # draw values from placebo arm 
  ad.super = rnorm( (n*p.super[i]), mean=m.pl, sd=SD) + d.super[j] # draw values for super responders (add expected gain from variable d.super)
  ad.rest  = rnorm( (n*(1-p.super[i])), mean=m.pl, sd=SD) + ((d.hamd*n - n*p.super[i]*d.super[j]) / ((1-p.super[i])*n)) # add value so that overall diff (d.hamd) is guaranteed
  ad = c(ad.super,ad.rest)
  vr[i,j]=sd(ad)/sd(placebo)
  # print(mean(ad)-mean(placebo))
  }
}

plot(c(min(d.super-.5),max(d.super+.5)), c(0.9,max(vr)),type="n",
     xlab="AD-placebo point difference for benefiters",
     ylab="Variance Ratio")

lines(c(0,100),c(1.01,1.01),lwd=2)
lines(c(0,100),c(0.99,0.99),lwd=2,col="darkgray")
lines(c(0,100),c(1.02,1.02),lwd=2,col="darkgray")

for (i in 1:length(p.super)){
     lines(d.super,vr[i,])
     text(max(d.super+.5),max(vr[i,]),as.character(p.super[i]*100) )
}



######################################################################################
### Scenario 2, assuming that AD-placebo difference is ONLY caused by super-responders

m.ad = mean(dat.all$all.m) # mean diff-value AD
m.pl = m.ad-d.hamd # mean diff-value placebo
SD = 8    # rounded, nearly identical for AD and placebo
n = 1000000   # sample size arms

p.super=seq(from=0.05,to=0.50,length.out=10) # probability super responders - i
d.super=seq(from=3,to=10,length.out = 10) # super responder definition - points HAMD - j
vr=matrix(data=NA,length(p.super),length(d.super))


for (i in 1:length(p.super)){            # counter for probability super-responder (y-axis)
  for(j in 1:length(d.super)){           # counter for different values of point-differences (x-axis)
    placebo = rnorm(n, mean=m.pl, sd=SD) # draw values from placebo arm 
    ad.super = rnorm( (n*p.super[i]), mean=m.pl, sd=SD) + d.super[j] # draw values for super responders (add expected gain from variable d.super)
    ad.rest  = rnorm( (n*(1-p.super[i])), mean=m.pl, sd=SD) + ((0*n - n*p.super[i]*d.super[j]) / ((1-p.super[i])*n)) # add value so that overall diff (d.hamd) is guaranteed
    ad = c(ad.super,ad.rest)
    vr[i,j]=sd(ad)/sd(placebo)
    # print(mean(ad)-mean(placebo))
  }
}

plot(c(min(d.super-.5),max(d.super+.5)), c(0.9,max(vr)),type="n",
     xlab="AD-placebo point difference for super-responders",
     ylab="Variance Ratio")

lines(c(0,100),c(1.01,1.01),lwd=2)
lines(c(0,100),c(0.99,0.99),lwd=2,col="darkgray")
lines(c(0,100),c(1.02,1.02),lwd=2,col="darkgray")

for (i in 1:length(p.super)){
  lines(d.super,vr[i,])
  text(max(d.super+.5),max(vr[i,]),as.character(p.super[i]*100) )
}





#############################################
#### Check if calculation is correct 

m.ad = mean(dat.all$all.m) # mean diff-value AD
m.pl = m.ad-d.hamd # mean diff-value placebo
SD = 8    # rounded, nearly identical for AD and placebo
n = 1000000   # sample size arms

p.super=0.300
d.super=10
placebo = rnorm(n, mean=m.pl, sd=SD) # draw values from placebo arm 
ad.super = rnorm( (n*p.super), mean=m.pl, sd=SD) + d.super # draw values for super responders (add expected gain from variable d.super)
ad.rest  = rnorm( (n*(1-p.super)), mean=m.pl, sd=SD) + ((d.hamd*n - n*p.super*d.super) / ((1-p.super)*n)) # add value so that overall diff (d.hamd) is guaranteed
ad = c(ad.super,ad.rest)
vr=sd(ad)/sd(placebo)
print(mean(ad)-mean(placebo)-d.hamd) # must be zero
plot(density(ad))


