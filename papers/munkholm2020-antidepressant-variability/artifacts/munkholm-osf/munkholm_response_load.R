#
# response_load.R
#
source("response_func.R")

# Defining reasonable HAMD17 values based on Cipriani et al. dataset
# Data from Cipriani et al., The Lancet 2019 (https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(17)32802-7/fulltext).
# Download from: https://data.mendeley.com/datasets/83rthbp8ys/2
# library(tidyverse)
# library(here)
# library(readxl)
# data_in <- read_excel(here("data", "Cipriani et al_GRISELDA_Lancet 2018_Open data.xlsx"), 
#                      col_types = c("text", "text", "text", 
#                                    "numeric", "numeric", "text", "numeric", 
#                                    "text", "numeric", "text", "text", 
#                                    "numeric", "numeric", "text", "numeric", 
#                                    "numeric", "numeric", "numeric", 
#                                    "numeric"), na = c("*", "NA"), skip = 2)
# 
# # Wrangling
# drug_in <- data_in %>%
#   filter(!Drug %in% c("placebo", "Placebo")) %>%
#   select("id" = StudyID, "tx" = Drug, "mu1tx" = Mean_endpoint, "sd1tx" = SD_endpoint, "ntx"  = N_comp_imputed_efficacy, "duration" = Weeks, Scale, Mean_baseline) %>%
#   separate(tx, c("tx", "dose_1", "dose_2", "dose_3"), remove = TRUE) %>%
#   select(-dose_1, -dose_2, -dose_3) # clean up drug name to ignore doses
# placebo_in <- data_in %>%
#   filter(Drug %in% c("placebo", "Placebo")) %>%
#   select("id" = StudyID,  "mu1ct" = Mean_endpoint, "sd1ct" = SD_endpoint, "nct"  = N_comp_imputed_efficacy)
# placebo_studies_in <- placebo_in$id
# response_in <- left_join(drug_in, placebo_in, by = "id") 
# response_in <- response_in %>%
#   mutate(placebo_study = if_else(id %in% placebo_studies_in, "yes", "no")) %>%
#   filter(placebo_study == "yes") %>%
#   filter(Scale %in% c("HAMD17", "HAMD21", "MADRS")) %>%
#   mutate(change_endpoint = ifelse(mu1tx < 0 & mu1ct < 0, "change_score", "endpoint_score")) %>%
#   drop_na()
# 
# # HAMD17 data on baseline and endpoint for AD and placebo groups
# response_in %>%
#   filter(Scale == "HAMD17" & change_endpoint == "endpoint_score") %>%
#   summarise(baseline_mean = mean(Mean_baseline, na.rm = TRUE),
#             drug_endpoint_mean = mean(mu1tx, na.rm = TRUE),
#             drug_endpoint_sd = mean(sd1tx, na.rm = TRUE),
#             placebo_endpoint_mean = mean(mu1ct, na.rm = TRUE),
#             placebo_endpoint_sd = mean(sd1ct, na.rm = TRUE))


# Define variables
# ----------------------------------------------------------------------
set.seed(20180926)
n        <- 30
id       <- c(1:n)
mu_x     <- 25 # baseline HAMD mean score
sd_x     <- 6 # baseline  HAMD score sd 
delta    <- 2 # baseline to endpoint change score mean difference between trial one (cs1) and trial two (cs2)
cutoff   <- 12.5 #given the baseline score of 25 this is the HAMD endpoint score that would equate a 50% reduction in HAMD score (i.e. the limit for achieving "response")


mu_y_tx <- 12.5 # endpoint HAMD score in treatment group
sd_y_tx <- 8 #endpoint HAMD score sd in treatment group
mu_y_ct <- 14.5 # endpoint HAMD score in control group
sd_y_ct <- 8 #endpoint HAMD score sd in control group
# delta_m_tx <- 11 # baseline to endpoint change mean in HAMD in treatment group
# delta_sd_tx <- 6 #baseline to endpoint change HAMD sd in treatment group
# delta_m_ct <- 9 # baseline to endpoint change mean in HAMD in control group
# delta_sd_ct <- 6 #baseline to endpoint change HAMD sd in control group

# create data frame
set.seed(4)
dat      <- simulate_rct(n, id, mu_x, sd_x, delta, mu_y_tx, sd_y_tx, mu_y_ct, sd_y_ct, cutoff)

