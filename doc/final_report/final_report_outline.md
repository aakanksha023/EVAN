Final Report Outline
================
2020-06-03

## Executive Summary

A brief and high level summary of the project proposal.

## Introduction

>   - Start broad, introducing the question being asked/problem needing
>     solving and why it is important.
>   - Indicate the refined tangible objectives  
>   - Reasoning for why these scientific objectives are useful for
>     addressing the capstone partner’s needs.
>   - Might need to describe the available data first before outlining
>     the objectives.

  - present general census demographic data

## Data Science Methods

>   - Describe the data science techniques you used to address the
>     objectives.
>   - Pros and cons of using this method
>   - Justification over other methods
>   - Possible improvements
>   - Difficulties associated with making these improvements, and why
>     you didn’t implement the improvements.

  - improvements include:
      - getting additional data sets which may be relevant to business
        renewal
          - difficulties: there is a vast amount data, could result in
            over fitting and make the model herder to interpret
      - could get the census data at more precise level (i.e. postal
        code)
          - difficulties: this would require additional data wrangling
            steps for which we did not have the time
      - additional feature engineering could be done
      - use various methods to determine feature selection: RFE, l1,
        Tree-based feature selection
      - imputing missing values: perform linear regression across the 4
        census years to get better estimates of the values for the
        missing years

## Data Product and Results

>   - Describe your data product and results  
>   - For the description of the data product, you might want to
>     include:
>   - How you intend the partner to use the data product
>   - Pros and cons of using this product/interface
>   - Justification over other products/interfaces
>   - Possible improvements
>   - Difficulties associated with making these improvements, and why
>     you didn’t implement the improvements.

  - map displaying business turnover
      - (time-slider, surviving businesses in blue, businesses failing
        to renew in red)
  - map displaying businesses grouped by industry
      - over time
      - each industry is a different colour
      - user could select industry of interest and rest of the
        businesses/dots not in that industry would appear grey
      - allows the user to see where these industries are concentrated
        and how this changes over time
  - What are the factors affecting the license renewal?
      - feature importance
      - Factor importance and interpretability is critical for public
        policy
  - Think about things at aggregate levels (business sectors e.g.)
      - model likelihood of specific industries renewing their licence
        in each of the neighbourhoods
  - Given the set of factors being input into the model, can we look at
    how we might simulate COVID across the business patterns?
      - tweak the model later to add variables that might best reflect
        the reality of COVID.

## Conclusions and Recommendations

>   - Restate the question being asked/problem needing solving
>   - explain how your data product answers it
>   - Comment on how well your product answered the question/solved the
>     problem
>   - Discuss limitations of the product
>   - Describe future improvements and recommendations