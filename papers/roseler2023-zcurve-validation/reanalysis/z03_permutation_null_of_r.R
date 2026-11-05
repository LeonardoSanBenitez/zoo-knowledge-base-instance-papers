# z03: the permutation null distribution of the paper's statistic r(ERR, RR) under its own design.
# z02/F2 showed that ONE permutation of z (no z-outcome link) gave r = -0.30 at fixed n: the stratified design turns
# the chance difference between the two fixed pools (success rows vs failure rows) into a large |r|. Here: NPERM
# independent permutations, each scored by r over NS stratified samples (paper's sampler, fixed n = 150), and the
# real-data r for comparison. Also the trivial statistic share(z > 2.8) under the same permutations.
# Same Docker invocation as z01. Aggregates only.
suppressMessages({library(zcurve)})
args <- commandArgs(trailingOnly = TRUE)
red <- read.csv(args[1], stringsAsFactors = FALSE); out <- args[2]
set.seed(20261107)
NPERM <- as.integer(Sys.getenv("NPERM", "30")); NS <- as.integer(Sys.getenv("NSAMP", "120"))
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
r_of <- function(dd, stat) {
  m <- t(sapply(1:NS, function(i) { s <- draw_fixed(dd, 150); c(mean(s$sigrep, na.rm = TRUE), if (stat == "zc") zc_err(s$z) else mean(s$z > 2.8)) }))
  m <- m[complete.cases(m), ]; cor(m[, 1], m[, 2])
}
real_zc <- r_of(d, "zc"); real_sh <- r_of(d, "share")
perm <- t(sapply(1:NPERM, function(j) { dp <- d; dp$z <- sample(dp$z); c(r_of(dp, "zc"), r_of(dp, "share")) }))
cat(sprintf("real data: r(ERR,RR) = %.3f ; r(share z>2.8, RR) = %.3f\n", real_zc, real_sh))
cat(sprintf("permutation null over %d permutations (each r over %d samples):\n", NPERM, NS))
cat(sprintf("  z-curve ERR: mean %.3f, sd %.3f, min %.3f, max %.3f, share |r| > .5: %.2f\n", mean(perm[, 1]), sd(perm[, 1]), min(perm[, 1]), max(perm[, 1]), mean(abs(perm[, 1]) > .5)))
cat(sprintf("  share z>2.8: mean %.3f, sd %.3f, min %.3f, max %.3f, share |r| > .5: %.2f\n", mean(perm[, 2]), sd(perm[, 2]), min(perm[, 2]), max(perm[, 2]), mean(abs(perm[, 2]) > .5)))
write.csv(data.frame(r_zcurve = perm[, 1], r_share = perm[, 2]), file.path(out, "z03_permutation_r.csv"), row.names = FALSE)
