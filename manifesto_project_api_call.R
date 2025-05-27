# ────────────────────────────────────────────────────────────────────────────
#  Bulk-download Manifesto PDFs (“original”) + sentence-level CSVs (“text”)
#  Labour (51320) | Conservative (51620) | Liberal Democrats (51421)
#  Requires: R ≥ 4.0, packages manifestoR (≥1.6), httr, readr, dplyr, purrr
# --------------------------------------------------------------------------

# install.packages(c("manifestoR","httr","readr","dplyr","purrr"))   # 1st run

library(manifestoR)
library(httr)
library(readr)
library(dplyr)
library(purrr)
library(stringr)   # for str_trim()

# 0.  API key ---------------------------------------------------------------
mp_setapikey("manifesto_apikey.txt")

# 1.  Fetch metadata for all manifestos of the three parties ---------------
uk_parties <- c(51320, 51620, 51421)

meta <- mp_metadata(party %in% uk_parties)

# 2.  Prepare output folders ----------------------------------------------
dir.create("pdf", showWarnings = FALSE)
dir.create("csv", showWarnings = FALSE)

# 3.  Download the original PDFs ------------------------------------------
base_url <- "https://manifesto-project.wzb.eu"

meta %>%                                     # keep rows with usable link & id
  filter(!is.na(url_original),
         url_original != "",
         !is.na(manifesto_id)) %>%
  mutate(full_url = if_else(str_starts(url_original, "/"),
                            paste0(base_url, url_original),
                            url_original),
         outfile  = file.path("pdf",
                              paste0(manifesto_id, ".pdf"))) %>%
  pwalk(function(full_url, outfile, manifesto_id, ...) {
    if (!file.exists(outfile)) {
      cat("▶ downloading", outfile, "\n")
      try(
        httr::GET(full_url,
                  write_disk(outfile, overwrite = TRUE),
                  progress()),
        silent = TRUE)
    }
  })

# 4.  Download machine-readable text (sentence-level CSVs) -----------------
corpus_df <- mp_corpus_df(meta, tibble_metadata = "all")

corpus_df %>%
  group_by(manifesto_id) %>%
  group_walk(~ {
    csv_path <- file.path("csv", paste0(.y$manifesto_id, ".csv"))
    write_csv(.x, csv_path)
    cat("✔ wrote", csv_path, "\n")
  })

cat("\n🏁  Done – PDFs saved in ./pdf/, text CSVs in ./csv/\n")
