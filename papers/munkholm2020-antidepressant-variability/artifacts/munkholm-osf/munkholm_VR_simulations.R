#
# VR_simulations.R
#

##################################################################################################################
### Simulation of VR in scenario with a proportion of the patients having a large effect of the antidepressant ###
### ##############################################################################################################

#Data to inform simulation is based on RMA of data in empirical study
sim_data <- df %>% 
  filter(change_endpoint == "endpoint_score" & Scale == "HAMD17") %>%
  summarise(mean(mu1tx), mean(sd1tx), mean(sd1ct))

delta.hamd = abs(round(hamd17_coef$estimate)) #mean outcome difference on the HAMD-17 between AD and placebo
mean.ad = round(sim_data$`mean(mu1tx)`) #mean endpoint HAMD-17 score in AD group
mean.pl = mean.ad-delta.hamd # mean endpoint HAMD-17 score in placebo group
sd.ad = round(sim_data$`mean(sd1tx)`) # sd of HAMD-17 score in AD group
sd.pl = round(sim_data$`mean(sd1ct)`) # sd of HAMD-17 score in placebo group
n = 300   # sample size arms
sims = 1000 # number of experiments
Res = list() # saves VR output as sims*matrices
lnVR <- function(sdE, sdC, nE, nC){ #function to calculate log VR
  log(sdE/sdC) + 1/(2*(nE-1)) - 1/(2*(nC-1))
}

p.large_ES=c(0.01, seq(from=0.05,to=0.50,length.out=10)) # probability of large effect 
d.large_ES=seq(from=5,to=10,by = 1) # mean large effect (baseline to endpoint change HAMD score - difference from placebo)
vr=matrix(data=NA,length(p.large_ES),length(d.large_ES))

#run simulation
for (k in 1:sims){ 
  for (i in 1:length(p.large_ES)){            
  for(j in 1:length(d.large_ES)){           
    placebo = rnorm(n, mean=mean.pl, sd=sd.pl)  
    ad.large_ES = rnorm( (n*p.large_ES[i]), mean=mean.pl, sd=sd.ad) + d.large_ES[j] 
    ad.rest  = rnorm( (n*(1-p.large_ES[i])), mean=mean.pl, sd=sd.ad) + ((delta.hamd*n - n*p.large_ES[i]*d.large_ES[j]) / ((1-p.large_ES[i])*n)) 
    ad = c(ad.large_ES,ad.rest)
    vr[i,j] = exp(lnVR(sdE = sd(ad), sdC = sd(placebo), nE = n, nC = n))
    colnames(vr) = d.large_ES
    rownames(vr) = p.large_ES
    }
  }
  Res[[k]] = vr #output as list of matrices
  array <- array(unlist(Res), c(length(p.large_ES), length(d.large_ES), sims)) #make a 3d array from list of matrices
  array_means <- rowMeans(array, dims = 2) #get means (over two dimensions) for each cell
}

#create data frame with the data
df_array <- data.frame(array_means, row.names = factor(p.large_ES))
names(df_array) <- round(d.large_ES, digits = 1)
df_array <- rownames_to_column(df_array, "Probability")

#plot the VR data as a function of HAMD cutoff for exceptional responders and grouped by probablity
p17 <- as.data.frame(df_array) %>%
  group_by(Probability) %>%
  gather(HAMD, VR, 2:7) %>%
  ggplot() +
  aes(fct_inorder(factor(HAMD)), VR, group = Probability, linetype = Probability) +
  geom_point(size = 2, shape = 15) + 
  geom_line() + 
  labs(x = "Mean effect in patients in AD group with large effect size", y = "Variability ratio (VR)", linetype = "p") + 
  #geom_hline(yintercept = 1, color = "red") +
  theme_bw() +
  theme_classic(base_size = 25) +
  theme(legend.text = element_text(size=15))

ggsave(plot = p17, filename = here("figures", "vr_effectSize_fig5.pdf"),
       width = 15.8, height = 6.99)
