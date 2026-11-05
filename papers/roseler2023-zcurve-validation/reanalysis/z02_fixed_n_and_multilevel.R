# z02: diagnose z01's K1 (permuted z still gives r = .645 under the paper's design).
# Hypothesis: in the paper's sampler the sample size falls linearly with the target replication rate
# (n = 0.3 * (P * n_success + (1 - P) * n_failure)), and z-curve's ERR depends on n -> r without any z-outcome link.
#   F1  paper design but FIXED n = 150 per sample, real z            -> the design's r with the n-confound removed
#   F2  fixed n = 150, z permuted                                     -> must be ~0 if the hypothesis is right
#   F3  ERR on permuted z vs n alone (n from 100 to 220, natural mix) -> the n-dependence itself
#   F4  one randomly drawn row per original (multilevel), paper design at fixed n = 60 (only ~200 originals exist)
# Same invocation as z01 (Docker zoo-r-zcurve:4.4.1). Prints aggregates only (blinding).
suppressMessages({library(zcurve)})
args <- commandArgs(trailingOnly = TRUE)
red <- read.csv(args[1], stringsAsFactors = FALSE); out <- args[2]
set.seed(20261106)
NS <- as.integer(Sys.getenv("NSAMP", "600"))
red <- red[!is.na(red$result), ]
red <- red[(red$result == "success") | (red$result == "informative failure to replicate"), ]
red$se <- sqrt((1 - abs(as.numeric(red$es_original))^2) / (as.numeric(red$n_original) - 2))
red$z <- abs(as.numeric(red$es_original) / red$se)
red$sigrep <- as.numeric(red$significant_replication)
d <- red[!is.na(red$z) & is.finite(red$z), ]
zc_err <- function(z) { zz <- z[!is.na(z)]; if (sum(zz > 1.96) < 10) return(NA); f <- try(suppressWarnings(zcurve(z = zz, method = "EM", bootstrap = 0)), silent = TRUE); if (inherits(f, "try-error")) return(NA); as.numeric(f$coefficients[1]) }
draw_fixed <- function(dd, n) {
  P <- runif(1); s <- dd[dd$result == "success", ]; f <- dd[dd$result != "success", ]
  ns <- min(nrow(s), round(P * n)); nf <- min(nrow(f), n - ns)
  rbind(s[sample(nrow(s), ns), ], f[sample(nrow(f), nf), ])
}
report <- function(label, res) {
  res <- res[complete.cases(res), , drop = FALSE]
  cat(sprintf("%-40s samples %4d  r(ERR,RR) %.3f  SD RR %.3f  SD ERR %.3f\n", label, nrow(res), cor(res[, 1], res[, 2]), sd(res[, 1]), sd(res[, 2])))
  write.csv(res, file.path(out, paste0("z02_", label, ".csv")), row.names = FALSE)
}
F1 <- t(sapply(1:NS, function(i) { s <- draw_fixed(d, 150); c(mean(s$sigrep, na.rm = TRUE), zc_err(s$z)) })); report("F1_fixed_n150_real_z", F1)
dp <- d; dp$z <- sample(dp$z)
F2 <- t(sapply(1:NS, function(i) { s <- draw_fixed(dp, 150); c(mean(s$sigrep, na.rm = TRUE), zc_err(s$z)) })); report("F2_fixed_n150_permuted_z", F2)
F3 <- t(sapply(1:NS, function(i) { n <- sample(100:220, 1); s <- dp[sample(nrow(dp), n), ]; c(n, zc_err(s$z)) }))
F3 <- F3[complete.cases(F3), ]
cat(sprintf("F3_permuted_natural_mix: r(n, ERR) = %.3f ; ERR at n<=130 %.3f vs n>=190 %.3f\n", cor(F3[, 1], F3[, 2]), mean(F3[F3[, 1] <= 130, 2]), mean(F3[F3[, 1] >= 190, 2])))
write.csv(F3, file.path(out, "z02_F3_n_vs_err_permuted.csv"), row.names = FALSE)
F4 <- t(sapply(1:NS, function(i) { u <- d[sample(nrow(d)), ]; u <- u[!duplicated(u$ref_original), ]; s <- draw_fixed(u, 60); c(mean(s$sigrep, na.rm = TRUE), zc_err(s$z)) })); report("F4_one_row_per_original_fixed_n60", F4)
# K4 again with NA-safe group statistics (z01's K4 crashed on a group whose RR was all NA)
g <- d$source; keep <- names(table(g))[table(g) >= 30]
r <- do.call(rbind, lapply(keep, function(k) { s <- d[g == k & !is.na(g), ]; data.frame(group = k, n = nrow(s), n_rr = sum(!is.na(s$sigrep)), RR = mean(s$sigrep, na.rm = TRUE), ERR = zc_err(s$z)) }))
r <- r[!is.na(r$RR) & !is.na(r$ERR), ]
print(r, row.names = FALSE, digits = 3)
cat(sprintf("K4 source groups (%d): Pearson r(ERR,RR) = %.3f ; Spearman = %.3f ; mean |ERR - RR| = %.3f ; mean ERR - RR = %.3f\n",
            nrow(r), cor(r$ERR, r$RR), cor(r$ERR, r$RR, method = "spearman"), mean(abs(r$ERR - r$RR)), mean(r$ERR - r$RR)))
write.csv(r, file.path(out, "z02_K4_source.csv"), row.names = FALSE)
