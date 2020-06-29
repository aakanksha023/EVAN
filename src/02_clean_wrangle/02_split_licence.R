# author: Keanna Knebel
# date: 2020-05-11
#
#
"This script reads in two .csv files with the same columns and combines 
 them into a single dataframe. The combined dataset is grouped by business
 name and location, and a new column is created to assign a business_id. The
 grouped data is then split into train, validate, and test sets. This script
 takes a file_path from which to read the .csv data files, a filepath to write 
 the processed .csv file, and the 2 filenames for the unprocessed data.
 
Usage: scripts/02_clean_wrangle/02_split_licence.R --filepath_in=<filepath_in> --filepath_out=<filepath_out> --filename_1=<filename_1> --filename_2=<filename_2>

Options:
--filepath_in=<filepath_in>     Path to raw data directory
--filepath_out=<filepath_out>   Path to processed data directory
--filename_1=<filename_1>       filename of raw .csv data file
--filename_2=<filename_2>       filename of second raw .csv data file
" -> doc

# Variables to pass in for Deetken evan
# filepath_in = 'data/raw'
# filepath_out = 'data/processed'
  # filename_1 = 'licence_1997_2012.csv'
  # filename_2 = 'licence_2013_current.csv'

suppressPackageStartupMessages({
  library(tidyverse)
  library(docopt)
  library(data.table)})
set.seed(2020)

opt <- docopt(doc)

main <- function(filepath_in, filepath_out, filename_1, filename_2) {
  
  # initialize progress bar 
  bar = txtProgressBar(max = 10, style = 3)
  setTxtProgressBar(bar, 0)
  
  # set column specifications
  col_types <- cols(FOLDERYEAR = col_double(),
                    LicenceRSN = col_double(),
                    LicenceNumber = col_character(),
                     LicenceRevisionNumber = col_character(),
                     BusinessName = col_character(),
                     BusinessTradeName = col_character(),
                     Status = col_character(),
                     IssuedDate = col_date(format = ""),
                     ExpiredDate = col_date(format = ""),
                     BusinessType = col_character(),
                     BusinessSubType = col_character(),
                     Unit = col_character(),
                     UnitType = col_character(),
                     House = col_character(),
                     Street = col_character(),
                     City = col_character(),
                     Province = col_character(),
                     Country = col_character(),
                     PostalCode = col_character(),
                     LocalArea = col_character(),
                     NumberofEmployees = col_character(),
                     FeePaid = col_double(),
                     ExtractDate = col_datetime(format = ""),
                     Geom = col_character())
  # open raw csv files
  csv1 <- (read_delim(paste0(filepath_in, "/", filename_1), delim = ";", col_types = col_types)) %>% 
    suppressWarnings()
  setTxtProgressBar(bar, 1)
  csv2 <- suppressWarnings(read_delim(paste0(filepath_in, "/", filename_2), delim = ";", col_types = col_types)) %>% 
    suppressWarnings()
  setTxtProgressBar(bar, 2)

  # combine the raw csv datasets
  combined_df <- csv1 %>% rbind(csv2)

  # group by business name + location
  combined_grouped_df <- combined_df %>%
    group_by(BusinessName, PostalCode, LocalArea, City, BusinessTradeName) %>%
    mutate(business_id = group_indices())
  setTxtProgressBar(bar, 3)

  # reorder columns
  combined_grouped_df <- combined_grouped_df[, c(25, 1:24)]

  # arrange dataset by business_id
  combined_grouped_df <- combined_grouped_df %>%
    arrange(business_id, IssuedDate)
  setTxtProgressBar(bar, 4)

  # save dataframe to csv
  dir.create(filepath_out, showWarnings = FALSE)
  combined_grouped_df %>% write_csv(paste0(filepath_out, "/combined_licences.csv"))
  setTxtProgressBar(bar, 5)

  # split data in train, validation, and test sets
  ids <- unique(combined_grouped_df$business_id)

  train_ids <- sample(1:length(ids), 0.7 * length(ids), replace = FALSE)
  test_valid_ids <- setdiff(1:length(ids), train_ids)
  test_ids <- sample(test_valid_ids, 0.7 * length(test_valid_ids), replace = FALSE)
  valid_ids <- setdiff(test_valid_ids, test_ids)
  setTxtProgressBar(bar, 6)
  
  dt <- as.data.table(combined_grouped_df)
  train_dt <- dt %>%
    filter(business_id %in% train_ids)
  setTxtProgressBar(bar, 7)
  valid_dt <- dt %>%
    filter(business_id %in% valid_ids)
  setTxtProgressBar(bar, 8)
  test_dt <- dt %>%
    filter(business_id %in% test_ids)
  setTxtProgressBar(bar, 9)

  # write csv files to filepath
  write_csv(train_dt, paste0(filepath_out, "/train.csv"))
  write_csv(valid_dt, paste0(filepath_out, "/validate.csv"))
  write_csv(test_dt, paste0(filepath_out, "/test.csv"))
  setTxtProgressBar(bar, 10)
  close(bar)
}

main(opt$filepath_in, opt$filepath_out, opt$filename_1, opt$filename_2)
