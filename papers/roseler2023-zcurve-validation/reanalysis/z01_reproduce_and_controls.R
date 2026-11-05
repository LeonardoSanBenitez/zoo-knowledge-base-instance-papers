# Roeseler (2023 preprint) "Predicting Replication Rates with Z-Curve" -- reproduce, then known-answer controls.
#
# Usage (from the zoo root, Docker image zoo-r-zcurve:4.4.1 = zoo-r-psych + zcurve + openxlsx):
#   D=$(python zoo-knowledge-base/tools/assets.py path paper-downloads/roseler2023-zcurve-validation)
#   docker run --rm -v "$D/osf_k4d6w/files/osfstorage/Code and Data":/data:ro \
#     -v "$PWD/zoo-knowledge-base/instance-papers/papers/roseler2023-zcurve-validation/reanalysis":/work \
#     zoo-r-zcurve:4.4.1 Rscript /work/z01_reproduce_and_controls.R /data/zcurve_validation_red_data.csv /work/out
#
# BLINDING (mark's known-answer control): prints corpus aggregates and group aggregates over groups of >= 30 rows
# only; never a row, reference or per-paper value.
#
# A  reproduce the paper's design (stratified on outcome) -> r(ERR, RR), lm slope/intercept, means (paper: r .945,
#    RR = 1.850 ERR - .573, M RR .43 ERR .54 EDR .24; abstract says r = .933)
# K1 same design, z permuted across rows (no z-outcome link)          -> r must collapse if r measures z-curve's skill
# K2 same design, z-curve replaced by a trivial statistic (share of |z| > 2.8) -> if r is as high, r is not specific
# K3 natural random 30% subsamples (no stratification)                -> the variation real literatures would show
# K4 natural groups: source project and discipline (>= 30 rows)       -> does ERR rank real literatures by RR?
suppressMessages({library(zcurve)})
args <- commandArgs(trailingOnly = TRUE)
red <- read.csv(args[1], stringsAsFactors = FALSE)
out <- args[2]; dir.create(out, showWarnings = FALSE)
set.seed(20261105)
NS <- as.integer(Sys.getenv("NSAMP", "1000"))
red <- red[!is.na(red$result), ]
red <- red[(red$result == "success") | (red$result == "informative failure to replicate"), ]
red$se <- sqrt((1 - abs(as.numeric(red$es_original))^2) / (as.numeric(red$n_original) - 2))
red$z <- abs(as.numeric(red$es_original) / red$se)
red$sigrep <- as.numeric(red$significant_replication)
d <- red[!is.na(red$z) & is.finite(red$z), ]
cat("rows after outcome filter:", nrow(red), " with z:", nrow(d), " unique ref_original:", length(unique(d$ref_original)), "\n")
cat("RR (mean significant_replication) overall:", round(mean(d$sigrep, na.rm = TRUE), 3),
    " success share:", round(mean(d$result == "success"), 3), "\n")
# individual-level discrimination of z for the outcome used as RR
auc <- function(score, y) { y <- as.logical(y); ok <- !is.na(y) & !is.na(score); r <- rank(score[ok]); n1 <- sum(y[ok]); n0 <- sum(!y[ok]); (sum(r[y[ok]]) - n1 * (n1 + 1) / 2) / (n1 * n0) }
cat("individual AUC of z for significant_replication:", round(auc(d$z, d$sigrep == 1), 3), "\n")
cat("individual AUC of z for success:", round(auc(d$z, d$result == "success"), 3), "\n")

zc_err <- function(z) { zz <- z[!is.na(z)]; if (sum(zz > 1.96) < 10) return(c(NA, NA)); f <- try(zcurve(z = zz, method = "EM", bootstrap = 0), silent = TRUE); if (inherits(f, "try-error")) return(c(NA, NA)); as.numeric(f$coefficients[1:2]) }

draw_strat <- function(dd, prop = 0.3) {
  P <- runif(1)
  s <- dd[dd$result == "success", ]; f <- dd[dd$result != "success", ]
  rbind(s[sample(nrow(s), round(prop * P * nrow(s))), ], f[sample(nrow(f), round(prop * (1 - P) * nrow(f))), ])
}
run <- function(label, sampler, stat = "zcurve", dd = d) {
  res <- t(sapply(1:NS, function(i) {
    smp <- sampler(dd)
    rr <- mean(smp$sigrep, na.rm = TRUE)
    if (stat == "zcurve") e <- zc_err(smp$z) else e <- c(mean(smp$z > 2.8), NA)
    c(rr, e, nrow(smp))
  }))
  colnames(res) <- c("RR", "ERR", "EDR", "n")
  res <- res[complete.cases(res[, 1:2]), , drop = FALSE]
  m <- lm(RR ~ ERR, data = as.data.frame(res))
  cat(sprintf("%-42s samples %4d  r(ERR,RR) %.3f  slope %.3f  intercept %.3f  M RR %.3f  M ERR %.3f  SD RR %.3f  SD ERR %.3f  median n %d\n",
              label, nrow(res), cor(res[, "ERR"], res[, "RR"]), coef(m)[2], coef(m)[1], mean(res[, "RR"]), mean(res[, "ERR"]),
              sd(res[, "RR"]), sd(res[, "ERR"]), as.integer(median(res[, "n"]))))
  write.csv(res, file.path(out, paste0("z01_", gsub("[^A-Za-z0-9]+", "_", label), ".csv")), row.names = FALSE)
  invisible(res)
}
A <- run("A_paper_design_stratified", draw_strat)
dperm <- d; dperm$z <- sample(dperm$z)
K1 <- run("K1_stratified_z_permuted", draw_strat, dd = dperm)
K2 <- run("K2_stratified_trivial_share_z_gt_2.8", draw_strat, stat = "share")
K3 <- run("K3_natural_random_30pct", function(dd) dd[sample(nrow(dd), round(0.3 * nrow(dd))), ])
# K4 natural groups
grp <- function(col) {
  g <- d[[col]]; tab <- table(g); keep <- names(tab)[tab >= 30]
  rows <- lapply(keep, function(k) { s <- d[g == k & !is.na(g), ]; e <- zc_err(s$z); data.frame(group = k, n = nrow(s), RR = mean(s$sigrep, na.rm = TRUE), ERR = e[1], EDR = e[2]) })
  r <- do.call(rbind, rows); r <- r[!is.na(r$ERR), ]
  cat("\nK4 groups by", col, "\n"); print(r, row.names = FALSE, digits = 3)
  if (nrow(r) >= 3) cat(sprintf("  across %d groups: r(ERR,RR) = %.3f ; Spearman = %.3f ; mean |ERR - RR| = %.3f\n", nrow(r), cor(r$ERR, r$RR), cor(r$ERR, r$RR, method = "spearman"), mean(abs(r$ERR - r$RR))))
  write.csv(r, file.path(out, paste0("z01_K4_", col, ".csv")), row.names = FALSE)
}
grp("source"); grp("discipline")
