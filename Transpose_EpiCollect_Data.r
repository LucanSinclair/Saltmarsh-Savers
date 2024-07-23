# Program to transpose EpiCollect data and save it as a new CSV file
# Code will remove columns with "Take_a_photo" and "Comments" in the header and the columns listed in columns_to_remove
# Code will also extract the leading number from each cell if it's not a date or lat-long
# LS 2024-07-23

# Load the required library
library(data.table)

# Read the CSV file
data <- fread("C:\\Users\\LucanSinclair\\OneDrive - Earthwatch\\Desktop\\Saltmarsh Savers\\form-1__super-saltmarsh-savers.csv")

# Define a vector of column names to remove
columns_to_remove <- c("ec5_uuid", "created_at", "uploaded_at", "title", 
                       "accuracy_5_Location", "UTM_Northing_5_Location", 
                       "UTM_Easting_5_Location", "UTM_Zone_5_Location")

# Remove columns with "Take_a_photo" in the header and the columns listed in columns_to_remove
data <- data[, !grepl("Take_a_photo", names(data)) & !(names(data) %in% columns_to_remove), with = FALSE]

# Remove columns with "Comments" in the header and the columns listed in columns_to_remove
data <- data[, !grepl("Comments", names(data)) & !(names(data) %in% columns_to_remove), with = FALSE]

# Transpose the remaining data
transposed_data <- t(data)

# Convert the transposed matrix back to a data frame
transposed_data_df <- as.data.frame(transposed_data, stringsAsFactors = FALSE)

# Function to check if a string is a date or lat-long
is_date_or_latlong <- function(x) {
  # Regular expression for date (simple check for formats like YYYY-MM-DD, DD/MM/YYYY, etc.)
  date_pattern <- "^([0-9]{4}-[0-9]{2}-[0-9]{2})$|^([0-9]{2}/[0-9]{2}/[0-9]{4})$"
  # Regular expression for latitude and longitude (simple check for formats like degrees, minutes, seconds)
  latlong_pattern <- latlong_pattern <- "^-?[0-9]+\\.?[0-9]+$"
  grepl(date_pattern, x) | grepl(latlong_pattern, x)
}

# Function to extract the leading number from a string if it's not a date or lat-long
extract_leading_number <- function(x) {
  ifelse(is_date_or_latlong(x), x, gsub("^([0-9]+).*", "\\1", x))
}

# Apply the function to each element of the data frame
transposed_data_df[] <- lapply(transposed_data_df, function(x) sapply(x, extract_leading_number))

# Define the new row names
new_row_names <- c("Site name", "Date", "Name of Surveyor", "Lat", "Long", "NRM Region", 
                   "Saltmarsh Knowledge", "Local Knowledge", "Fish Habitat Accessibility", 
                   "Fish Habitat Proximity", "Crabs/Snail", "Salt Couch", "Fish Habitat Diversity", 
                   "Vegetation Type", "Sediment Type", "Vegetation Cover", "Vegetation Density", 
                   "Algal Mat Cover", "Direct Runoff", "Proximity to Point Source", "Indirect Runoff", 
                   "Tidal Connectivity", "Migratory Wader Birds", "Threatened Species", 
                   "Locally Iconic Species", "General Habitat Value", "Access", "Visual Appeal", 
                   "Buffer Zone value", "Cultural Values", "Vehicles", "Cattle", "Pigs", "Mowing", 
                   "Burning", "Trampling", "Surface Erosion & Scouring", "Sediment Burial", 
                   "Shoreline Erosion", "Dumping/Rubbish", "Infilling/Landfill", "Agricultural Runoff", 
                   "Urban Runoff", "Chemical Spray Drift", "Chemical Pollution", "Altered Hydrology (Tidal)", 
                   "Altered Hydrology (Fresh)", "Buffer Zone condition", "Coastal Squeeze", 
                   "Terrestrial Retreat", "Mangrove Encroachment", "Weeds", "Drought/Water Stress", 
                   "Value this because..", "Notable Features", "Threatened By..", "Could be mmproved by..")

# Set the row names of the transposed data frame to the original column names
rownames(transposed_data_df) <- new_row_names

# Include the original column names (now row names) as a separate column in the CSV:
transposed_data_df <- cbind(Original_Column_Names = rownames(transposed_data_df), transposed_data_df)

# Save the transposed data as a new file
new_file_name <- "C:\\Users\\LucanSinclair\\OneDrive - Earthwatch\\Desktop\\Saltmarsh Savers\\form-1__super-saltmarsh-savers_transposed.csv"
write.csv(transposed_data_df, file = new_file_name, row.names = FALSE)