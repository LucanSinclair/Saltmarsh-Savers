# NDVI Trend Analysis for Saltmarsh Sites
# Load required libraries
install.packages(c("trend", "dplyr", "ggplot2"))
library(trend)
library(dplyr)
library(ggplot2)

# Create the dataset
ndvi_data <- data.frame(
  Year = 2005:2024,
  Airport_Boardwalk = c(0.148, 0.147, 0.142, 0.142, 0.156, 0.129, 0.169, 0.190, 0.181, 0.196, 0.175, 0.197, 0.177, 0.203, 0.223, 0.211, 0.214, 0.218, 0.240, 0.234),
  Federal_Police = c(0.137, 0.132, 0.135, 0.131, 0.142, 0.141, 0.158, 0.147, 0.155, 0.173, 0.139, 0.168, 0.173, 0.156, 0.177, 0.161, 0.173, 0.169, 0.194, 0.196),
  Yorkeys_Knob = c(0.147, 0.166, 0.160, 0.158, 0.168, 0.182, 0.185, 0.176, 0.174, 0.195, 0.177, 0.187, 0.191, 0.187, 0.199, 0.192, 0.197, 0.200, 0.224, 0.225),
  Machans_Site_B = c(0.205, 0.219, 0.194, 0.177, 0.208, 0.206, 0.204, 0.220, 0.217, 0.219, 0.219, 0.242, 0.238, 0.218, 0.244, 0.245, 0.255, 0.253, 0.289, 0.202),
  Machans_Site_A = c(0.212, 0.231, 0.221, 0.180, 0.233, 0.256, 0.207, 0.241, 0.233, 0.239, 0.258, 0.268, 0.261, 0.228, 0.273, 0.263, 0.263, 0.273, 0.295, 0.219),
  Trinity_Site_A = c(0.146, 0.159, 0.155, 0.152, 0.162, 0.125, 0.162, 0.172, 0.167, 0.161, 0.163, 0.184, 0.182, 0.180, 0.183, 0.172, 0.186, 0.189, 0.197, 0.200),
  Trinity_Site_B = c(0.143, 0.155, 0.152, 0.152, 0.154, 0.106, 0.163, 0.160, 0.177, 0.176, 0.151, 0.185, 0.173, 0.185, 0.182, 0.168, 0.179, 0.173, 0.187, 0.188),
  Thomats_Site_A = c(0.138, 0.219, 0.124, 0.138, 0.212, 0.238, 0.206, 0.200, 0.205, 0.184, 0.226, 0.278, 0.224, 0.189, 0.230, 0.233, 0.253, 0.241, 0.257, 0.244),
  Thomats_Site_B = c(0.137, 0.239, 0.131, 0.138, 0.194, 0.193, 0.201, 0.187, 0.224, 0.189, 0.230, 0.278, 0.238, 0.192, 0.242, 0.253, 0.269, 0.250, 0.286, 0.266)
)

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
    stringsAsFactors = FALSE
  )
  
  for(site in sites) {
    # Sen's Slope
    sens_result <- sens.slope(data[[site]])
    
    # Mann-Kendall Test
    mk_result <- mk.test(data[[site]])
    
    # Linear regression for comparison
    lm_result <- lm(data[[site]] ~ data$Year)
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
      R_Squared = round(r_squared, 4)
    ))
  }
  
  return(results)
}

# Calculate trends
trend_results <- calculate_trends(ndvi_data)

# Sort by Sen's slope (strongest to weakest increase)
trend_results <- trend_results[order(-trend_results$Sens_Slope), ]

# Display results
print("NDVI Trend Analysis Results:")
print("============================")
print(trend_results)

# Create summary interpretation
cat("\n\nSUMMARY INTERPRETATION:\n")
cat("=======================\n")

significant_increasing <- trend_results[trend_results$MK_Trend == "Increasing", ]
if(nrow(significant_increasing) > 0) {
  cat("Sites with statistically significant INCREASING trends:\n")
  for(i in 1:nrow(significant_increasing)) {
    cat(sprintf("- %s: +%.6f NDVI/year (p = %.4f)\n", 
                significant_increasing$Site[i], 
                significant_increasing$Sens_Slope[i],
                significant_increasing$MK_Pvalue[i]))
  }
}

significant_decreasing <- trend_results[trend_results$MK_Trend == "Decreasing", ]
if(nrow(significant_decreasing) > 0) {
  cat("\nSites with statistically significant DECREASING trends:\n")
  for(i in 1:nrow(significant_decreasing)) {
    cat(sprintf("- %s: %.6f NDVI/year (p = %.4f)\n", 
                significant_decreasing$Site[i], 
                significant_decreasing$Sens_Slope[i],
                significant_decreasing$MK_Pvalue[i]))
  }
}

no_trend <- trend_results[trend_results$MK_Trend == "No significant trend", ]
if(nrow(no_trend) > 0) {
  cat("\nSites with NO significant trend:\n")
  for(i in 1:nrow(no_trend)) {
    cat(sprintf("- %s: %.6f NDVI/year (p = %.4f)\n", 
                no_trend$Site[i], 
                no_trend$Sens_Slope[i],
                no_trend$MK_Pvalue[i]))
  }
}

# Optional: Create visualization
create_trend_plot <- function(data, results) {
  # Reshape data for plotting
  library(tidyr)
  plot_data <- data %>%
    pivot_longer(cols = -Year, names_to = "Site", values_to = "NDVI") %>%
    mutate(Site = gsub("_", " ", Site))
  
  # Create plot
  p <- ggplot(plot_data, aes(x = Year, y = NDVI, color = Site)) +
    geom_line(size = 1) +
    geom_smooth(method = "lm", se = FALSE, linetype = "dashed", alpha = 0.7) +
    theme_minimal() +
    labs(title = "NDVI Trends by Site (2005-2024)",
         subtitle = "Dashed lines show linear trends",
         x = "Year",
         y = "NDVI") +
    theme(legend.position = "bottom") +
    guides(color = guide_legend(ncol = 3))
  
  return(p)
}

# Create and display plot
trend_plot <- create_trend_plot(ndvi_data, trend_results)
print(trend_plot)

# Export results to CSV
write.csv(trend_results, "ndvi_trend_analysis_results.csv", row.names = FALSE)
cat("\n\nResults exported to 'ndvi_trend_analysis_results.csv'\n")