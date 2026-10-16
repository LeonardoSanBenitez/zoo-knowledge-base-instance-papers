# Parfit 2a - UK sample
# Lucius Caviola

library(psych)
library(effsize)
library(dplyr)
library(yarrr)
library(tidyr)


# Load data

df <- read.csv("Parfit2a.csv", sep=';',
               header=TRUE, stringsAsFactors=FALSE)

df <- tbl_df(df)



# Exclude participants

n_raw = nrow(df)
df <- filter(df, Progress == 100 & att_check == 1 & OUS_10 == 2)
sprintf("Final N = %s (Excluded = %s); female = %s; M-age = %s (SD = %s)", 
        nrow(df), (n_raw - nrow(df)), nrow(filter(df, gender == 1)), round(mean(df$age), digits=2), round(sd(df$age), digits=2))


# Prepare scales

df <- mutate(df, OUS_IB = rowMeans(select(df, OUS_1, OUS_2, OUS_3, OUS_4, OUS_5), na.rm = TRUE))
df <- mutate(df, OUS_IH = rowMeans(select(df, OUS_6, OUS_7, OUS_8, OUS_9), na.rm = TRUE))

df$CRT = 0
df$CRT <- ifelse(df$CRT_1 == 2, df$CRT + 1, df$CRT)
df$CRT <- ifelse(df$CRT_2 == 8, df$CRT + 1, df$CRT)
df$CRT <- ifelse(tolower(df$CRT_3) == "emily", df$CRT + 1, df$CRT)


# Analysis

## Ranking question

df$Parfit_prel_1 <- coalesce(df$control_Parfit_prel_1, df$good_Parfit_prel_1, df$Zebra_Parfit_prel_1, df$salience_Parfit_prel_1, df$Steril_Parfit_prelim_1)
df$Parfit_prel_2 <- coalesce(df$control_Parfit_prel_2, df$good_Parfit_prel_2, df$Zebra_Parfit_prel_2, df$salience_Parfit_prel_2, df$Steril_Parfit_prelim_2)
df$Parfit_prel_4 <- coalesce(df$control_Parfit_prel_4, df$good_Parfit_prel_4, df$Zebra_Parfit_prel_4, df$salience_Parfit_prel_4, df$Steril_Parfit_prelim_4)
df$Parfit_main <- coalesce(df$control_Parfit_main, df$good_Parfit_main, df$Zebra_Parfit_main, df$salience_Parfit_main, df$Steril_Parfit_main)

df$p_ranking <- ifelse(df$Parfit_prel_1 == 1 & df$Parfit_prel_4 == 3, T, F)

tbl = table(df$p_ranking, df$condition)
tbl
chisq.test(tbl)

df_zebra <- filter(df, condition == "control" | condition == "zebras")
tbl = table(df_zebra$p_ranking, df_zebra$condition)
tbl
chisq.test(tbl)


## exclude those who didn't give Parfitian rankings
df <- filter(df, p_ranking == T)
nrow(df)


## main question

tbl = table(df$Parfit_main, df$condition)
tbl
chisq.test(tbl)


df_control <- filter(df, condition == "control")
df_good <- filter(df, condition == "control" | condition == "goodfuture")
df_zebra <- filter(df, condition == "control" | condition == "zebras")
df_salient <- filter(df, condition == "control" | condition == "salientfuture")
df_steril <- filter(df, condition == "control" | condition == "sterilization")

tbl = table(df_good$Parfit_main, df_good$condition)
tbl
chisq.test(tbl)

tbl = table(df_zebra$Parfit_main, df_zebra$condition)
tbl
chisq.test(tbl)

tbl = table(df_salient$Parfit_main, df_salient$condition)
tbl
chisq.test(tbl)

tbl = table(df_steril$Parfit_main, df_steril$condition)
tbl
chisq.test(tbl)

df_good_salient <- filter(df, condition == "salientfuture" | condition == "goodfuture")
tbl = table(df_good_salient$Parfit_main, df_good_salient$condition)
tbl
chisq.test(tbl)


tbl = table(df$Parfit_main, df$CRT)
tbl
chisq.test(tbl)


## logistic regression including OUS and CRT
model.glm <- glm(Parfit_main ~  CRT + OUS_IH + OUS_IB, 
                 data = filter(df, !is.na(Parfit_main)),
                 family = binomial) 
summary(model.glm)
exp(coef(model.glm))


# Plot

df_only_control <- filter(df, condition == "control")
df_only_good <- filter(df,  condition == "goodfuture")
df_only_zebra <- filter(df, condition == "zebras")
df_only_salient <- filter(df,  condition == "salientfuture")
df_only_steril <- filter(df,  condition == "sterilization")

perc_control <- sum(df_only_control$Parfit_main)/nrow(df_only_control)
perc_good <- sum(df_only_good$Parfit_main)/nrow(df_only_good)
perc_zebra <- sum(df_only_zebra$Parfit_main)/nrow(df_only_zebra)
perc_salient <- sum(df_only_salient$Parfit_main)/nrow(df_only_salient)
perc_steril <- sum(df_only_steril$Parfit_main)/nrow(df_only_steril)


barplot(height = c(perc_control*100, perc_steril*100, perc_zebra*100, perc_salient*100, perc_good*100 ), 
        names.arg = c("control", "steril", "zebra", "salient", "good"), 
        xlab = "conditions", 
        ylab = "percentage saying difference 2 greater than 1")



# Appendix

## logistic regression of finding extinction uniquely bad with demographics

model.glm <- glm(Parfit_main ~ gender + age + education + income, 
                 data = filter(df_good, !is.na(Parfit_main)),
                 family = binomial) 
summary(model.glm)
