#
# density_plots.R
#
#---------------------------------------------------------------------------#
#---------------generate data for marginal density plots -------------------#
#---------------------------------------------------------------------------#

#define variables
set.seed(20180926)
ns        <- 30
ids       <- sample(c(1:ns))
m_ctr     <- -10 # mean HAMD baseline to endpoint change score in control condition
sd_ctr     <- 6 # HAMD baseline to endpoint change score SD in control condition
m_tx     <- -12 # mean HAMD baseline to endpoint change score in treatment condition
sd_tx     <- 6 # HAMD baseline to endpoint change score SD in treatment condition
subgroup_two <- c(rep("group_1", 15), rep("group_2", 15))

simulate_rct_variance <- function(ns, ids, m_ctr, sd_ctr, m_tx, sd_tx, subgroup_two) {
  
  hamd_ctr <-  sort(round(rnorm(ns, m_ctr, sd_ctr))) #actual
  hamd_tx  <-  round(rnorm(ns, m_tx, sd_tx)) #actual
  hamd_tx_eq  <-  hamd_ctr #A
  hamd_tx_const  <-  hamd_ctr-6 #B
  hamd_tx_grp1  <-  hamd_ctr[1:15] - 10 #C 
  hamd_tx_grp2  <-  hamd_ctr[16:30] + 10 #C 
  hamd_tx_increase_var  <-  round(rnorm(ns, m_tx, sd_ctr+4)) #D
  hamd_tx_grp3  <-  hamd_ctr[1:15] +4 #E 
  hamd_tx_grp4  <-  hamd_ctr[16:30] -4 #E 
  hamd_tx_decrease_var  <-  round(rnorm(ns, m_tx, sd_ctr-4)) #F
  
  var_data <- tibble(ids,
                     subgroup = subgroup_two, 
                     control = hamd_ctr, 
                     hamd_tx,
                     hamd_tx_eq, 
                     hamd_tx_const,
                     hamd_tx_grp_incr_var = c(hamd_tx_grp1, hamd_tx_grp2),
                     hamd_tx_increase_var,
                     hamd_tx_grp_decr_var = c(hamd_tx_grp4, hamd_tx_grp3),
                     hamd_tx_decrease_var)

}

#six scenarios
#A: no treatment effect
#B: constant treatment effect, equal variances
#C: subgroup-by-treatment effect, higher variance in treatment group
#D: patient-by-treatment effect, higher variance in treatment group
#E: subgroup-by-treatment effect, lower variance in treatment group
#F: patient-by-treatment effect, lower variance in treatment group
#generate dataset for simulations
var_data <- simulate_rct_variance(ns, ids, m_ctr, sd_ctr, m_tx, sd_tx, subgroup_two)
#longitudinal dataset for marginal plots
dat_A <- var_data %>%
  gather(control_vs_treatment , hamd, control, hamd_tx_eq) %>%
  select(ids, control_vs_treatment, hamd)
dat_B <- var_data %>%
  gather(control_vs_treatment , hamd, control, hamd_tx_const) %>%
  select(ids, control_vs_treatment, hamd)
dat_C <- var_data %>%
  gather(control_vs_treatment , hamd, control, hamd_tx_grp_incr_var) %>%
  select(ids, control_vs_treatment, hamd)
dat_D <- var_data %>%
  gather(control_vs_treatment , hamd, control, hamd_tx_increase_var) %>%
  select(ids, control_vs_treatment, hamd)
dat_E <- var_data %>%
  gather(control_vs_treatment , hamd, control, hamd_tx_grp_decr_var) %>%
  select(ids, control_vs_treatment, hamd)
dat_F <- var_data %>%
  gather(control_vs_treatment , hamd, control, hamd_tx_decrease_var) %>%
  select(ids, control_vs_treatment, hamd)

#plots
#B plot
#scatterplot
B_plot <- ggplot(var_data) +
  geom_point(size = pointsize - 1, 
             aes(x = control, y = ids, shape = "Control")) +
  geom_point(size = pointsize, 
             aes(x = hamd_tx_const, y = ids, shape = "Treatment")) +
  geom_segment(aes(x = control, xend = hamd_tx_const, y = ids, yend = ids)) +
  theme_classic(base_size = 25) +
  theme(
    legend.title = element_blank(),
    legend.text = element_text(size=15),
    legend.position = "right") +
  scale_shape_manual(values = c("Control" = 0, 
                                "Treatment" = 15)) +
  xlab(bquote(Delta~HAMD)) +
  ylab("Patient")

#add density plot
margplot_B <- ggdensity(data = dat_B, x = "hamd", fill = "control_vs_treatment", palette = "grey")

# Cleaning the plots
B_plot <- B_plot + border() + theme(legend.position="bottom")
margplot_B <- margplot_B + clean_theme() + rremove("legend")

# Arranging the plot using cowplot
plot_b <- plot_grid(margplot_B, NULL, B_plot, align = "v",
          rel_widths = c(2, 1), rel_heights = c(1, 2))

#C plot
C_plot <- ggplot(var_data) +
  geom_point(size = pointsize - 1, 
             aes(x = control, y = ids, shape = "Control")) +
  geom_point(size = pointsize, 
             aes(x = hamd_tx_grp_incr_var, y = ids, shape = "Treatment")) +
  geom_segment(aes(x = control, xend = hamd_tx_grp_incr_var, y = ids, yend = ids)) +
  theme_classic(base_size = 25) +
  theme(
    legend.title = element_blank(),
    legend.text = element_text(size=15),
    legend.position = "right") +
  scale_shape_manual(values = c("Control" = 0, 
                                "Treatment" = 15)) +
  xlab(bquote(Delta~HAMD)) +
  ylab("Patient")
#add density plot
margplot_C <- ggdensity(data = dat_C, x = "hamd", fill = "control_vs_treatment", palette = "grey")

# Cleaning the plots
C_plot <- C_plot + border() + theme(legend.position="bottom")
margplot_C <- margplot_C + clean_theme() + rremove("legend")

# Arranging the plot using cowplot
plot_c <- plot_grid(margplot_C, NULL, C_plot, align = "v",
          rel_widths = c(2, 1), rel_heights = c(1, 2))

#D plot
D_plot <- ggplot(var_data) +
  geom_point(size = pointsize - 1, 
             aes(x = control, y = ids, shape = "Control")) +
  geom_point(size = pointsize, 
             aes(x = hamd_tx_increase_var, y = ids, shape = "Treatment")) +
  geom_segment(aes(x = control, xend = hamd_tx_increase_var, y = ids, yend = ids)) +
  theme_classic(base_size = 25) +
  theme(
    legend.title = element_blank(),
    legend.text = element_text(size=15),
    legend.position = "right") +
  scale_shape_manual(values = c("Control" = 0, 
                                "Treatment" = 15)) +
  xlab(bquote(Delta~HAMD)) +
  ylab("Patient")
#add density plot
margplot_D <- ggdensity(data = dat_D, x = "hamd", fill = "control_vs_treatment", palette = "grey")

# Cleaning the plots
D_plot <- D_plot + border() + theme(legend.position="bottom")
margplot_D <- margplot_D + clean_theme() + rremove("legend")

# Arranging the plot using cowplot
plot_d <- plot_grid(margplot_D, NULL, D_plot, align = "v",
          rel_widths = c(2, 1), rel_heights = c(1, 2))

#plot all three together
# plot all together
p15 <- plot_grid(plot_b, plot_c, plot_d,
                   nrow = 1,
                   labels = "auto",
                   label_size = 30,
                   align = "hav")

ggsave(plot = p15, filename = here("figures", "variation_scenarios_fig4.pdf"),
       width = 15.80, height = 8)
