Wrangling Licence Datasets
================

``` r
library(tidyverse)
```

    ## ── Attaching packages ───────────────────────────────────────────────────────────────────────────────────── tidyverse 1.2.1 ──

    ## ✓ ggplot2 3.2.1     ✓ purrr   0.3.3
    ## ✓ tibble  2.1.3     ✓ dplyr   0.8.3
    ## ✓ tidyr   1.0.0     ✓ stringr 1.4.0
    ## ✓ readr   1.3.1     ✓ forcats 0.4.0

    ## ── Conflicts ──────────────────────────────────────────────────────────────────────────────────────── tidyverse_conflicts() ──
    ## x dplyr::filter() masks stats::filter()
    ## x dplyr::lag()    masks stats::lag()

This file serves to combined the buisness licence data into a singular
csv file and group by the buisness name + location.

``` r
# read in the 2013-2020 licence data
licence_2013_cur <- read_delim('../data/raw/licence_2013_current.csv', delim=';')
```

    ## Parsed with column specification:
    ## cols(
    ##   .default = col_character(),
    ##   FOLDERYEAR = col_double(),
    ##   LicenceRSN = col_double(),
    ##   IssuedDate = col_datetime(format = ""),
    ##   ExpiredDate = col_date(format = ""),
    ##   House = col_double(),
    ##   FeePaid = col_double(),
    ##   ExtractDate = col_datetime(format = "")
    ## )

    ## See spec(...) for full column specifications.

    ## Warning: 13 parsing failures.
    ##    row   col               expected  actual                                   file
    ##  21893 House no trailing characters  &520   '../data/raw/licence_2013_current.csv'
    ##  34604 House no trailing characters  &520   '../data/raw/licence_2013_current.csv'
    ##  69803 House no trailing characters  &520   '../data/raw/licence_2013_current.csv'
    ##  73251 House no trailing characters C       '../data/raw/licence_2013_current.csv'
    ## 124919 House no trailing characters  & 2070 '../data/raw/licence_2013_current.csv'
    ## ...... ..... ...................... ....... ......................................
    ## See problems(...) for more details.

``` r
licence_2013_cur
```

    ## # A tibble: 504,360 x 24
    ##    FOLDERYEAR LicenceRSN LicenceNumber LicenceRevision… BusinessName
    ##         <dbl>      <dbl> <chr>         <chr>            <chr>       
    ##  1         14    2154508 14-142098     00               Flok Enterp…
    ##  2         14    2154510 14-142100     00               Joshua Lawr…
    ##  3         14    2154511 14-142101     00               Greater Van…
    ##  4         14    2154512 14-142102     00               Pay Low Aut…
    ##  5         14    2154517 14-142107     00               HP3 Clothin…
    ##  6         14    2154518 14-142108     00               Honey Gifts…
    ##  7         14    2154521 14-142111     00               (Michael Lu…
    ##  8         14    2154524 14-142114     00               High Output…
    ##  9         14    2154528 14-142118     00               Wang On Bli…
    ## 10         14    2154531 14-142121     00               Laura L Fre…
    ## # … with 504,350 more rows, and 19 more variables: BusinessTradeName <chr>,
    ## #   Status <chr>, IssuedDate <dttm>, ExpiredDate <date>, BusinessType <chr>,
    ## #   BusinessSubType <chr>, Unit <chr>, UnitType <chr>, House <dbl>,
    ## #   Street <chr>, City <chr>, Province <chr>, Country <chr>, PostalCode <chr>,
    ## #   LocalArea <chr>, NumberofEmployees <chr>, FeePaid <dbl>,
    ## #   ExtractDate <dttm>, Geom <chr>

``` r
# read in the 1997-2012 licence data
licence_1997_2012 <- read_delim('../data/raw/licence_1997_2012.csv', delim=';')
```

    ## Parsed with column specification:
    ## cols(
    ##   .default = col_character(),
    ##   FOLDERYEAR = col_double(),
    ##   LicenceRSN = col_double(),
    ##   IssuedDate = col_date(format = ""),
    ##   ExpiredDate = col_date(format = ""),
    ##   FeePaid = col_double(),
    ##   ExtractDate = col_datetime(format = "")
    ## )

    ## See spec(...) for full column specifications.

    ## Warning: 34 parsing failures.
    ##    row         col   expected    actual                                file
    ##  27338 ExpiredDate date like  200-12-31 '../data/raw/licence_1997_2012.csv'
    ##  75690 ExpiredDate date like  203-12-31 '../data/raw/licence_1997_2012.csv'
    ## 128575 ExpiredDate date like  209-12-31 '../data/raw/licence_1997_2012.csv'
    ## 128998 ExpiredDate date like  209-12-31 '../data/raw/licence_1997_2012.csv'
    ## 202309 ExpiredDate date like  201-12-31 '../data/raw/licence_1997_2012.csv'
    ## ...... ........... .......... ......... ...................................
    ## See problems(...) for more details.

``` r
# combine the licence datasets
all_licences <- licence_1997_2012 %>% rbind(licence_2013_cur)
all_licences
```

    ## # A tibble: 1,463,270 x 24
    ##    FOLDERYEAR LicenceRSN LicenceNumber LicenceRevision… BusinessName
    ##         <dbl>      <dbl> <chr>         <chr>            <chr>       
    ##  1         98     136556 98-176044     00               T S G Sales…
    ##  2         98     136559 98-176047     00               Datin Commu…
    ##  3         98     136562 98-176050     00               (Sajdha sam…
    ##  4         98     136564 98-176052     00               The News Ho…
    ##  5         98     136566 98-176054     00               Florence Ga…
    ##  6         98     136568 98-176056     00               (Pierre Smi…
    ##  7         98     136570 98-176058     00               Advanced Ph…
    ##  8         98     136572 98-176060     00               Nirwan Smok…
    ##  9         98     136574 98-176062     00               Sylvia F Ka…
    ## 10         98     136575 98-176063     00               Derek Norto…
    ## # … with 1,463,260 more rows, and 19 more variables: BusinessTradeName <chr>,
    ## #   Status <chr>, IssuedDate <date>, ExpiredDate <date>, BusinessType <chr>,
    ## #   BusinessSubType <chr>, Unit <chr>, UnitType <chr>, House <chr>,
    ## #   Street <chr>, City <chr>, Province <chr>, Country <chr>, PostalCode <chr>,
    ## #   LocalArea <chr>, NumberofEmployees <chr>, FeePaid <dbl>,
    ## #   ExtractDate <dttm>, Geom <chr>

``` r
# group by buisness name + location
all_licences_group <- all_licences %>% 
  group_by(BusinessName,PostalCode) %>% 
  mutate(business_id = group_indices())

# reorder columns
all_licences_group <- all_licences_group[, c(25, 1:24)]

# arrange dataset by buisness_id
all_licences_group <- all_licences_group %>% 
  arrange(business_id) 
all_licences_group
```

    ## # A tibble: 1,463,270 x 25
    ## # Groups:   BusinessName, PostalCode [229,682]
    ##    business_id FOLDERYEAR LicenceRSN LicenceNumber LicenceRevision… BusinessName
    ##          <int>      <dbl>      <dbl> <chr>         <chr>            <chr>       
    ##  1           1         18    3100450 18-516072     00               !Exotics By…
    ##  2           1         19    3265242 19-139570     00               !Exotics By…
    ##  3           2          6    1010837 06-140328     00               .243 Racing…
    ##  4           2          7    1108572 07-131745     00               .243 Racing…
    ##  5           2          4     804123 04-036444     00               .243 Racing…
    ##  6           2          5     884526 05-112560     00               .243 Racing…
    ##  7           3          3     749871 03-504332     00               .243 Racing…
    ##  8           3          4     816583 04-047530     00               .243 Racing…
    ##  9           3          3     749872 03-504333     00               .243 Racing…
    ## 10           4         97      21678 97-048639     00               '86 Fashion…
    ## # … with 1,463,260 more rows, and 19 more variables: BusinessTradeName <chr>,
    ## #   Status <chr>, IssuedDate <date>, ExpiredDate <date>, BusinessType <chr>,
    ## #   BusinessSubType <chr>, Unit <chr>, UnitType <chr>, House <chr>,
    ## #   Street <chr>, City <chr>, Province <chr>, Country <chr>, PostalCode <chr>,
    ## #   LocalArea <chr>, NumberofEmployees <chr>, FeePaid <dbl>,
    ## #   ExtractDate <dttm>, Geom <chr>

``` r
# save dataframe to csv
all_licences_group %>% write_csv("../data/processed/licences.csv")
```
