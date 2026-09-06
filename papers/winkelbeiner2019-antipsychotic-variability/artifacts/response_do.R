#
# response_do.R
#
#-----------------------------------------------------------------------

# create file stamp and load all variables and functions
#-----------------------------------------------------------------------
system("touch ../output/R/response_do.Rout")
source("response_load.R")


# formatting of plots
basesize = 25 
legendsize = 15 
pointsize = 4


# Outcome RCT (absolut values)
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
        xlab("PANSS") +
        ylab("Patient")


# Fig. 1a (delta outcome RCT delta) 
#-----------------------------------------------------------------------
p1a <- p.rct %+% 
  (dat %>% mutate(y1 = cs1)) + 
  xlab(bquote(Delta ~ PANSS))

# save plot
ggsave(plot = p1a, filename = "../output/Figures/response_fig1a.pdf", 
       width = 6.99, height = 6.99)
ggsave(plot = p1a, filename = "../output/Figures/response_fig1a.png", 
       width = 3.99, height = 2.99)



# Ranking (no cut-off)
#-----------------------------------------------------------------------
p2 <- p1a %+% 
  (dat %>% filter(tx1 == "Treatment") %>%
  # get reverse ranking of cs1
  arrange(cs1) %>% 
  mutate(y1 = cs1, id = factor(id, levels = id))) +
  scale_shape_manual(values = 15) +
  theme(legend.position = "")



# Fig. 1b (ranking with cut-off)
#-----------------------------------------------------------------------
a$group <- aes(group = as.factor(resp1))

p1b <- ggplot(dat %>% filter(tx1 == "Treatment") %>%
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
  xlab(bquote(Delta ~ PANSS)) +
  ylab("Patient")

# save plot
ggsave(plot = p1b, filename = "../output/Figures/response_fig1b.pdf",
       width = 6.99, height = 6.99)
ggsave(plot = p1b, filename = "../output/Figures/response_fig1b.png", 
       width = 3.99, height = 2.99)


# fig 1a and b in one plot
p1 <- plot_grid(p1a, p1b, 
                 ncol = 2, 
                 labels = "auto",
                 label_size = 30,
                 align = "hav")

# save plot
ggsave(plot = p1, filename = "../output/Figures/response_fig1.png",
       height = 6.99, width = 15.8)
ggsave(plot = p1, filename = "../output/Figures/response_fig1.pdf",
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
cs2r <- rep(1:(n/2)) + 
  sort(dat$cs1[dat$tx1 == "Treatment"])

p2r <- plot_crossover(dat %>% arrange(cs1) %>%
                        filter(tx1 == "Treatment") %>%
                        mutate(id = factor(id, levels = id),
                               cs2 = cs2r),
                      pointsize = pointsize) +
  theme_classic(base_size = basesize) +
  theme(legend.title = element_blank())


# plot equal benefits
p2eb <- plot_benefit(dat %>% mutate(d=as.factor(d)),
                     pointsize = pointsize-1) +
  theme_classic(base_size = basesize)


p2rb <- plot_benefit(dat %>% arrange(cs1) %>%
                       filter(tx1 == "Treatment") %>%
                       mutate(id = factor(id, levels = id),
                              cs2 = cs2r, d = cs1-cs2),
                     pointsize = pointsize-1) +
  theme_classic(base_size = basesize)


# plot all 6 plots together
p2all <- plot_grid(p2, p2e, p2eb, p2, p2r, p2rb,
                   labels = "auto",
                   label_size = 30,
                   align = "hav"
                   )

# save plot
ggsave(plot = p2all, filename = "../output/Figures/response_fig2.pdf",
       height = 10.4, width = 15.8)
ggsave(plot = p2all, filename = "../output/Figures/response_fig2.png",
       height = 10.4, width = 15.8)



# Fig. 3 Within-subject variability
#-----------------------------------------------------------------------

# Simulate basic characteristics
f               <- seq(0, 10, .1)    # fluctuations
ID              <- seq(1, 4, 1)      # N = 4 patients
M_PANSS_outcome <- ceiling(mean(dat$y1[dat$tx1 == "Treatment"]))


# Time and within-subject variability (wsv)
## Define sine and cosine functions to simulate symptom fluctuations
## for slope add: sin(f) - .2*f + 80

sin.fun = function(sine, f = seq(0, 10, .1)) {
  sin(f) + M_PANSS_outcome
}

sin.fun.1 = function(sine, f = seq(0, 10, .1)) {
  2 * sin(f) + M_PANSS_outcome
}

sin.fun.2 = function(sine, f = seq(0, 10, .1)) {
  .5 * sin(f) + M_PANSS_outcome
}

cos.fun = function(cosin, f = seq(0, 10, .1)) {
 cos(f + pi/2) + M_PANSS_outcome
}


# Plot all waves
p3a <- 
  ggplot(data.frame(x = f), aes(x)) +
    stat_function(fun = sin.fun, aes(linetype = "Patient 1")) + 
    stat_function(fun = sin.fun.1, aes(linetype = "Patient 2")) +
    stat_function(fun = sin.fun.2, aes(linetype = "Patient 3")) +
    stat_function(fun = cos.fun, aes(linetype = "Patient 4")) +
    geom_hline(yintercept = M_PANSS_outcome) +
    xlim(0, 10) +
    theme(axis.text.x = element_blank(), 
          legend.title = element_blank(), 
          legend.text = element_text(size = legendsize)) +
    theme_classic(base_size = basesize) +
    scale_x_continuous(breaks = c(0, 2, 4, 6, 8, 10)) +
    ylab("PANSS") +
    xlab("Time")


# Calculate M and SD for the individual waves
sin.values  <- sin(f) + M_PANSS_outcome
M.s         <- floor(mean(sin.values))
SD.s        <- sd(sin.values)

sin1.values <- 2 * sin(f) + M_PANSS_outcome
M.s1        <- floor(mean(sin1.values))
SD.s1       <- sd(sin1.values)

sin2.values <- .5 * sin(f) + M_PANSS_outcome
M.s2        <- floor(mean(sin2.values))
SD.s2       <- sd(sin2.values)

cos.values  <- cos(f + pi/2) + M_PANSS_outcome
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
  geom_hline(yintercept = M_PANSS_outcome, linetype = 2, col = "gray42", 
             show.legend = TRUE) +
  theme_classic(base_size = basesize) +
  geom_point(size = pointsize) +
  scale_y_continuous(breaks = c(84, 85, 86)) +
  coord_flip(xlim = NULL, ylim = NULL, expand = TRUE) +
  ylab("PANSS") +
  xlab("Patient")



# Plot all in one
p3 <- plot_grid(p3a + theme(legend.title = element_blank()),
                p3b,
                label_size = 30,
                labels = c("a", "b"), 
                nrow = 1,
                rel_widths = c(0.6, 0.4))


# plot3
ggsave(plot = p3, filename = "../output/Figures/response_fig3.pdf",
       height = 6.99, width = 15.8)
ggsave(plot = p3, filename = "../output/Figures/response_fig3.png",
       height = 6.99, width = 15.8)




# Fig. 4 Repeated cross-over trials
#---------------------------------------------------------------------- 
# names(dat)
dat2 <- simulate_rct(n, id, mu_x, sd_x,
                     delta = round(rnorm(n, delta, 5)),
                     cutoff)

# strongly correlated net benefit
dat2s <- simulate_rct(n, id, mu_x, sd_x,
                       delta = round(-dat2$d + rnorm(n, 0, 5)),
                       cutoff)
                                                      
# weakly correlated net benefit
set.seed(8)
dat2w <- simulate_rct(n, id, mu_x, sd_x,
                       delta = round(rnorm(n, delta, 15)),
                       cutoff)

#cor.test(dat2$d, dat2w$d)

# plot crossovers
p4   <- plot_crossover(dat2, pointsize = pointsize-1)
p4s  <- plot_crossover(dat2s, pointsize = pointsize-1)
p4w  <- plot_crossover(dat2w, pointsize = pointsize-1)

# plot regressions
p4sr <- plot_regression(data.frame(d1 = dat2$d, d2 = dat2s$d))
p4wr <- plot_regression(data.frame(d1 = dat2$d, d2 = dat2w$d))


# plot all together
p4all <- plot_grid(p4, p4w, p4wr, p4, p4s, p4sr,
                   nrow = 2,
                   labels = "auto",
                   label_size = 30,
                   align = "hav")

# save plot
ggsave(plot = p4all, filename = "../output/Figures/response_fig4.pdf",
       height = 10.4, width = 15.8)
ggsave(plot = p4all, filename = "../output/Figures/response_fig4.png",
       height = 10.4, width = 15.8)





########################################################################
# Empirical models part
########################################################################

# Meta-analyse data from RCTs that have investigated the effects of 
# antipsychotics versus placebo. 

# Load data from RCTs
df            <- read_csv("../data/response.csv") 

# Extract basics
N_pairs       <- length(df$id)
df$N_study    <- (df$ntx + df$nct)
Ntotal        <- sum(df$N_study)



# Descriptives
# ----------------------------------------------------------------------

# Number of studies in which variance difference treatment>placebo
N_trpb      <- sum(df$diff.var > 0)
N_pbtr      <- N_pairs - N_trpb

# %
perc_trpb   <- (N_trpb / N_pairs) * 100
perc_pbtr   <- (N_pbtr / N_pairs) * 100


# Frequency & percentage
# Use table function for frequency
tab.tr      <- table(df[, c("tx")], useNA = "ifany")
tab.resp    <- table(df[, c("responder")], useNA = "ifany")
#tab.cov     <- table(df[, c("covariates")], useNA = "ifany")
tab.test    <- table(df[, c("statstest")], useNA = "ifany")
tab.eff     <- table(df[, c("d")], useNA = "ifany")

# Use table together with freqlist function for percentage
result.tr   <- freqlist(tab.tr, na.options = "include")
result.resp <- freqlist(tab.resp, na.options = "include")
#result.cov  <- freqlist(tab.cov, na.options = "include")
result.test <- freqlist(tab.test, na.options = "include")
result.eff  <- freqlist(tab.eff, na.options = "include")



# Model 1:  Variability ratio
# ----------------------------------------------------------------------
# using variance ratios as outcome as implemented in the metafor
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

# transform values back to relative scale through exponentiation
srdat <- summary(rdat, trans = exp, digits = 2)


# calculate the number (%) of studies that had VR < 1
vr_count <- sum(aggregate(srdat[ , "zi"], list(srdat$id), mean) < 1)



# Fig. 5 Forest plot VR
# ----------------------------------------------------------------------
srdat$n     <- srdat$N_study
srdat$study <- attr(m1$yi, "slab")

# get values from model
fdd         <- df_from_rma(srdat, m1) 

# plot forest
fpl         <- gg_forest(fdd = fdd, 
                         ylab = "Study",
                         xlab = "Variability ratio (VR)",
                         cilab = "VR [95% CI]")

plot(fpl[[1]])

# save plot
ggsave(plot = fpl[[1]], filename = "../output/Figures/response_fig5.pdf",
       width = 7.64, height = 10.2)
ggsave(plot = fpl[[1]], filename = "../output/Figures/response_fig5.png",
       width = 7.64, height = 10.2)



# Fig. 6 Forest plot VR, averaged across comparisons
# ----------------------------------------------------------------------

# aggregate data across comparisons
datm3 <- df %>%
  group_by(id) %>%
  dplyr::summarize(mu1txm = mean(mu1tx),
                   mu1ctm = mean(mu1ct),
                   ntxm = sum(ntx),
                   nctm = sum(nct),
                   sd1txm = sqrt(sum(sd1tx^2 * (ntx -1))/
                                 (ntxm-length(ntx))),
                   sd1ctm = sqrt(sum(sd1ct^2 * (nct -1))/
                                 (nctm-length(nct)))) 

# calculate VR
rdat3 <- escalc(measure = "VR", 
              m1i = mu1txm, n1i = ntxm, sd1i = sd1txm, 
              m2i = mu1ctm, n2i = nctm, sd2i = sd1ctm, 
              data = datm3) 

# fit random-effects models
m3    <- rma(yi = yi, vi = vi, data = rdat3, method = "REML",
             slab = paste(rdat3$id))
coef(summary(m3))


# for transformed overall effect size
tm3          <- predict(m3, trans = exp, digits = 2)

# transform values back to relative scale through exponentiation
srdat3       <- summary(rdat3, trans = exp, digits = 2)

# add necessary variables
srdat3$n     <- srdat3$ntxm + srdat3$nctm
srdat3$study <- attr(m3$yi, "slab")
srdat3       <- srdat3 %>%
                  left_join(unique(df %>%
                  dplyr::select(id, idnoyear, year)))
srdat3$study <- paste0(srdat3$idnoyear, " ", srdat3$year)

# extract values from model
fdd3         <- df_from_rma(dat = srdat3, rmamod = m3, addrefs = TRUE) 

## caluculate number (%) of studies with effect size < 1
srdat3_yi_01      <- sum(srdat3$yi < 1)
srdat3_yi_1       <- sum(srdat3$yi > 1)
srdat3_yi_01_perc <- srdat3_yi_01/52*100
srdat3_yi_1_perc  <- srdat3_yi_1/52*100


# plot forest
fpl     <- gg_forest(fdd = fdd3, 
                     ylab = "Study", 
                     ylim = c(0, 2.5),
                     xlab = "Variability ratio (VR)",
                     cilab = "VR [95% CI]")

plot(fpl[[1]])

# save plot
ggsave(plot = fpl[[1]],
       filename = "../output/Figures/response_fig6.pdf",
       width = 7.56, height = 7.38)
ggsave(plot = fpl[[1]],
       filename = "../output/Figures/response_fig6.png",
       width = 7.56, height = 7.38)



# Model 2: VR model over treatment (by antipsychotics)
# ----------------------------------------------------------------------
# aggregate data over antipsychotics
datm <- rdat %>%
  group_by(tx) %>%
  dplyr::summarize(mu1txm = mean(mu1tx),
                   mu1ctm = mean(mu1ct),
                   ntxm = sum(ntx),
                   nctm = sum(nct),
                   sd1txm = sqrt(sum(sd1tx^2 * (ntx -1))/(ntxm-length(ntx))),
                   sd1ctm = sqrt(sum(sd1ct^2 * (nct -1))/(nctm-length(nct))))

# calculate VR  
rdat2 <- escalc(measure = "VR", 
              m1i = mu1txm, n1i = ntxm, sd1i = sd1txm, 
              m2i = mu1ctm, n2i = nctm, sd2i = sd1ctm, 
              data = datm)

# Fit random-effects models
m2    <- rma(yi = yi, vi = vi, data = rdat2, method = "REML",
             slab = paste(rdat2$tx))

summary(m2)
coef(summary(m2)) 

# transform values back to relative scale through exponentiation
srdat2 <- summary(rdat2, trans = exp, digits = 2)



# Fig. 7 Forest plot VR by medication
# ----------------------------------------------------------------------
# overall n
srdat2$n     <- srdat2$ntxm + srdat2$nctm
srdat2$study <- attr(m2$yi, "slab")

# extract values from model
fdd2         <- df_from_rma(srdat2, m2)

# forest plot
fpl <- gg_forest(fdd = fdd2, 
                 ylab = "Drug",
                 xlab = "Variability ratio (VR)",
                 cilab = "VR [95% CI]",
                 ylim = c(0, 2.3))
fpl[[1]]

# save plots
ggsave(plot = fpl[[1]], filename = "../output/Figures/response_fig7.pdf",
       width = 6.99, height = 3.26)
ggsave(plot = fpl[[1]], filename = "../output/Figures/response_fig7.png",
       width = 6.99, height = 3.26)



# Mean-variance relationship
# ----------------------------------------------------------------------
# demonstrate that there is no positive association between sd(change) 
# and mean(change) for treatment and control

# aggrgate data for means
tmpdf1 <- df %>%
  dplyr::select(id, mu1ct, mu1tx,  year, N_study) %>%
  gather(key = mucttx, value = meanchange, mu1ct, mu1tx)

# aggregate data for sds
tmpdf2 <- df %>% 
  dplyr::select(id, sd1ct, sd1tx) %>%
  gather(key = sdcttx, value = sdchange, sd1ct, sd1tx)

# bind columns 
tmpdf <- cbind(tmpdf1, tmpdf2[, 3])

# Mean-variance relationship for control
lmfit11a1 <- lm(scale(sdchange) ~ scale(meanchange),
                weight = N_study, 
                data = tmpdf %>%
                  filter(mucttx == "mu1ct"))
summary(lmfit11a1)

# Mean-variance relationship for treatment
lmfit11a2 <- lm(scale(sdchange) ~ scale(meanchange),
                weight = N_study, 
                data = tmpdf %>%
                  filter(mucttx == "mu1tx"))
summary(lmfit11a2)



# Fig. 11 SD change - M change 
# ----------------------------------------------------------------------

p11a1 <- tmpdf %>%
  filter(mucttx == "mu1ct") %>%
  ggplot(aes(y = sdchange, x = meanchange)) +
  geom_point(aes(size = N_study), col = "darkblue", alpha = 0.3) +
  scale_size(range = c(3, 12)) +
  geom_smooth(method = "lm", col = "darkblue", fill = "darkblue") +
  theme_gray(base_size = 30) +
  theme(legend.position = "") +
  xlab("Mean") +
  ylab("SD") +
  ggtitle("Control")
 
p11a1 <- annotate_regression(lmfit11a1, p11a1)

p11a2 <- tmpdf %>%
  filter(mucttx == "mu1tx") %>%
  ggplot(aes(y = sdchange, x = meanchange)) +
  geom_point(aes(size = N_study), col = "darkblue", alpha = 0.3) +
  scale_size(range = c(3, 12)) +
  geom_smooth(method = "lm", col = "darkblue", fill = "darkblue") +
  theme_gray(base_size = 30) +
  theme(legend.position = "") +
  xlab("Mean") +
  ylab("SD") +
  ggtitle("Treatment")

p11a2 <- annotate_regression(lmfit11a2, p11a2)


# plot both in one plot
p11 <- plot_grid(p11a1, p11a2, 
                 labels = c("a", "b"),
                 label_size = 30, 
                 scale = 0.95)

# save plot
ggsave(filename = "../output/Figures/response_fig11.pdf",
       plot = p11, width = 14.1, height = 7.26)
ggsave(filename = "../output/Figures/response_fig11.png",
       plot = p11, width = 14.1, height = 7.26)




# Old diff var model, here as random intercept model
# ----------------------------------------------------------------------
# calculate difference of variances
df$diff.var <- df$sd1tx^2 - df$sd1ct^2
df$pooledsd <- sqrt(df$sd1tx^2 + df$sd1ct^2)

# old rme model
m10 <- lmer(diff.var ~ 1 + (1|id), data=df)
summary(m10)
