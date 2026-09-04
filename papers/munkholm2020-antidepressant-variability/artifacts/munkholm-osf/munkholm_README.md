# Individual response to antidepressants for depression in adults - a meta-analysis and simulation study

## Authors
- Klaus Munkholm, M.D., DMSc.  
- Stephanie Winkelbeiner, Ph.D.  
- Philipp Homan, M.D., Ph.D.  

## Getting started
This repository contains all the data and analysis code to reproduce the manuscript "Individual response to antidepressants for depression in adults - a meta-analysis and simulation study".  
These instructions describe how to reproducing the analyses, figures, and the final manuscript and supplement.
  
## Prerequisites
Download the project source files (https://osf.io/5gpe4/) to the root of an R project directory. Download the dataset from Cipriani et al., The Lancet 2019 (https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(17)32802-7/fulltext) from: https://data.mendeley.com/datasets/83rthbp8ys/2. Place the downloaded dataset in a subfolder named "data" and create an empty subfolder named "figures.

## Reproducing the manuscript
The manuscript and supplement are knitted from the manuscript_accepted_upload.Rmd and the supplement1_accepted_upload.Rmd and supplement2_accepted_upload.Rmd files, respectively. 

## Built With
R version 3.6.0 (2019-04-26).  
Platform: x86_64-w64-mingw32/x64 (64-bit).  
Running under: Windows 10 x64 (build 17763).  

## Session info
#### Attached packages  
forcats_0.4.0     stringr_1.4.0     dplyr_0.8.3       purrr_0.3.2       readr_1.3.1       tidyr_1.0.0       tibble_2.1.3      tidyverse_1.2.1   float_0.2-3      
here_0.1          ggpubr_0.2.3      ggplot2_3.2.1     table1_1.1        gridExtra_2.3     ggsci_2.9         kableExtra_1.1.0  meta_4.9-6        metafor_2.1-0    
MASS_7.3-51.4     lmerTest_3.1-0    lme4_1.1-21       Matrix_1.2-17     magrittr_1.5      arsenal_3.3.0     car_3.0-3         carData_3.0-2     backports_1.1.4  
cowplot_1.0.0     readxl_1.3.1      knitr_1.25        rmarkdown_1.15    bookdown_0.13     papaja_0.1.0.9842 devtools_2.2.1    usethis_1.5.1     rJava_0.9-11     
pacman_0.5.1      sessioninfo_1.1.1.

#### Packages loaded via a namespace (and not attached)  
minqa_1.2.4         colorspace_1.4-1    ggsignif_0.6.0      ellipsis_0.3.0      rio_0.5.16          rprojroot_1.3-2     fs_1.3.1            rstudioapi_0.10    
remotes_2.1.0       lubridate_1.7.4     xml2_1.2.2          splines_3.6.0       pkgload_1.0.2       zeallot_0.1.0       Formula_1.2-3       jsonlite_1.6       
nloptr_1.2.1        broom_0.5.2         compiler_3.6.0      httr_1.4.1          assertthat_0.2.1    lazyeval_0.2.2      cli_1.1.0           htmltools_0.3.6    
prettyunits_1.0.2   tools_3.6.0         gtable_0.3.0        glue_1.3.1          Rcpp_1.0.2          cellranger_1.1.0    vctrs_0.2.0         nlme_3.1-141       
xfun_0.9            ps_1.3.0            openxlsx_4.1.0.1    testthat_2.2.1      rvest_0.3.4         lifecycle_0.1.0     scales_1.0.0        hms_0.5.1          
yaml_2.2.0          curl_4.1            memoise_1.1.0       stringi_1.4.3       highr_0.8           desc_1.2.0          boot_1.3-23         pkgbuild_1.0.5     
zip_2.0.4           rlang_0.4.0         pkgconfig_2.0.3     evaluate_0.14       lattice_0.20-38     labeling_0.3        processx_3.4.1      tidyselect_0.2.5   
R6_2.4.0            generics_0.0.2      pillar_1.4.2        haven_2.1.1         foreign_0.8-72      withr_2.1.2         abind_1.4-5         modelr_0.1.5       
crayon_1.3.4        data.table_1.12.2   callr_3.3.2         digest_0.6.21       webshot_0.5.1       numDeriv_2016.8-1.1 munsell_0.5.0       viridisLite_0.3.0. 

## License
See the MIT License information below the project description on osf.io.