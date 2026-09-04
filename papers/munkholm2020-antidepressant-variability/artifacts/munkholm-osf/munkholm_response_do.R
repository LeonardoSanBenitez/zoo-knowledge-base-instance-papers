#
# response_do.R
#
#-----------------------------------------------------------------------
# create file stamp and load all variables and functions
#-----------------------------------------------------------------------
system("touch ../output/R/response_do.Rout")
source("response_load.R")

# NB: create a subfolder "figures" and a subfolder "data".


# formatting of plots
basesize = 25 
legendsize = 15 
pointsize = 4


# Outcome RCT (absolut endpoint values)
#-----------------------------------------------------------------------
a <- aes(x = y1, y = id, group = as.factor(tx1))

p.rct <- ggplot(dat, a) +
  geom_point(aes(shape = as.factor(tx1),
                 color = as.factor(tx1)),
             size = pointsize) +
  scale_color_manual(values = c("black", "black")) +
  scale_shape_manual(values = c(1, 15)) +
  theme_classic(base_size = basesize) + 
  theme(legend.position = "right",
        legend.title = element_blank(), 
        legend.text = element_text(size = legendsize)) +
  xlab("HAMD") +
  ylab("Patient")


# Fig. 1a (delta outcome RCT delta) 
#-----------------------------------------------------------------------
p1aa <- p.rct %+% 
  (dat %>% mutate(y1 = cs1)) +
  xlab(bquote(Delta ~ HAMD)) 

p1a <- p.rct %+% 
  (dat %>% mutate(y1 = cs1)) +
  xlab(bquote(Delta ~ HAMD)) +
  scale_y_continuous(breaks = seq(0,30,1),
                     labels = c(0, rep("", 9), 10, rep("", 9), 20, rep("", 9), 30))


# Fig. 1b (ranking (no cut-off))
#-----------------------------------------------------------------------
p2 <- p1aa %+% 
  (dat %>% filter(tx1 == "Treatment") %>%
     # get reverse ranking of cs1
     arrange(cs1) %>% 
     mutate(y1 = cs1, id = factor(id, levels = id))) +
  scale_shape_manual(values = 15) +
  theme(legend.position = "")
p1b <- p2


# Fig. 1c (ranking with cut-off)
#-----------------------------------------------------------------------
a$group <- aes(group = as.factor(resp1))

p1c <- ggplot(dat %>% filter(tx1 == "Treatment") %>%
                arrange(cs1) %>% 
                mutate(y1 = cs1, id = factor(id, levels = id)),
              aes(x = cs1, y = id, group = as.factor(resp1))) +
  theme_classic(base_size = basesize) +       
  theme(legend.position = "right",
        legend.title = element_text(size = legendsize), 
        legend.text = element_text(size = legendsize)) +   
  geom_point(size = pointsize, shape = 22, aes(fill = as.factor(resp1))) +
  scale_fill_manual(name = "Response", values = c("gray", "black"),
                    labels = c("No", "Yes")) +
  geom_vline(xintercept = -cutoff, lty = 2) +
  xlab(bquote(Delta ~ HAMD)) +
  ylab("Patient")

# fig 1a, b and c in one plot
p1 <- plot_grid(p1a, p1b, p1c, 
                ncol = 3, 
                labels = "auto",
                label_size = 30,
                align = "hav")

# save plot
ggsave(plot = p1, filename = here("figures", "ranking_observedOutcome_fig1.pdf"),
       height = 6.99, width = 15.8)


# Fig. 2 Between-subject variability
# ----------------------------------------------------------------------
# Show how arbitrary and misleading ranking can be.

# plot equal benefit crossover
p2e <- plot_crossover(dat %>% arrange(cs1) %>%
                        filter(tx1 == "Treatment") %>%
                        mutate(id = factor(id, levels = id))) + 
  theme_classic(base_size = basesize) +
  theme(legend.title = element_blank())

# plot rervese benefit crossover
#cs2r <- -sort(dat$cs1[dat$tx1=="Treatment"])
cs2r <- seq(0.5, 7.5, length.out = n/2) + #adding sequential outcome from control to treatment condition across patients
  sort(dat$cs1[dat$tx1 == "Treatment"])

p2r <- plot_crossover(dat %>% arrange(cs1) %>%
                        filter(tx1 == "Treatment") %>%
                        mutate(id = factor(id, levels = id),
                               cs2 = cs2r),
                      pointsize = pointsize) +
  theme_classic(base_size = basesize) +
  theme(legend.title = element_blank())


# plot equal benefit
p2eb <- plot_benefit(dat %>% arrange(cs1) %>%
                       filter(tx1 == "Treatment") %>%
                       mutate(d=as.factor(d),
                              id = factor(id, levels = id)), 
                       pointsize = pointsize-1) +
  theme_classic(base_size = basesize)


# plot reverse benefit
p2rb <- plot_benefit(dat %>% arrange(cs1) %>%
                       filter(tx1 == "Treatment") %>%
                       mutate(id = factor(id, levels = id),
                              cs2 = cs2r, d = cs1-cs2),
                     pointsize = pointsize-1) +
  theme_classic(base_size = basesize)


# plot 4 plots together
p2all <- plot_grid(p2e, p2eb, p2r, p2rb,
                   labels = "auto",
                   label_size = 30,
                   align = "hav")

# save plot
ggsave(plot = p2all, filename = here("figures", "variation_btwPatients_fig2.pdf"),
       height = 10.4, width = 15.8)



# Fig. 3 Within-subject variability
#-----------------------------------------------------------------------

# Simulate basic characteristics
f               <- seq(0, 10, .1)    # fluctuations
ID              <- seq(1, 4, 1)      # N = 4 patients
M_HAMD_outcome <- ceiling(mean(dat$y1[dat$tx1 == "Treatment"]))


# Time and within-subject variability (wsv)
## Define sine and cosine functions to simulate symptom fluctuations
## for slope add: sin(f) - .2*f + 80

sin.fun = function(sine, f = seq(0, 10, .1)) {
  sin(f) + M_HAMD_outcome
}

sin.fun.1 = function(sine, f = seq(0, 10, .1)) {
  2 * sin(f) + M_HAMD_outcome
}

sin.fun.2 = function(sine, f = seq(0, 10, .1)) {
  .5 * sin(f) + M_HAMD_outcome
}

cos.fun = function(cosin, f = seq(0, 10, .1)) {
  cos(f + pi/2) + M_HAMD_outcome
}


# Plot all waves
p3a <- 
  ggplot(data.frame(x = f), aes(x)) +
  stat_function(fun = sin.fun, aes(linetype = "Patient 1")) + 
  stat_function(fun = sin.fun.1, aes(linetype = "Patient 2")) +
  stat_function(fun = sin.fun.2, aes(linetype = "Patient 3")) +
  stat_function(fun = cos.fun, aes(linetype = "Patient 4")) +
  geom_hline(yintercept = M_HAMD_outcome) +
  xlim(0, 10) +
  theme(axis.text.x = element_blank(), 
        legend.title = element_blank(), 
        legend.text = element_text(size = legendsize)) +
  theme_classic(base_size = basesize) +
  scale_x_continuous(breaks = c(0, 2, 4, 6, 8, 10)) +
  ylab("HAMD") +
  xlab("Time")


# Calculate M and SD for the individual waves
sin.values  <- sin(f) + M_HAMD_outcome
M.s         <- floor(mean(sin.values))
SD.s        <- sd(sin.values)

sin1.values <- 2 * sin(f) + M_HAMD_outcome
M.s1        <- floor(mean(sin1.values))
SD.s1       <- sd(sin1.values)

sin2.values <- .5 * sin(f) + M_HAMD_outcome
M.s2        <- floor(mean(sin2.values))
SD.s2       <- sd(sin2.values)

cos.values  <- cos(f + pi/2) + M_HAMD_outcome
M.c         <- ceiling(mean(cos.values))
SD.c        <- sd(cos.values)

# Sum of all means
mean_wsv   <- mean(M.s, M.s1, M.s2, M.c)

# Put together Ms and SDs
M_all      <- round(rbind(M.s, M.s1, M.s2, M.c)) 
SD_all     <- rbind(SD.s, SD.s1, SD.s2, SD.c) 

# Build df
df_fluc    <- data.frame(ID, M_all, SD_all)


# Plot average improvement
p3b <- 
  df_fluc %>%
  ggplot(aes(ID, M_all, group = ID)) +
  geom_errorbar(aes(ymin = M_all - SD_all, ymax = M_all + SD_all),
                size = .6, width = 0) +
  geom_hline(yintercept = M_HAMD_outcome, linetype = 2, col = "gray42", 
             show.legend = TRUE) +
  theme_classic(base_size = basesize) +
  geom_point(size = pointsize) +
  scale_y_continuous(breaks = c(9:13)) +
  coord_flip(xlim = NULL, ylim = NULL, expand = TRUE) +
  ylab("HAMD") +
  xlab("Patient")



# Plot all in one
p3 <- plot_grid(p3a + theme(legend.title = element_blank()),
                p3b,
                label_size = 30,
                labels = c("a", "b"), 
                nrow = 1,
                rel_widths = c(0.6, 0.4))


# plot3
ggsave(plot = p3, filename = here("figures", "variation_withinPatients_fig3.pdf"),
       height = 6.99, width = 15.8)


# Fig. S1 Repeated cross-over trials
#---------------------------------------------------------------------- 
# names(dat)
dat2 <- simulate_rct(n, id, mu_x, sd_x, mu_y_tx, sd_y_tx, mu_y_ct, sd_y_ct, cutoff,
                     delta = round(rnorm(n, delta, 5)))
                     

# weakly correlated net benefit
set.seed(6)
dat2w <- simulate_rct(n, id, mu_x, sd_x, mu_y_tx, sd_y_tx, mu_y_ct, sd_y_ct, cutoff,
                      delta = round(rnorm(n, delta, 15)))

# strongly correlated net benefit
dat2s <- simulate_rct(n, id, mu_x, sd_x, mu_y_tx, sd_y_tx, mu_y_ct, sd_y_ct, cutoff,
                      delta = round(-dat2$d + rnorm(n, 0, 5)))


#cor.test(dat2$d, dat2w$d)

# plot crossovers
p4   <- plot_crossover(dat2, pointsize = pointsize-1)
p4w  <- plot_crossover(dat2w, pointsize = pointsize-1)
p4s  <- plot_crossover(dat2s, pointsize = pointsize-1)

# plot regressions
p4wr <- plot_regression(data.frame(d1 = dat2$d, d2 = dat2w$d))
p4sr <- plot_regression(data.frame(d1 = dat2$d, d2 = dat2s$d))



# plot all together
p4all <- plot_grid(p4, p4w, p4wr, p4, p4s, p4sr,
                   nrow = 2,
                   labels = "auto",
                   label_size = 30,
                   align = "hav")

# save plot
ggsave(plot = p4all, filename = here("figures", "repeated_crossover_figS1.pdf"),
       height = 10.4, width = 15.8)


########################################################################
# Empirical models part
########################################################################

# Meta-analyse data from RCTs that have investigated the effects of 
# antidepressants versus placebo. 

# Load data from RCTs
# Data from Cipriani et al., The Lancet 2019 (https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(17)32802-7/fulltext).
# Download from: https://data.mendeley.com/datasets/83rthbp8ys/2
infile <- read_excel(here("data", "Cipriani et al_GRISELDA_Lancet 2018_Open data.xlsx"), 
                     col_types = c("text", "text", "text", 
                                   "numeric", "numeric", "text", "numeric", 
                                   "text", "numeric", "text", "text", 
                                   "numeric", "numeric", "text", "numeric", 
                                   "numeric", "numeric", "numeric", 
                                   "numeric"), na = c("*", "NA"), skip = 2)

# Wrangling
drug <- infile %>%
  filter(!Drug %in% c("placebo", "Placebo")) %>%
  select("id" = StudyID, "tx" = Drug, "mu1tx" = Mean_endpoint, "sd1tx" = SD_endpoint, "ntx"  = N_comp_imputed_efficacy, "duration" = Weeks, Scale) %>%
  separate(tx, c("tx", "dose_1", "dose_2", "dose_3"), remove = TRUE) %>%
  select(-dose_1, -dose_2, -dose_3) # clean up drug name to ignore doses
placebo <- infile %>%
  filter(Drug %in% c("placebo", "Placebo")) %>%
  select("id" = StudyID,  "mu1ct" = Mean_endpoint, "sd1ct" = SD_endpoint, "nct"  = N_comp_imputed_efficacy)
placebo_studies <- placebo$id
response <- left_join(drug, placebo, by = "id") 
response <- response %>%
  mutate(placebo_study = if_else(id %in% placebo_studies, "yes", "no")) %>%
  filter(placebo_study == "yes") %>%
  filter(Scale %in% c("HAMD17", "HAMD21", "MADRS")) %>%
  mutate(change_endpoint = ifelse(mu1tx < 0 & mu1ct < 0, "change_score", "endpoint_score"))
response <- response %>%
  drop_na() %>%
  group_by(id) %>%
  mutate(tx_arms = max(row_number())) %>%
  ungroup
response <- response %>%
  mutate(nct_orig = nct,
         nct = nct_orig/tx_arms)  #divide placebo arm n by number of treatment arms in study
df <- response


# ----------------------------------------------------------------------
# Extract basics
df <- df %>%
  group_by(id) %>%
  mutate(n_study_tx = sum(ntx)) %>%
  mutate(N_study = sum(nct_orig)/tx_arms + n_study_tx) %>%
  ungroup() %>%
  mutate(n_comparison = ntx+nct) 
  
df_grouped <- df %>%
  group_by(id) %>%
  filter(row_number() ==1)

N_pairs       <- length(df$id)
Ntotal <- sum(df_grouped$N_study)
Ntotal_tx <- sum(df_grouped$n_study_tx)
Ntotal_ct <- sum(df_grouped$nct_orig)
n_studies <- length(unique(df$id))
n_antidepressants <- length(unique(df$tx))



# Descriptive tables
# ----------------------------------------------------------------------

# overall descriptives

#tab1 <- tableby(Scale   ~ mu1tx + mu1ct + sd1tx + sd1ct, data=df, test = FALSE, total = FALSE, control = tableby.control(numeric.stats = c("meansd")), digits = 1)
#mylabels <- list(mu1tx = "Tx change score", mu1ct = "Ct change score", sd1tx = "Tx change SD", sd1ct = "Ct change SD")
#tab1 <- kable(summary(tab1, labelTranslations = mylabels, text=TRUE))

df <- df %>%
  mutate("Outcome type" = recode(change_endpoint, change_score = "Change score", endpoint_score = "Endpoint score")) %>%
  mutate("Outcome treatment group" = mu1tx,
         "Outcome control group" = mu1ct, 
         "SD treatment group" = sd1tx,
         "SD control group" = sd1ct)
# tab1 <- table1(~ `Outcome treatment group` + `Outcome control group` + `SD treatment group` + `SD control group` | Scale*`Outcome type`, data=df, overall=F)
#tab1_1 <- tableby(interaction(Scale, `Outcome type`) ~ `Outcome treatment group` + `Outcome control group`+ `SD treatment group` + `SD control group`, 
#                     test = FALSE, total = FALSE, data = df, digits = 2)
#tab1 <- summary(tab1_1)
tab1_df <- df %>%
  select(7, 18:22)

tab1 <- tab1_df %>%
  gather(Variable, value, -Scale, -`Outcome type`) %>%
  group_by(Scale, `Outcome type`, Variable) %>%
  summarise(mean = round(mean(value), digits = 2), 
            sd = round(sd(value), digits = 2)) %>%
  unite("Mean (sd)", mean, sd, sep = " (") %>%
  mutate("Mean (sd)" = paste0(`Mean (sd)`, ")")) %>%
  spread(Scale, `Mean (sd)`)

# random effects meta-analyses by Scale
meta_dat <- escalc(measure = "MD", m1i = mu1tx, sd1i = sd1tx, n1i = ntx, m2i = mu1ct, sd2i = sd1ct, n2i = nct, data = df)

#HAMD17
meta_hamd17    <- rma(yi = yi, vi = vi, data = meta_dat, method = "REML",
                      slab = paste(df$id), weighted = TRUE, subset = (Scale == "HAMD17"))
hamd17_coef <- coef(summary(meta_hamd17)) # this is identical to the one below
metacont_hamd17 <- metacont(ntx, mu1tx, sd1tx, nct, mu1ct, sd1ct, data = df, sm = "MD", method.tau = "REML", subset = Scale == "HAMD17") # this is identical to the one above
#HAMD21
meta_hamd21    <- rma(yi = yi, vi = vi, data = meta_dat, method = "REML",
                      slab = paste(df$id), weighted = TRUE, subset = (Scale == "HAMD21"))
hamd21_coef <- coef(summary(meta_hamd21))
#MADRS
meta_madrs    <- rma(yi = yi, vi = vi, data = meta_dat, method = "REML",
                     slab = paste(df$id), weighted = TRUE,subset = (Scale == "MADRS"))
madrs_coef <- coef(summary(meta_madrs))


names(hamd21_coef) <- names(hamd17_coef)
names(madrs_coef) <- names(hamd17_coef)
tab2 <- rbind(hamd17_coef, hamd21_coef, madrs_coef) %>%
  dplyr::select("Mean difference" = "estimate", 5:6) %>%
  round(1) %>%
  unite("95% CI", ci.lb, ci.ub, sep = "; ")

tab2$Scale <- c("HAMD17", "HAMD21", "MADRS")
rownames(tab2) <- NULL
tab2 <- tab2 %>%
  dplyr::select(Scale, everything())





# Model 1:  Variability difference between antidepressants and placebo groups
# ----------------------------------------------------------------------
# using log coefficient of variation ratio (log CVR) as the effect size statistic as implemented in the metafor
# package (cf. Viechtbauer 2010; Cortes 2018)

# important: by default, metafor will conduct a weighted analysis (see:
# www.rdocumentation.org/packages/metafor/versions/1.9-9/topics/rma.uni)
# i.e., the parameter "weighted" is set to TRUE by default!

# calculate VR
rdat <- escalc(measure = "VR", 
               m1i = mu1tx, n1i = ntx, sd1i = sd1tx, 
               m2i = mu1ct, n2i = nct, sd2i = sd1ct, 
               data = df)


# fit random-effects models
m1    <- rma(yi = yi, vi = vi, data = rdat, method = "REML",
             slab = paste(df$id), weighted = TRUE)
summary(m1)
coef(summary(m1))
m1_back <- round(exp(coef(summary(m1))), digits = 2)

# equivealent RE model using the meta package
# both endpoint and change scores
m1_meta <- metagen(yi, sqrt(vi), data = rdat, tau.common = FALSE, method.tau = "REML", sm = "MD") #total yields identical estimates to m1 using rma
sum_m1_meta <- summary(m1_meta)
sum_m1_meta_back <- exp(c(sum_m1_meta$random$TE, sum_m1_meta$random$lower, sum_m1_meta$random$upper))

# endpoint scores only
m1_meta_endpoint <- metagen(yi, sqrt(vi), data = rdat, tau.common = FALSE, method.tau = "REML", sm = "MD", subset = change_endpoint == "endpoint_score") #total yields identical estimates to m1 using rma
sum_m1_meta_endpoint <- summary(m1_meta_endpoint)
sum_m1_meta_endpoint_back <- exp(c(sum_m1_meta_endpoint$random$TE, sum_m1_meta_endpoint$random$lower, sum_m1_meta_endpoint$random$upper))

# change scores only
m1_meta_change <- metagen(yi, sqrt(vi), data = rdat, tau.common = FALSE, method.tau = "REML", sm = "MD", subset = change_endpoint == "change_score") #total yields identical estimates to m1 using rma
sum_m1_meta_change <- summary(m1_meta_change)
sum_m1_meta_change_back <- exp(c(sum_m1_meta_change$random$TE, sum_m1_meta_change$random$lower, sum_m1_meta_change$random$upper))

# transform values from individual comparisons back to relative scale through exponentiation
srdat <- summary(rdat, trans = exp, digits = 2)


# calculate the number of studies that had VR < 1
N_VR_below1 <- srdat %>%
  group_by(id) %>%
  mutate(av_VR = mean(zi)) %>%
  mutate(below_over_1 = ifelse(av_VR < 1, "below", "equal to 1 or over")) %>%
  group_by(below_over_1) %>%
  count(n_distinct(id))


# Model 2: VR model by treatment (antidepressants) subgroup
# ----------------------------------------------------------------------
# Fit random-effects models using the meta package
#### Endpoint scores #####
# Calculate N for included studies in meta-analysis
df_grouped_endpoint <- df %>%
  filter(change_endpoint == "endpoint_score") %>%
  group_by(id) %>%
  filter(row_number() == 1)
Ntotal_endpoint <- sum(df_grouped_endpoint$N_study)
df_endpoint <- df %>%
  filter(change_endpoint == "endpoint_score")
N_pairs_endpoint       <- length(df_endpoint$id)


m2_endpoint <- metagen(yi, sqrt(vi), data = rdat, byvar = tx, subset = change_endpoint == "endpoint_score", tau.common = FALSE, method.tau = "REML") #here the results for the individual drugs are the same as the subset rma analyses - OK.
sum_m2_endpoint <- summary(m2_endpoint) #this model produces valid results
#create table with subgroup estimates
subgroup_estimates_m2_1_endpoint <- tibble(
  Drug = c(sum_m2_endpoint$bylevs, "Summary"), 
  Estimate = c(round(exp(sum_m2_endpoint$within.random$TE), digits = 2), round(exp(sum_m1_meta_endpoint$random$TE), digits = 2)), 
  ci_lower = c(round(exp(sum_m2_endpoint$within.random$lower), digits = 2), round(exp(sum_m1_meta_endpoint$random$lower), digits = 2)), 
  ci_upper = c(round(exp(sum_m2_endpoint$within.random$upper), digits = 2), round(exp(sum_m1_meta_endpoint$random$upper), digits = 2)),
  `I^2 (%)` = c(round(sum_m2_endpoint$I2.w$TE, digits = 4), sum_m1_meta_endpoint$I2$TE) * 100,
  Comparisons = c(sum_m2_endpoint$k.w, N_pairs_endpoint)) 
subgroup_estimates_m2_endpoint <- subgroup_estimates_m2_1_endpoint %>%
  unite("95% CI", ci_lower, ci_upper, sep = "; ")
N_by_tx_endpoint <- df %>%
  filter(change_endpoint == "endpoint_score") %>%
  group_by(tx) %>%
  summarise(N = round(sum(ntx+nct), digits = 0)) %>%
  rename("Drug" = tx)
 tab_by_tx_endpoint <- left_join(subgroup_estimates_m2_endpoint, N_by_tx_endpoint, by = "Drug")
 tab_by_tx_endpoint$Drug <- str_to_title(tab_by_tx_endpoint$Drug)
 tab_by_tx_endpoint$N[tab_by_tx_endpoint$Drug == "Summary"] <- Ntotal_endpoint
 tab_by_tx_endpoint$N <- round(tab_by_tx_endpoint$N, digits = 0)
 m2_bytx_tab_endpoint <- kable(tab_by_tx_endpoint)
 m2_subgroup_diff_pval_endpoint <- round(sum_m2_endpoint$pval.Q.b.random, digits = 2)


#RMA for sertraline only, as a moderate I^2 was observed
m2_2_endpoint <- metagen(yi, sqrt(vi), data = rdat, subset = tx == "sertraline" & change_endpoint == "endpoint_score",  tau.common = FALSE, method.tau = "REML", studlab = id) #here the results for the individual drugs are the same as the subset rma analyses - OK.
sum_m2_2_endpoint <- summary(m2_2_endpoint)
forest(m2_2_endpoint)  #the study Brunoni2012 has a very large effect of 0.42 (log scale)
pdf(here("figures", "forest_plot_sertraline_endpoint.pdf"), width = 11.5, height = 5.0) # save plot
forest(m2_2_endpoint)
dev.off()
ex_2 <- rdat %>%
  filter(change_endpoint == "endpoint_score") %>%
  filter(tx == "sertraline") %>%
  filter(!id == "Brunoni2012")
m2_2_1_endpoint <- metagen(yi, sqrt(vi), data = ex_2,  tau.common = FALSE, method.tau = "REML", studlab = id) #analysis without Brunoni et al. 2012
sum_m2_2_1_endpoint <- summary(m2_2_1_endpoint)
exp_sum_m2_2_1 <- round(exp(c(sum_m2_2_1_endpoint$random$TE, sum_m2_2_1_endpoint$random$lower, sum_m2_2_1_endpoint$random$upper)), digits = 2)
forest(metagen(yi, sqrt(vi), data = ex_2,  tau.common = FALSE, method.tau = "REML", studlab = id)) #without Brunoni2012 no heterogeneity and  larger (NS) ES

#organise data frame for forestplot by drug
forest_data_endpoint <- subgroup_estimates_m2_1_endpoint %>%
  left_join(N_by_tx_endpoint, by = "Drug") %>%
  mutate(Drug = str_to_title(Drug))
forest_data_endpoint$N[forest_data_endpoint$Drug == "Summary"] <- Ntotal_endpoint
forest_data_endpoint <- forest_data_endpoint %>%
  filter(!Drug == "Summary") %>%
  arrange(Estimate) %>%
  rbind(forest_data_endpoint[16,]) %>%
  arrange(-row_number()) %>%
  rename(study = Drug, es = Estimate, ci.lb = ci_lower, ci.ub = ci_upper, n = N) %>%
  mutate(ci.lb.c = ci.lb, ci.ub.c = ci.ub, study2 = factor(study), studywithref = study, nsize = n, ci.lb.a =  NA, ci.ub.a = NA) %>%
  mutate(rank = row_number()) %>%
  mutate(type = ifelse(study == "Summary", "Summary", "study"))
forest_data_endpoint$`I^2 (%)`[forest_data_endpoint$study == "Citalopram"] <- "NA"

# ------------------------------------- #

#### Change scores ####
# Calculate N for included studies  
df_grouped_change <- df %>%
  filter(change_endpoint == "change_score") %>%
  group_by(id) %>%
  filter(row_number() == 1)

Ntotal_change <- sum(df_grouped_change$N_study)  
df_change <- df %>%
  filter(change_endpoint == "change_score")
N_pairs_change <- length(df_change$id)
  
m2 <- metagen(yi, sqrt(vi), data = rdat, byvar = tx, subset = change_endpoint == "change_score", tau.common = FALSE, method.tau = "REML") #here the results for the individual drugs are the same as the subset rma analyses - OK.
sum_m2 <- summary(m2) #this model produces valid results
#create table with subgroup estimates
subgroup_estimates_m2_1 <- tibble(
  Drug = c(sum_m2$bylevs, "Summary"), 
  Estimate = c(round(exp(sum_m2$within.random$TE), digits = 2), round(exp(sum_m1_meta_change$random$TE), digits = 2)), 
  ci_lower = c(round(exp(sum_m2$within.random$lower), digits = 2), round(exp(sum_m1_meta_change$random$lower), digits = 2)), 
  ci_upper = c(round(exp(sum_m2$within.random$upper), digits = 2), round(exp(sum_m1_meta_change$random$upper), digits = 2)),
  `I^2 (%)` = c(round(sum_m2$I2.w$TE, digits = 4), sum_m1_meta_change$I2$TE) * 100,
  Comparisons = c(sum_m2$k.w, N_pairs_change)) 
subgroup_estimates_m2 <- subgroup_estimates_m2_1 %>%
  unite("95% CI", ci_lower, ci_upper, sep = "; ")
N_by_tx_change <- df %>%
  filter(change_endpoint == "change_score") %>%
  group_by(tx) %>%
  summarise(N = round(sum(ntx+nct), digits = 0)) %>%
  rename("Drug" = tx)
tab_by_tx <- left_join(subgroup_estimates_m2, N_by_tx_change, by = "Drug")
tab_by_tx$Drug <- str_to_title(tab_by_tx$Drug)
tab_by_tx$N[tab_by_tx$Drug == "Summary"] <- Ntotal_change
tab_by_tx$N <- round(tab_by_tx$N, digits = 0)
m2_bytx_tab <- kable(tab_by_tx)
m2_subgroup_diff_pval <- round(sum_m2$pval.Q.b.random, digits = 2)

#RMA for escitalopram only, as a large I^2 was observed
m2_1 <- metagen(yi, sqrt(vi), data = rdat, subset = tx == "escitalopram" & change_endpoint == "change_score",  tau.common = FALSE, method.tau = "REML", studlab = id) #here the results for the individual drugs are the same as the subset rma analyses - OK.
sum_m2_1 <- summary(m2_1)
forest(m2_1)  #the study DUbe et al. 2010 has a very large effect of 0.98 (log scale)
pdf(here("figures", "forest_plot_escitalopram_change.pdf"), width = 11.5, height = 5.0) # save plot
forest(m2_1)
dev.off()
ex <- rdat %>%
  filter(change_endpoint == "change_score") %>%
  filter(tx == "escitalopram") %>%
  filter(!id == "Dube2010 (NCT00420004)")
m2_1_1 <- metagen(yi, sqrt(vi), data = ex,  tau.common = FALSE, method.tau = "REML", studlab = id) #analysis without Dube et al. 2010
sum_m2_1_1 <- summary(m2_1_1)
exp_sum_m2_1_1 <- round(exp(c(sum_m2_1_1$random$TE, sum_m2_1_1$random$lower, sum_m2_1_1$random$upper)), digits = 2)
forest(m2_1_1) # forest plot without Dube et al. 2010 no heterogeneity and  lower ES

#RMA for sertraline only, as a moderate I^2 was observed
m2_2 <- metagen(yi, sqrt(vi), data = rdat, subset = tx == "sertraline" & change_endpoint == "change_score",  tau.common = FALSE, method.tau = "REML", studlab = id) #here the results for the individual drugs are the same as the subset rma analyses - OK.
sum_m2_2 <- summary(m2_2)
forest(m2_2)  #the study SER315 (FDA) has a very small effect of 0.58 (log scale)
ex_2 <- rdat %>%
  filter(change_endpoint == "change_score") %>%
  filter(tx == "sertraline") %>%
  filter(!id == "SER 315 (FDA)")
forest(metagen(yi, sqrt(vi), data = ex_2,  tau.common = FALSE, method.tau = "REML", studlab = id)) #without SER 315 (FDA) no heterogeneity and  larger (NS) ES

#organise data frame for forestplot by drug
forest_data <- subgroup_estimates_m2_1 %>%
  left_join(N_by_tx_change, by = "Drug") %>%
  mutate(Drug = str_to_title(Drug))
forest_data$N[forest_data$Drug == "Summary"] <- Ntotal_change
forest_data <- forest_data %>%
  filter(!Drug == "Summary") %>%
  arrange(Estimate) %>%
  rbind(forest_data[20,]) %>%
  arrange(-row_number()) %>%
  rename(study = Drug, es = Estimate, ci.lb = ci_lower, ci.ub = ci_upper, n = N) %>%
  mutate(ci.lb.c = ci.lb, ci.ub.c = ci.ub, study2 = factor(study), studywithref = study, nsize = n, ci.lb.a =  NA, ci.ub.a = NA) %>%
  mutate(rank = row_number()) %>%
  mutate(type = ifelse(study == "Summary", "Summary", "study")) 
forest_data$`I^2 (%)`[forest_data$study == "Fluvoxamine"] <- "NA"



# Model 3: VR model by scale subgroup
# ----------------------------------------------------------------------
# Fit random-effects models using the meta package
m3_endpoint <- metagen(yi, sqrt(vi), data = rdat, subset = change_endpoint == "endpoint_score", byvar = Scale,  tau.common = FALSE, method.tau = "REML", sm = "MD") #here the results for the individual drugs are the same as the subset rma analyses - OK.
sum_m3_endpoint <- summary(m3_endpoint) #this model produces valid results
#create table with subgroup estimates
subgroup_estimates_m3_endpoint <- tibble(
  Scale = c(sum_m3_endpoint$bylevs, "Total"), 
  Estimate = c(round(exp(sum_m3_endpoint$within.random$TE), digits = 2), round(exp(sum_m3_endpoint$random$TE), digits = 2)), 
  ci_lower = c(round(exp(sum_m3_endpoint$within.random$lower), digits = 2), round(exp(sum_m3_endpoint$random$lower), digits = 2)),
  ci_upper = c(round(exp(sum_m3_endpoint$within.random$upper), digits = 2), round(exp(sum_m3_endpoint$random$upper), digits = 2)),
  "I^2" = c(round(sum_m3_endpoint$I2.w$TE, digits = 4), sum_m1_meta$I2$TE)*100,
  Comparisons = c(sum_m3_endpoint$k.w, N_pairs_endpoint)) %>%
  unite("95% CI", ci_lower, ci_upper, sep = "; ")
N_by_scale_endpoint <- df %>%
  filter(change_endpoint == "endpoint_score") %>%
  group_by(Scale) %>%
  summarise(N = sum(ntx+nct))
tab_by_scale_endpoint <- left_join(subgroup_estimates_m3_endpoint, N_by_scale_endpoint, by = "Scale")
tab_by_scale_endpoint$N[tab_by_scale_endpoint$Scale == "Total"] <- Ntotal_endpoint
tab3_endpoint <- tab_by_scale_endpoint
m3_endpoint_subgroup_diff_pval <- round(sum_m3_endpoint$pval.Q.b.random, digits = 2)

#### Change scores ####
m3_change <- metagen(yi, sqrt(vi), data = rdat, subset = change_endpoint == "change_score", byvar = Scale,  tau.common = FALSE, method.tau = "REML", sm = "MD") #here the results for the individual drugs are the same as the subset rma analyses - OK.
sum_m3_change <- summary(m3_change) #this model produces valid results
#create table with subgroup estimates
subgroup_estimates_m3_change <- tibble(
  Scale = c(sum_m3_change$bylevs, "Total"), 
  Estimate = c(round(exp(sum_m3_change$within.random$TE), digits = 2), round(exp(sum_m3_change$random$TE), digits = 2)), 
  ci_lower = c(round(exp(sum_m3_change$within.random$lower), digits = 2), round(exp(sum_m3_change$random$lower), digits = 2)),
  ci_upper = c(round(exp(sum_m3_change$within.random$upper), digits = 2), round(exp(sum_m3_change$random$upper), digits = 2)),
  "I^2" = c(round(sum_m3_change$I2.w$TE, digits = 4), sum_m1_meta$I2$TE)*100,
  Comparisons = c(sum_m3_change$k.w, N_pairs_change)) %>%
  unite("95% CI", ci_lower, ci_upper, sep = "; ")
N_by_scale_change <- df %>%
  filter(change_endpoint == "change_score") %>%
  group_by(Scale) %>%
  summarise(N = sum(ntx+nct))
tab_by_scale_change <- left_join(subgroup_estimates_m3_change, N_by_scale_change, by = "Scale")
tab_by_scale_change$N[tab_by_scale_change$Scale == "Total"] <- Ntotal_change
tab3_change <- tab_by_scale_change
m3_change_subgroup_diff_pval <- round(sum_m3_change$pval.Q.b.random, digits = 2)

# -----------------------------------------------------------------------
# Fig 6. forest plot VR by drug
# -----------------------------------------------------------------------
# Endpoint scores
#srdat$n     <- srdat$N_study
#srdat$study <- attr(m1$yi, "slab")

# get values from model
#fdd         <- df_from_rma(srdat, m1) 

# plot forest
#fpl_by_drug         <- gg_forest(forest_data, 
#                         ylab = "Drug",
#                         xlab = "Variability ratio (VR)",
#                         cilab = "VR [95% CI]", 
#                         i2lab = "I^2")

#p_forest <- plot(fpl_by_drug[[1]])
#p_forest

forest_data_drugs_endpoint <- forest_data_endpoint %>%
  filter(!study == "Summary") %>%
  arrange(desc(rank))
summary_forest_endpoint <- forest_data_endpoint %>%
  filter(study == "Summary")

pdf(here("figures", "forest_plot_endpoint_scores.pdf"), width = 15.8, height = 8) # save figure

metafor::forest.default(x = forest_data_drugs_endpoint$es, ci.lb = forest_data_drugs_endpoint$ci.lb, 
                        ci.ub = forest_data_drugs_endpoint$ci.ub, slab = forest_data_drugs_endpoint$study2, 
                        ilab = cbind(forest_data_drugs_endpoint$n, forest_data_drugs_endpoint$`I^2 (%)`), ilab.xpos = c(0.60, 1.45), 
                        annotate = TRUE, ylim=c(-0.8, 20), top = 5, refline = 1, xlab = "VR (95% CI)")
addpoly.default(summary_forest_endpoint$es, ci.lb = summary_forest_endpoint$ci.lb, ci.ub = summary_forest_endpoint$ci.ub, 
                mlab = "Summary", rows = -0.5, cex = 1)

#add annotations
text(1.45, 16.5, as.expression(bquote(I^2)))
text(1.80, 16.5, "VR [95% CI]")
text(0.20, 16.5, "Drug")
text(0.88, 16.5, "Greater in placebo")
text(1.14, 16.5, "Greater in antidepressant")
text(0.60, 16.5, "N")
text(0.60, -0.5, summary_forest_endpoint$n)
text(1.45, -0.5, summary_forest_endpoint$`I^2 (%)`)

dev.off()


# save plot
#ggsave(plot = p_forest, filename = here("figures", "forest_plot_fig6.pdf"),
#       width = 6.99, height = 15.80)
# -------------------- #
  
# Change scores
forest_data_drugs <- forest_data %>%
  filter(!study == "Summary") %>%
  arrange(desc(rank))
summary_forest <- forest_data %>%
  filter(study == "Summary")

pdf(here("figures", "forest_plot_change_scores.pdf"), width = 15.8, height = 8) # save figure

metafor::forest.default(x = forest_data_drugs$es, ci.lb = forest_data_drugs$ci.lb, 
                        ci.ub = forest_data_drugs$ci.ub, slab = forest_data_drugs$study2, 
                        ilab = cbind(forest_data_drugs$n, forest_data_drugs$`I^2 (%)`), ilab.xpos = c(0.60, 1.45), 
                        annotate = TRUE, ylim=c(-0.8, 20), top = 1, refline = 1, xlab = "VR (95% CI)")
addpoly.default(summary_forest$es, ci.lb = summary_forest$ci.lb, ci.ub = summary_forest$ci.ub, 
                mlab = "Summary", rows = -0.5, cex = 1)

#add annotations
text(1.45, 20.5, as.expression(bquote(I^2)))
text(2.10, 20.5, "VR [95% CI]")
text(-0.1, 20.5, "Drug")
text(0.83, 20.5, "Greater in placebo")
text(1.22, 20.5, "Greater in antidepressant")
text(0.60, 20.5, "N")
text(0.60, -0.5, summary_forest$n)
text(1.45, -0.5, summary_forest$`I^2 (%)`)

dev.off()


# save plot
#ggsave(plot = p_forest, filename = here("figures", "forest_plot_fig6.pdf"),
#       width = 6.99, height = 15.80)

# ----------------------------------------------------------- #
### Assessment of normality of data ###
# ----------------------------------------------------------- #
  
# Wrangling
df_new <- infile %>%
  mutate(Group = ifelse(Drug %in% c("placebo", "Placebo"), "Placebo", "Antidepressant")) %>%
  mutate(change_endpoint = ifelse(Mean_endpoint < 0, "change_score", "endpoint_score")) 
placebo_studies <- df_new %>%
  filter(Group == "Placebo")
placebo_ids <- placebo_studies$StudyID
df_skew_data <- df_new %>%
  filter(StudyID %in% df$id) %>%
  select(StudyID, Group, Drug, N_comp_imputed_efficacy, Scale, change_endpoint, Mean_endpoint, SD_endpoint) %>%
  drop_na()

skew_table <- df_skew_data %>%
  filter(change_endpoint == "endpoint_score") %>%
  mutate(Mean_endpoint = abs(Mean_endpoint)) %>%
  mutate(skewvalue = Mean_endpoint/SD_endpoint) %>%
  mutate(Skewness = ifelse(skewvalue < 1, "Skew", ifelse(skewvalue >= 1 & skewvalue < 2, "Suggestive skew", "No skew"))) %>%
  mutate(`Endpoint or change score` = recode(change_endpoint, change_score = "Change score", endpoint_score = "Endpoint score")) %>%
  group_by(Group, Skewness) %>%
  count("N" = n()) %>%
  select(-n)
kableExtra::kable(skew_table, caption = "Indication of skew by group.")

skew_bar_chart <- df_skew_data %>%
  filter(change_endpoint == "endpoint_score") %>%
  mutate(Mean_endpoint = abs(Mean_endpoint)) %>%
  mutate(skewvalue = Mean_endpoint/SD_endpoint) %>%
  mutate(Skewness = ifelse(skewvalue < 1, "Skew", ifelse(skewvalue >= 1 & skewvalue < 2, "Suggestive skew", "No skew"))) %>%
  mutate(change_endpoint = recode(change_endpoint, change_score = "Change score", endpoint_score = "Endpoint score")) %>%
  ggplot(mapping = aes(x = Group,
                       fill = Skewness)) +
  geom_bar(position = "Stack") +
  theme_minimal() +
  labs(x = "Treatment group",
       y = "N arms") +
  scale_fill_jama()

skew_dotplot <- df_skew_data %>%
  filter(change_endpoint == "endpoint_score") %>%
  mutate(Mean_endpoint = abs(Mean_endpoint)) %>%
  mutate(skewvalue = Mean_endpoint/SD_endpoint) %>%
  mutate(StudyID = as.factor(StudyID)) %>%
  mutate(change_endpoint = recode(change_endpoint, change_score = "Change score", endpoint_score = "Endpoint score")) %>%
  ggplot(mapping = aes(x = fct_reorder(StudyID, skewvalue),
                       y = skewvalue,
                       color = Group, 
                       size = N_comp_imputed_efficacy)) +
  geom_point(alpha = 0.8) +
  theme_minimal() +
  guides(size = FALSE) +
  theme(axis.text.x = element_blank(), axis.ticks.x = element_blank()) +
  labs(x = "Study", y = "Skew ratio (mean/sd)",
       color = "Treatment group",
       size = element_blank()) +
  scale_color_jama()

skew_plots <- plot_grid(skew_bar_chart, skew_dotplot, 
                        nrow = 1, labels = "auto") 

# plot combined
ggsave(plot = skew_plots, filename = here("figures", "skew_plots.pdf"),
       height = 6.99, width = 15.8)

# VR meta-analysis by Skewness subgroup
# Generate skew indication categories and values
df_skew_ma <- df %>%
  mutate(mu1tx = abs(mu1tx),
         mu1ct = abs(mu1ct)) %>%
  mutate(skewvalue_tx = mu1tx/sd1tx) %>%
  mutate(Skewness_tx = ifelse(skewvalue_tx < 1 , "Skew", ifelse(skewvalue_tx >= 1 & skewvalue_tx < 2, "Suggestive skew", "No skew"))) %>%
  mutate(skewvalue_ct = mu1ct/sd1ct) %>%
  mutate(Skewness_ct = ifelse(skewvalue_ct < 1 , "Skew", ifelse(skewvalue_ct >= 1 & skewvalue_ct < 2, "Suggestive skew", "No skew"))) %>%
  mutate(Skewness = ifelse(Skewness_tx == "Skew" | Skewness_ct == "Skew", "Skew", ifelse(Skewness_tx == "No skew" & Skewness_ct == "No skew", "No skew", "Suggestive skew"))) %>%
  select(skewvalue_tx, skewvalue_ct, Skewness_tx, Skewness_ct, Skewness)

df_skew <- cbind(df, df_skew_ma)

df_skew %>%
  group_by(Skewness) %>%
  count(n_distinct(id))

df_skew %>%
  group_by(change_endpoint, Scale) %>%
  count(n_distinct(id))

rdat_skew <- escalc(measure = "VR", 
                    m1i = mu1tx, n1i = ntx, sd1i = sd1tx, 
                    m2i = mu1ct, n2i = nct, sd2i = sd1ct, 
                    data = df_skew)

# Fit RE model using the meta package
m1_meta_skew <- metagen(yi, sqrt(vi), data = rdat_skew, tau.common = FALSE, method.tau = "REML", sm = "MD") #total yields identical estimates to m1 using rma
sum_m1_meta_skew <- summary(m1_meta_skew)
sum_m1_meta_back_skew <- exp(c(sum_m1_meta_skew$random$TE, sum_m1_meta_skew$random$lower, sum_m1_meta_skew$random$upper))

# subgroup analysis according to skew for endpoint scores
sum_skew_subgroup_endpoint <- summary(update.meta(m1_meta_skew, byvar = Skewness, subset = change_endpoint == "endpoint_score"))
skew_subgroup_endpoint_p_diff <- round(sum_skew_subgroup_endpoint$pval.Q.b.random, digits = 2)

# sensitivity analysis, removing the studies with strong evidence of skew
sum_skew_excluding_skew_studies <- summary(update.meta(m1_meta_skew, subset = Skewness %in% c("Suggestive skew", "No skew") & change_endpoint == "endpoint_score"))
exp_sum_skew_excluding_skew_studies <- round(exp(c(sum_skew_excluding_skew_studies$random$TE, sum_skew_excluding_skew_studies$random$lower, sum_skew_excluding_skew_studies$random$upper)), digits = 2)

# sensitivity analysis of only studies with no suggestion of skew
sum_skew_only_noskew_studies <- summary(update.meta(m1_meta_skew, subset = Skewness == "No skew"))
exp_sum_skew_only_noskew_studies <- round(exp(c(sum_skew_excluding_skew_studies$random$TE, sum_skew_excluding_skew_studies$random$lower, sum_skew_excluding_skew_studies$random$upper)), digits = 2)


# ---------------------------------------------------------------------- #
#generate marginal density plots with RCT simulations to illustrate
#variances in different scenarios
source("density_plots.R")
source("VR_simulations.R")

