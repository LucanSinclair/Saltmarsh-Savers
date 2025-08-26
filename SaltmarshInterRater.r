# Install and load necessary packages
install.packages("irr")
install.packages("readxl")  # For reading Excel files

library(irr)
library(readxl)

# Function to compute Kendall's W for a single sheet (site)
compute_kendall_w <- function(sheet_name, excel_file) {
  # Read the data from the specified sheet in the Excel file
  ratings <- read_excel(excel_file, sheet = sheet_name)
  
  # Remove the first column if it contains the observation names
  ratings <- ratings[,-1]
  
  # Compute Kendall's W (Kendall's Coefficient of Concordance)
  kendall_result <- kendall(ratings, correct = TRUE)
  
  # Return the result
  return(kendall_result)
}

# Function to automate over multiple sheets (sites)
run_analysis <- function(excel_file) {
  # Read the sheet names from the Excel file
  sheet_names <- excel_sheets(excel_file)
  
  # List to store results
  results <- list()
  
  # Loop through each sheet and compute Kendall's W
  for (sheet_name in sheet_names) {
    print(paste("Processing", sheet_name))
    
    # Compute Kendall's W for the current sheet (site)
    kendall_result <- compute_kendall_w(sheet_name, excel_file)
    
    # Store the results in the list
    results[[sheet_name]] <- kendall_result
  }
  
  return(results)
}

# Define the path to your Excel file
excel_file <- "E:\\Saltmarsh Savers\\2024_SaltmarshSavers_DataForStatsNEW.xlsx"  # Path to file

# Run the analysis for all sheets (sites) in the Excel file
analysis_results <- run_analysis(excel_file)

# Print the results for each site
print(analysis_results)
