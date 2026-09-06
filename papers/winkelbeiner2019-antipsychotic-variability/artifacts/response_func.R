#
# response_func.R
#

if (!require("pacman")) install.packages("pacman")
library("pacman")
pacman::p_load(
          "rJava",
          "devtools",
          "grid",
          "papaja",
          "bookdown",
          "rmarkdown",
          "knitr",
          "tidyverse",  
          "readxl",     
          "cowplot",
          "stats",
          "backports",
          "car", 
          "arsenal",
          "magrittr",
          "lme4",
          "lmerTest",
          "MASS", 
          "metafor"
        )


# Simulate data for RCT
#-----------------------------------------------------------------------

simulate_rct <- function(n, id, mu_x, sd_x, delta, cutoff = 15) {
  #
  # simulate rct data frame
  #
  x_tx     <- round(rnorm(n, mu_x, sd_x))
  y_tx     <- round(rnorm(n, mu_x - delta, sd_x))
  x_ct     <- round(rnorm(n, mu_x, sd_x))
  y_ct     <- round(rnorm(n, mu_x - delta/3, sd_x))
  y1       <- c(y_ct[1:(n/2)], y_tx[1:(n/2)])
  x1       <- c(x_ct[1:(n/2)], x_tx[1:(n/2)])
  y2       <- c(y_ct[(n/2+1):n], y_tx[(n/2+1):n])
  x2       <- c(x_ct[(n/2+1):n], x_tx[(n/2+1):n])

  #x_tx <- round(rnorm(n/2, y_mean + raw_mu, y_sd))
  #x_ct <- round(rnorm(n/2, y_mean + delta_mu + raw_mu, y_sd))

  # data frame
  dat <- data.frame(id = id, y1 = y1, x1 = x1, 
                    tx1 = c(rep("Control", n/2), 
                            rep("Treatment", n/2)),
                    tx2 = c(rep("Treatment", n/2), 
                            rep("Control", n/2))) %>%
    mutate(id = sample(id), # shuffle ids
           x2 = x2,
           #y2=x2 + delta + (y1-x1),
           #-delta=(y1-x1) - (y2-x2)
           #-delta=y1-x1-y2+x2
           y2 = y1-x1+x2+delta,
           cs1 = y1-x1,
           cs2 = y2-x2,
           d = cs1-cs2,
           resp1 = ifelse(cs1 < -cutoff, 1, 0),
           resp2 = ifelse(cs2 < -cutoff, 1, 0))

    # correct cs2
    dat$cs2 <- dat$cs2 * c(rep(-1, n/2), rep(1, n/2))
    dat$cs1 <- dat$cs1 * c(rep(-1, n/2), rep(1, n/2))
    
    # add response rate
    resprate1tx = round(sum(dat$resp1[dat$tx1=="Treatment"]==1)/(n/2)*100, 
                      digits = 2)
    resprate1ct = round(sum(dat$resp1[dat$tx1=="Control"]==1)/(n/2)*100, 
                      digits = 2)
    resprate2tx = round(sum(dat$resp2[dat$tx2=="Treatment"]==1)/(n/2)*100, 
                      digits = 2)
    resprate2ct = round(sum(dat$resp2[dat$tx2=="Control"]==1)/(n/2)*100, 
                      digits = 2)
    
    dat$resprate1[dat$tx1=="Treatment"] <- resprate1tx
    dat$resprate1[dat$tx1=="Control"]   <- resprate1ct
    dat$resprate2[dat$tx2=="Treatment"] <- resprate2tx
    dat$resprate2[dat$tx2=="Control"]   <- resprate2ct
    
    return(dat)
}


# Compare response rates (%)
#-----------------------------------------------------------------------
# use fisher instead of z-test, because N<30 & not normally distributed
parse_fisher <- function(calc){
  tab        <- table(dat$tx1, dat$resp1)
  fisher     <- fisher.test(tab)
  print(paste("Odds ratio = ", round(fisher$estimate, 2),
              ", 95% CI: ", round(fisher$conf.int[1], 2), 
              ", ",  round(fisher$conf.int[2], 2),
              ", *p* = ", round(fisher$p.value, 3)))
}
  

# Paste p-value
#-----------------------------------------------------------------------
parse_pval <- function(pval, cutoff = 0.001) {
  #
  # parse p value
  #
  pval <- ifelse(pval < cutoff, "< 0.001", round(pval, 3))
}


# Paste t-statistic
#-----------------------------------------------------------------------
parse_tstat <- function(tstat) {
  #
  # parse t statistic
  #
  pval <- parse_pval(tstat$p.value)
  tval <- tstat$statistic
  df   <- tstat$parameter
  d    <- 2 * tval / sqrt(df)
  print(paste("Cohen's *d* = ", round(d, 2), ", ",
              "*t* (", round(df, 1), ")", " = ", round(tval, 2), ", ",
              "*P* = ", pval, sep = ""))
}


# Paste random effects model (metafor) results
#-----------------------------------------------------------------------
parse_metafor <- function(rma, model){
  #
  # print back-transformed VR, CI upper & CI lower
              
  print(paste("*VR* = ", round(rma[1,"es"], 2),
              ", 95% CI: ", round(rma[1, "ci.lb"], 2), 
              ", ", round(rma[1, "ci.ub"], 2),
              ", *P* = ", round(coef(summary(model))$pval, 2), 
              sep = ""))
}


# Report p-values with *
#-----------------------------------------------------------------------
starsfromp <- function(pval) {
  # Parses pvalues, returns asterisks

  as <- vector(mode = "character", length = length(pval))
  for (i in 1:length(pval)) {
    p <- pval[i]
    if (p < 0.1) as[i] <- "~"
    if (p < 0.05) as[i] <- "*"
    if (p < 0.01) as[i] <- "**"
    if (p < 0.001) as[i] <- "***"
  }
  return(as)
}


# Plot cross-over simulation
#-----------------------------------------------------------------------
plot_crossover <- function(dat, pointsize = 4, ...) {
  #
  # crossover graph
  #
  p <- ggplot(dat) +
    geom_point(size = pointsize, 
               aes(x = cs2, y = id, shape = "Control")) +
    geom_point(size = pointsize, 
               aes(x = cs1, y = id, shape = "Treatment")) +
    geom_segment(aes(x = cs1, xend = cs2, y = id, yend = id)) +
    theme_classic(base_size = 25) +
    theme(
      legend.title = element_blank(),
      legend.text = element_text(size=15),
      legend.position = "right"
       ) +
    scale_shape_manual(values = c("Control" = 1, 
                                  "Treatment" = 15)) +
    xlab(bquote(Delta~PANSS)) +
    ylab("Patient")
  #dev.off()    
  #plot(p)
  #return(list(p))
  return(p)
}


# Plot regression for cross-over simulation
#-----------------------------------------------------------------------
plot_regression <- function(dat, ...) {
  #
  # plot regression
  #
  rstat <- cor.test(dat$d1, dat$d2)
  pval  <- starsfromp(rstat$p.value)
  r     <- round(rstat$estimate, 2)
  
  p <- dat %>% 
    ggplot(aes(x = d1, y = d2)) +
    geom_point(size = 3) +
    geom_smooth(method = "lm") +
    theme_classic(base_size = 25) +
    theme(
    ) +
    xlab("Crossover 1") +
    ylab("Crossover 2") +
    annotate("text", x = Inf, y = Inf,
           label = paste("r=", r, pval, sep = ""),
           size = 8, hjust = 1, vjust = 1)
  return(p)
  }


# Plot net benefit 
#-----------------------------------------------------------------------
plot_benefit <- function(dat, pointsize = pointsize, ...) {
  #
  # plot net benefit
  #
  p <- dat %>% 
    ggplot(aes(x = d, y = id)) +
    geom_point(size = pointsize) +
    theme_classic(base_size = 25) +
    theme(legend.position = "right") +
    #xlim(xlim) +
    xlab("Net improvement") +
    ylab("Patient")
  return(p)
}


# Aestetics for ggplot (all elements bold)
#-----------------------------------------------------------------------
colorado <- function(src, boulder) {
  #
  # to plot elements of a graph in bold
  #
  if (!is.factor(src)) src <- factor(src)                   
  src_levels <- levels(src)                                
  brave <- boulder %in% src_levels                          
  if (all(brave)) {                                         
    b_pos <- purrr::map_int(boulder, ~which(.==src_levels)) 
    b_vec <- rep("plain", length(src_levels))              
    b_vec[b_pos] <- "bold"                                 
    b_vec                                                   
  } else {
    stop("All elements of 'boulder' must be in src")
  }
}


# Variability ratio (VR): extract results
#-----------------------------------------------------------------------
df_from_rma <- function(dat, 
                        rmamod, 
                        lblim = 0.2, 
                        ublim = 2,
                        refoffset = 16, 
                        addrefs = FALSE) {
  #
  # extract values from rma data

  # create data frame for individual studies
  fd <- data.frame(es = round(dat$yi, 2),
               se = dat$sei,
               ci.lb = round(dat$ci.lb, 2),
               ci.ub = round(dat$ci.ub, 2),
               n = dat$n,
               nsize = dat$n,
               type = "study",
               #study = attr(rmamod$yi, "slab"))
               study = dat$study)

  # inverse ranking according to effect sizes
  idx     <- (sort(fd$es, index.return = TRUE, 
                   decreasing = TRUE)$ix)
  fd      <- fd[(sort(fd$es, index.return = TRUE, 
                      decreasing = TRUE)$ix),]
  fd$rank <- 2:(nrow(dat) + 1)

  # add reference if needed
  if (addrefs == TRUE) {
    fd$refno <- rev(1:nrow(dat)) + refoffset
    fd$studywithref <- paste(fd$study, " (", fd$refno, ")", sep="")
  } else {
    fd$studywithref <- fd$study
  }
 
  pmod <- predict(rmamod, trans = exp, digits = 2)

  fd2 <- data.frame(es = round(pmod$pred, 2),
                 se = NA,
                 ci.lb = round(pmod$ci.lb, 2),
                 ci.ub = round(pmod$ci.ub, 2),
                 type = "Summary",
                 study = "Summary",
                 studywithref = "Summary",
                 rank = 1,
                 n = sum(fd$n),
                 nsize = mean(fd$n)) 

  fdd <- bind_rows(fd2, fd) 


  fdd$study2 <- factor((fdd$studywithref[fdd$rank]),
                      levels = (fdd$studywithref[fdd$rank]),
                      ordered = TRUE)

  # ci limits and arrows stuff
  fdd$ci.lb.c <- ifelse(fdd$ci.lb < lblim, fdd$es, fdd$ci.lb) 
  fdd$ci.ub.c <- ifelse(fdd$ci.ub > ublim, fdd$es, fdd$ci.ub) 
  fdd$ci.lb.a <- ifelse(fdd$ci.lb < lblim, lblim, NA) 
  fdd$ci.ub.a <- ifelse(fdd$ci.ub > ublim, ublim, NA) 

  return(fdd)
}


# Forest plot with ggplot
#-----------------------------------------------------------------------
gg_forest <- function(fdd, 
                      xlab = "Coefficient of variation ratio",
                      ylab = "Study",
                      cilab = "CVR [95% CI]",
                      ylim = c(0, 2.7)) {
  #
  # forest plot with ggplot2

  # create two shapes for polygon of summary es
  fr <- fdd[1, ]
  s1 <- data.frame(x = c(1, 0.5, 0.5, 1),
                   y = c(fr$ci.lb, fr$es, fr$es,
                       fr$ci.ub),
                   row = "lower")
  s2 <- data.frame(x = c(1, 1.5, 1.5, 1),
                   y = c(fr$ci.lb, fr$es, fr$es,
                       fr$ci.ub),
                   row = "upper")
  s <- bind_rows(s1, s2)
  
  fp1 <- fdd %>% 
    ggplot(aes(x = study2, y = es)) +
    geom_errorbar(aes(ymax = ci.ub.c, ymin = ci.lb.c,
                width = 0.0, col = type), size = 0.4) +
    geom_point(aes(shape = type, size = nsize, col = type)) +
    scale_shape_manual(values = c(19, 18)) +
    scale_color_manual(values = c("black", "white")) +
    scale_size(range = c(1, 2)) +
    theme_minimal(base_size = 11) +
    theme(
      legend.position = "",
      plot.margin = unit(c(0.5, 0.5, 0.5, 0.5), "cm"),
      legend.title = element_blank(),
      panel.grid = element_blank(),
      #axis.line.x = element_line(),
      #axis.ticks.x = element_line(),
      axis.title.x = element_text(face="bold"),
      axis.title.y = element_text(face="bold"),
      axis.text = element_text(color="black"),
      axis.text.y = element_text(size = 8, color="black")
    ) +
   ylim(ylim) +
   xlab(ylab) + 
   ylab(xlab) + 
   #scale_y_continuous(breaks = c(0, 1, 2), limits = c(0, 2), 
    #expand = c(0, 0)) +
   geom_point(data = s, aes(x = x, y = y), 
              size = 0.01, col = "white") +
   geom_polygon(data = s, aes(x = x, y = y)) 

#th <- textGrob(idheader, gp=gpar(fontsize=11, fontface="bold"))
#tl <- textGrob("Variability ratio (VR)", gp=gpar(fontsize=11,
#                                              fontface="bold"))
fp2 <- fp1 + 
  coord_flip(clip = "off") +
  geom_hline(aes(yintercept = 1), lty = 2, 
             size = 0.5, col = "black") + 
  annotate("text", y = ylim[2], x = nrow(fdd) + 1.5, 
           label = paste0(cilab), hjust = 1, fontface = "bold") +
  annotate("text", y = ylim[2], x = 1:nrow(fdd), hjust = 1,
           label = paste0(
                       sprintf("%.2f", round(fdd$es, 2)),
                        " [",
                       sprintf("%.2f", round(fdd$ci.lb, 2)),
                       ", ",
                       sprintf("%.2f", round(fdd$ci.ub, 2)),
                       "]"), size = 2.5) +
  annotate("text", y = 0.85, x = nrow(fdd) + 1.5, 
           label = "Greater in control", hjust = 1, 
           fontface = "bold")  +
  annotate("text", y = 1.15, x = nrow(fdd) + 1.5, 
           label = "Greater in treatment",
           hjust = 0, fontface = "bold")  +
  annotate("text", y = 0.05, x = nrow(fdd) + 1.5,
           label = "N", hjust = 1, fontface = "bold") +
  annotate("text", y = 0.05, x = 1:nrow(fdd), label = paste0(fdd$n), 
           hjust = 1, size = 2.5) 
  #annotation_custom(th, xmin=nrow(fdd)+1.5, xmax=nrow(fdd)+1.5,
  #                  ymin=-0.25, ymax=-0.25) 
  #annotation_custom(tl, xmin=-2.0, xmax=-2.0,
  #                ymin=1, ymax=1)

  if (sum(!is.na(fdd$ci.ub.a)) > 0) {
    fp2 <- fp2 +
      geom_segment(aes(x = study2, xend = study2, y = es,
                       yend = ci.ub.a), size = 0.4,
                 arrow = arrow(length = unit(0.01, "npc"), 
                               ends = "last", type = "closed"))
  }

  if (sum(!is.na(fdd$ci.lb.a)) > 0) {
    fp2 <- fp2 +
      geom_segment(aes(x = study2, xend = study2, y = es, 
                       yend = ci.lb.a),
                 arrow = arrow(length = unit(0.01, "npc"), 
                               ends = "last", type = "closed"))
  }
  
  #plot(fp2)
  return(list(fp2))
}


# Calculate range for M
#-----------------------------------------------------------------------
rng <- function(vec) {
  #
  # calc the range and return the delta
  r <- range(vec)
  return(abs(r[1] - r[2]))
}


# Write test statistic in plot
#-----------------------------------------------------------------------
annotate_regression <- function(lmfit, ggp) {
  #
  # annotate a regression plot
  slmfit <- coef(summary(lmfit))
  nr     <- nrow(slmfit)
  nc     <- ncol(slmfit)
  r      <- slmfit[nr, 1]
  p      <- slmfit[nr, nc]
  a      <- represearch::starsfromp(p)
  ggp2   <- ggp +
    annotate("text", x = Inf, y = Inf, size = 10,
             hjust = 1, vjust = 1,
             label = paste0("r=", round(r, 2), starsfromp(p)))
  return(ggp2)
} 
  
    
