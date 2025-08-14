# NDVI Trend Analysis for Saltmarsh Sites (1990-2024)
# Updated to work with Google Earth Engine exports

# Load required libraries
if (!require("trend")) install.packages("trend")
if (!require("dplyr")) install.packages("dplyr")
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("tidyr")) install.packages("tidyr")

library(trend)
library(dplyr)
library(ggplot2)
library(tidyr)

# Load the data exported from Google Earth Engine
# Make sure these CSV files are in your working directory

# Load NDVI time series data
ndvi_raw <- read.csv("D:\\Saltmarsh Savers\\NDVI\\Data\\Saltmarsh_NDVI_TimeSeries_for_R_Analysis_1990_2024.csv")

# Load rainfall data
rainfall_raw <- read.csv("D:\\Saltmarsh Savers\\NDVI\\Data\\Wet_Tropics_Rainfall_for_R_Analysis_1990_2024.csv")

# Preview the data structure
cat("NDVI Data Structure:\n")
print(head(ndvi_raw))
cat("\nRainfall Data Structure:\n")
print(head(rainfall_raw))

# Reshape NDVI data to wide format (Year as rows, Sites as columns)
ndvi_wide <- ndvi_raw %>%
  select(Year, Site, NDVI) %>%
  pivot_wider(names_from = Site, values_from = NDVI) %>%
  arrange(Year)

# Clean up site names (replace spaces/special characters with underscores for R)
names(ndvi_wide)[-1] <- gsub("[^A-Za-z0-9]", "_", names(ndvi_wide)[-1])
names(ndvi_wide)[-1] <- gsub("_{2,}", "_", names(ndvi_wide)[-1])  # Remove multiple underscores
names(ndvi_wide)[-1] <- gsub("_$", "", names(ndvi_wide)[-1])     # Remove trailing underscores

cat("\nNDVI Data (Wide Format):\n")
print(head(ndvi_wide))

# Function to calculate trend statistics for each site
calculate_trends <- function(data) {
  sites <- names(data)[-1]  # Exclude 'Year' column
  results <- data.frame(
    Site = character(),
    Sens_Slope = numeric(),
    Sens_Slope_Pvalue = numeric(),
    MK_Tau = numeric(),
    MK_Pvalue = numeric(),
    MK_Trend = character(),
    Linear_Slope = numeric(),
    R_Squared = numeric(),
    Period = character(),
    stringsAsFactors = FALSE
  )
  
  for(site in sites) {
    # Remove NA values for analysis
    site_data <- data[[site]][!is.na(data[[site]])]
    years_data <- data$Year[!is.na(data[[site]])]
    
    if(length(site_data) < 10) {
      cat(sprintf("Warning: Site %s has less than 10 data points, skipping...\n", site))
      next
    }
    
    # Sen's Slope
    sens_result <- sens.slope(site_data)
    
    # Mann-Kendall Test
    mk_result <- mk.test(site_data)
    
    # Linear regression for comparison
    lm_result <- lm(site_data ~ years_data)
    lm_slope <- coef(lm_result)[2]
    r_squared <- summary(lm_result)$r.squared
    
    # Determine trend direction and significance
    trend_direction <- ifelse(mk_result$p.value < 0.05,
                             ifelse(mk_result$statistic > 0, "Increasing", "Decreasing"),
                             "No significant trend")
    
    # Add results to dataframe
    results <- rbind(results, data.frame(
      Site = gsub("_", " ", site),
      Sens_Slope = round(sens_result$estimates, 6),
      Sens_Slope_Pvalue = round(sens_result$p.value, 4),
      MK_Tau = round(mk_result$statistic, 4),
      MK_Pvalue = round(mk_result$p.value, 4),
      MK_Trend = trend_direction,
      Linear_Slope = round(lm_slope, 6),
      R_Squared = round(r_squared, 4),
      Period = "1990-2024"
    ))
  }
  
  return(results)
}

# Calculate NDVI trends
cat("\nCalculating NDVI trends...\n")
ndvi_trend_results <- calculate_trends(ndvi_wide)

# Calculate rainfall trend
cat("Calculating rainfall trends...\n")
rainfall_data <- rainfall_raw %>%
  select(Year, Annual_Rainfall_mm) %>%
  arrange(Year)

# Remove NA values
rainfall_clean <- rainfall_data$Annual_Rainfall_mm[!is.na(rainfall_data$Annual_Rainfall_mm)]
years_clean <- rainfall_data$Year[!is.na(rainfall_data$Annual_Rainfall_mm)]

if(length(rainfall_clean) >= 10) {
  # Sen's Slope for rainfall
  rainfall_sens <- sens.slope(rainfall_clean)
  rainfall_mk <- mk.test(rainfall_clean)
  rainfall_lm <- lm(rainfall_clean ~ years_clean)
  
  rainfall_trend_direction <- ifelse(rainfall_mk$p.value < 0.05,
                                   ifelse(rainfall_mk$statistic > 0, "Increasing", "Decreasing"),
                                   "No significant trend")
  
  rainfall_results <- data.frame(
    Variable = "Regional Rainfall",
    Sens_Slope = round(rainfall_sens$estimates, 3),
    Sens_Slope_Pvalue = round(rainfall_sens$p.value, 4),
    MK_Tau = round(rainfall_mk$statistic, 4),
    MK_Pvalue = round(rainfall_mk$p.value, 4),
    MK_Trend = rainfall_trend_direction,
    Linear_Slope = round(coef(rainfall_lm)[2], 3),
    R_Squared = round(summary(rainfall_lm)$r.squared, 4),
    Period = "1990-2024",
    Units = "mm/year"
  )
} else {
  cat("Warning: Insufficient rainfall data for trend analysis\n")
  rainfall_results <- NULL
}

# Sort NDVI results by Sen's slope (strongest to weakest increase)
ndvi_trend_results <- ndvi_trend_results[order(-ndvi_trend_results$Sens_Slope), ]

# Display results
cat(paste0("\n", strrep("=", 50), "\n"))
cat("NDVI TREND ANALYSIS RESULTS (1990-2024)\n")
cat(paste0(strrep("=", 50), "\n"))
print(ndvi_trend_results)

if(!is.null(rainfall_results)) {
  cat(paste0("\n", strrep("=", 50), "\n"))
  cat("RAINFALL TREND ANALYSIS RESULTS (1990-2024)\n")
  cat(paste0(strrep("=", 50), "\n"))
  print(rainfall_results)
}

# Create summary interpretation
cat("\n\nSUMMARY INTERPRETATION:\n")
cat("=======================\n")

significant_increasing <- ndvi_trend_results[ndvi_trend_results$MK_Trend == "Increasing", ]
if(nrow(significant_increasing) > 0) {
  cat("Sites with statistically significant INCREASING NDVI trends:\n")
  for(i in 1:nrow(significant_increasing)) {
    cat(sprintf("- %s: +%.6f NDVI/year (p = %.4f)\n", 
                significant_increasing$Site[i], 
                significant_increasing$Sens_Slope[i],
                significant_increasing$MK_Pvalue[i]))
  }
}

significant_decreasing <- ndvi_trend_results[ndvi_trend_results$MK_Trend == "Decreasing", ]
if(nrow(significant_decreasing) > 0) {
  cat("\nSites with statistically significant DECREASING NDVI trends:\n")
  for(i in 1:nrow(significant_decreasing)) {
    cat(sprintf("- %s: %.6f NDVI/year (p = %.4f)\n", 
                significant_decreasing$Site[i], 
                significant_decreasing$Sens_Slope[i],
                significant_decreasing$MK_Pvalue[i]))
  }
}

no_trend <- ndvi_trend_results[ndvi_trend_results$MK_Trend == "No significant trend", ]
if(nrow(no_trend) > 0) {
  cat("\nSites with NO significant NDVI trend:\n")
  for(i in 1:nrow(no_trend)) {
    cat(sprintf("- %s: %.6f NDVI/year (p = %.4f)\n", 
                no_trend$Site[i], 
                no_trend$Sens_Slope[i],
                no_trend$MK_Pvalue[i]))
  }
}

# Rainfall vs NDVI trend comparison
if(!is.null(rainfall_results)) {
  cat(sprintf("\nREGIONAL RAINFALL TREND: %s\n", rainfall_results$MK_Trend))
  cat(sprintf("- Rainfall change: %.3f mm/year (p = %.4f)\n", 
              rainfall_results$Sens_Slope, rainfall_results$MK_Pvalue))
  
  cat("\nINTERPRETATION:\n")
  if(nrow(significant_increasing) > 0) {
    if(rainfall_results$MK_Trend == "No significant trend" || rainfall_results$MK_Trend == "Decreasing") {
      cat("*** NDVI increases are occurring despite stable/decreasing rainfall ***\n")
      cat("*** This supports the mangrove encroachment hypothesis! ***\n")
    } else {
      cat("Both NDVI and rainfall are increasing - consider climate vs. ecological drivers\n")
    }
  }
}

# Create visualization
create_trend_plot <- function(ndvi_data, rainfall_data) {
  # NDVI plot
  plot_data <- ndvi_data %>%
    select(-contains("_$")) %>%
    pivot_longer(cols = -Year, names_to = "Site", values_to = "NDVI") %>%
    mutate(Site = gsub("_", " ", Site))
  
  p1 <- ggplot(plot_data, aes(x = Year, y = NDVI, color = Site)) +
    geom_line(size = 0.8) +
    geom_smooth(method = "lm", se = FALSE, linetype = "dashed", alpha = 0.7, size = 0.5) +
    theme_minimal() +
    labs(title = "NDVI Trends by Site (1990-2024)",
         subtitle = "Dashed lines show linear trends",
         x = "Year",
         y = "NDVI") +
    theme(legend.position = "bottom") +
    guides(color = guide_legend(ncol = 3))
  
  # Rainfall plot
  p2 <- ggplot(rainfall_data, aes(x = Year, y = Annual_Rainfall_mm)) +
    geom_line(color = "blue", size = 1) +
    geom_smooth(method = "lm", se = TRUE, color = "darkblue", fill = "lightblue", alpha = 0.3) +
    theme_minimal() +
    labs(title = "Regional Rainfall Trend (1990-2024)",
         subtitle = "Blue band shows 95% confidence interval",
         x = "Year",
         y = "Annual Rainfall (mm)")
  
  return(list(ndvi_plot = p1, rainfall_plot = p2))
}

# Create and display plots
if(exists("ndvi_wide") && exists("rainfall_data")) {
  plots <- create_trend_plot(ndvi_wide, rainfall_data)
  
  print(plots$ndvi_plot)
  print(plots$rainfall_plot)
}

# Export results to CSV
write.csv(ndvi_trend_results, "ndvi_sens_slope_results_1990_2024.csv", row.names = FALSE)
if(!is.null(rainfall_results)) {
  write.csv(rainfall_results, "rainfall_sens_slope_results_1990_2024.csv", row.names = FALSE)
}

cat("\n\nResults exported to CSV files:\n")
cat("- ndvi_sens_slope_results_1990_2024.csv\n")
if(!is.null(rainfall_results)) {
  cat("- rainfall_sens_slope_results_1990_2024.csv\n")
}

# Summary statistics
cat(paste0("\n", strrep("=", 50), "\n"))
cat("SUMMARY STATISTICS\n")
cat(paste0(strrep("=", 50), "\n"))
cat(sprintf("Analysis period: 1990-2024 (%d years)\n", max(ndvi_wide$Year) - min(ndvi_wide$Year) + 1))
cat(sprintf("Number of sites analyzed: %d\n", ncol(ndvi_wide) - 1))
cat(sprintf("Sites with increasing trends: %d\n", nrow(significant_increasing)))
cat(sprintf("Sites with decreasing trends: %d\n", nrow(significant_decreasing)))
cat(sprintf("Sites with no significant trend: %d\n", nrow(no_trend)))

if(!is.null(rainfall_results)) {
  cat(sprintf("Regional rainfall trend: %s\n", rainfall_results$MK_Trend))
}