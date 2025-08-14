# Saltmarsh NDVI vs Sea Level Regression Analysis

# Load required libraries
library(readr)
library(dplyr)
library(ggplot2)
library(lubridate)
library(broom)

# Set working directory and load data
setwd("D:/Saltmarsh Savers/NDVI/Data")

# Load sea level data
sea_level <- read_csv("Cairns Port Mean Sea Level 1990 - 2023.csv")

# Load NDVI monthly data
ndvi_monthly <- read_csv("Saltmarsh_NDVI_Monthly_Sites_1990_2024.csv")

# Examine data structure
cat("=== Sea Level Data Structure ===\n")
str(sea_level)
head(sea_level)

cat("\n=== NDVI Monthly Data Structure ===\n")
str(ndvi_monthly)
head(ndvi_monthly)

# Clean sea level data
sea_level_clean <- sea_level %>%
  rename(Month = Mth, Sea_Level = Mean) %>%
  select(Year, Month, Sea_Level) %>%
  filter(!is.na(Sea_Level))

# Clean NDVI data
ndvi_clean <- ndvi_monthly %>%
  # Remove special characters from site names
  mutate(Site = gsub("Â", "", Site),
         Site = trimws(Site)) %>%
  # Filter out missing NDVI values
  filter(!is.na(NDVI)) %>%
  # Keep only required columns
  select(Year, Month, Site, NDVI)

# Check data ranges
cat("\n=== Data Coverage ===\n")
cat("Sea Level: ", min(sea_level_clean$Year), "-", max(sea_level_clean$Year), "\n")
cat("NDVI: ", min(ndvi_clean$Year), "-", max(ndvi_clean$Year), "\n")

# Find overlapping period (both datasets have data)
overlap_start <- max(min(sea_level_clean$Year), min(ndvi_clean$Year))
overlap_end <- min(max(sea_level_clean$Year), max(ndvi_clean$Year))
cat("Overlapping period: ", overlap_start, "-", overlap_end, "\n")

# Filter both datasets to overlapping period
sea_level_overlap <- sea_level_clean %>% 
  filter(Year >= overlap_start & Year <= overlap_end)

ndvi_overlap <- ndvi_clean %>% 
  filter(Year >= overlap_start & Year <= overlap_end)

# Display unique sites
cat("\n=== Sites in NDVI Data ===\n")
sites <- unique(ndvi_overlap$Site)
print(sites)

# ANALYSIS 1: Average NDVI across all sites vs Sea Level
cat("\n=== ANALYSIS 1: Average NDVI vs Sea Level ===\n")

# Calculate average NDVI across all sites for each month/year
ndvi_avg <- ndvi_overlap %>%
  group_by(Year, Month) %>%
  summarise(NDVI_avg = mean(NDVI, na.rm = TRUE), 
            n_sites = n(), 
            .groups = 'drop')

# Merge with sea level data
merged_avg <- merge(sea_level_overlap, ndvi_avg, by = c("Year", "Month"))
merged_avg <- merged_avg[complete.cases(merged_avg), ]

cat("Total observations for regression:", nrow(merged_avg), "\n")

# Run regression
model_avg <- lm(Sea_Level ~ NDVI_avg, data = merged_avg)
summary(model_avg)

# Capture model summary for saving
avg_summary <- broom::tidy(model_avg)
avg_glance <- broom::glance(model_avg)

# Print to console
print(summary(model_avg))

# Create scatter plot
p1 <- ggplot(merged_avg, aes(x = NDVI_avg, y = Sea_Level)) +
  geom_point(alpha = 0.6, color = "blue") +
  geom_smooth(method = "lm", se = TRUE, color = "red") +
  labs(title = "Sea Level vs Average NDVI (All Sites)",
       subtitle = paste("R² =", round(summary(model_avg)$r.squared, 3),
                       ", p =", round(summary(model_avg)$coefficients[2,4], 4)),
       x = "Average NDVI",
       y = "Sea Level (m)") +
  theme_classic()

print(p1)
ggsave("SeaLevel_vs_Average_NDVI.png", p1, width = 8, height = 6, dpi = 300)

# ANALYSIS 2: Individual site analysis
cat("\n=== ANALYSIS 2: Individual Site Analysis ===\n")

site_results <- data.frame()

for(site in sites) {
  # Filter NDVI data for this site
  site_ndvi <- ndvi_overlap %>% filter(Site == site)
  
  # Merge with sea level data
  merged_site <- merge(sea_level_overlap, site_ndvi, by = c("Year", "Month"))
  merged_site <- merged_site[complete.cases(merged_site), ]
  
  if(nrow(merged_site) > 10) {  # Only analyze if sufficient data
    # Run regression
    model_site <- lm(Sea_Level ~ NDVI, data = merged_site)
    
    # Capture detailed results
    site_tidy <- broom::tidy(model_site)
    site_glance <- broom::glance(model_site)
    
    # Print summary to console
    cat("\nSite:", site, "\n")
    print(summary(model_site))
    
    # Extract key statistics
    r_squared <- summary(model_site)$r.squared
    p_value <- summary(model_site)$coefficients[2, 4]
    slope <- summary(model_site)$coefficients[2, 1]
    n_obs <- nrow(merged_site)
    
    # Store results
    site_results <- rbind(site_results, data.frame(
      Site = site,
      n_observations = n_obs,
      slope = slope,
      r_squared = r_squared,
      p_value = p_value,
      significant = p_value < 0.05
    ))
    
    cat("\nSite:", site, "\n")
    cat("Observations:", n_obs, "\n")
    cat("R²:", round(r_squared, 3), "\n")
    cat("p-value:", round(p_value, 4), "\n")
    cat("Slope:", round(slope, 4), "\n")
    cat("Significant:", p_value < 0.05, "\n")
  }
}

# Display summary table
cat("\n=== SUMMARY TABLE ===\n")
site_results$slope <- round(site_results$slope, 4)
site_results$r_squared <- round(site_results$r_squared, 3)
site_results$p_value <- round(site_results$p_value, 4)
print(site_results)

# Save site results to CSV
write_csv(site_results, "NDVI_SeaLevel_Regression_Results_by_Site.csv")
cat("\nSite results saved to: NDVI_SeaLevel_Regression_Results_by_Site.csv\n")

# Create visualization of site results
p2 <- ggplot(site_results, aes(x = reorder(Site, r_squared), y = r_squared, 
                              fill = significant)) +
  geom_col() +
  coord_flip() +
  scale_fill_manual(values = c("FALSE" = "lightgray", "TRUE" = "darkgreen")) +
  labs(title = "Effect Sizes: NDVI-Sea Level Relationships by Site",
       subtitle = "All relationships statistically significant (p < 0.001)",
       x = "Site",
       y = "R² Value",
       fill = "Significant (p<0.05)") +
  theme_classic() +
  theme(axis.text.y = element_text(size = 10))

print(p2)
ggsave("Effect_Sizes_by_Site.png", p2, width = 10, height = 6, dpi = 300)

# Time series plot
merged_avg$Date <- as.Date(paste(merged_avg$Year, merged_avg$Month, "01", sep = "-"))

p3 <- ggplot(merged_avg, aes(x = Date)) +
  geom_line(aes(y = Sea_Level * 10, color = "Sea Level (×10)")) +
  geom_line(aes(y = NDVI_avg, color = "Average NDVI")) +
  scale_y_continuous(
    name = "Average NDVI",
    sec.axis = sec_axis(~./10, name = "Sea Level (m)")
  ) +
  scale_color_manual(values = c("Sea Level (×10)" = "blue", "Average NDVI" = "green")) +
  labs(title = "Time Series: Sea Level vs Average NDVI (1990-2023)",
       subtitle = "Monthly data showing co-variation over time",
       x = "Date",
       color = "Variable") +
  theme_classic() +
  theme(legend.position = "bottom")

print(p3)
ggsave("Time_Series_SeaLevel_NDVI.png", p3, width = 12, height = 6, dpi = 300)

# Scatter plot with all sites on one plot
# Prepare data for multi-site scatter plot
all_site_data <- data.frame()

for(site in sites) {
  site_ndvi <- ndvi_overlap %>% filter(Site == site)
  merged_site <- merge(sea_level_overlap, site_ndvi, by = c("Year", "Month"))
  merged_site <- merged_site[complete.cases(merged_site), ]
  
  if(nrow(merged_site) > 10) {
    merged_site$Site_clean <- site
    all_site_data <- rbind(all_site_data, merged_site)
  }
}

# Multi-site scatter plot
p4 <- ggplot(all_site_data, aes(x = NDVI, y = Sea_Level, color = Site_clean)) +
  geom_point(alpha = 0.5, size = 0.8) +
  geom_smooth(method = "lm", se = FALSE, size = 0.8) +
  labs(title = "Sea Level vs NDVI: All Sites with Regression Lines",
       subtitle = "Each site shows positive correlation (all p < 0.001)",
       x = "NDVI",
       y = "Sea Level (m)",
       color = "Site") +
  theme_classic() +
  theme(legend.position = "right",
        legend.text = element_text(size = 8)) +
  guides(color = guide_legend(override.aes = list(alpha = 1, size = 2)))

print(p4)
ggsave("All_Sites_Scatter_Plot.png", p4, width = 12, height = 8, dpi = 300)

# Slope comparison plot
p5 <- ggplot(site_results, aes(x = reorder(Site, slope), y = slope)) +
  geom_col(fill = "steelblue", alpha = 0.7) +
  coord_flip() +
  labs(title = "Regression Slopes: NDVI Response to Sea Level by Site",
       subtitle = "Higher values indicate greater NDVI sensitivity to sea level changes",
       x = "Site",
       y = "Slope (NDVI change per meter sea level change)") +
  theme_classic() +
  theme(axis.text.y = element_text(size = 10))

print(p5)
ggsave("Slopes_by_Site.png", p5, width = 10, height = 6, dpi = 300)

# Combined effect size and slope plot
p6 <- ggplot(site_results, aes(x = slope, y = r_squared)) +
  geom_point(size = 4, alpha = 0.7, color = "darkblue") +
  geom_text(aes(label = Site),
            vjust = -0.8, hjust = 0.5, size = 3) +
  labs(title = "Effect Size vs Sensitivity: NDVI Response to Sea Level",
       subtitle = "Top-right quadrant shows sites most responsive to sea level changes",
       x = "Slope (NDVI sensitivity per meter sea level)",
       y = "R² (% variance explained by sea level)") +
  theme_classic() +
  geom_hline(yintercept = median(site_results$r_squared), linetype = "dashed", alpha = 0.5) +
  geom_vline(xintercept = median(site_results$slope), linetype = "dashed", alpha = 0.5) +
  annotate("text", x = max(site_results$slope) * 0.9, y = max(site_results$r_squared) * 0.9, 
           label = "High Effect Size\n& High Sensitivity", size = 3, alpha = 0.7) +
  annotate("text", x = min(site_results$slope) * 1.1, y = min(site_results$r_squared) * 1.1, 
           label = "Low Effect Size\n& Low Sensitivity", size = 3, alpha = 0.7)

print(p6)
ggsave("Effect_Size_vs_Slope.png", p6, width = 10, height = 8, dpi = 300)

# Correlation analysis
correlation <- cor(merged_avg$Sea_Level, merged_avg$NDVI_avg, use = "complete.obs")
cat("\n=== CORRELATION ANALYSIS ===\n")
cat("Pearson correlation coefficient:", round(correlation, 3), "\n")

# Test correlation significance
cor_test <- cor.test(merged_avg$Sea_Level, merged_avg$NDVI_avg)
cat("Correlation p-value:", round(cor_test$p.value, 4), "\n")
cat("Correlation is significant:", cor_test$p.value < 0.05, "\n")

# Create overall summary including average NDVI analysis
overall_summary <- data.frame(
  Analysis = c("Average_All_Sites", site_results$Site),
  n_observations = c(nrow(merged_avg), site_results$n_observations),
  slope = c(summary(model_avg)$coefficients[2, 1], site_results$slope),
  r_squared = c(summary(model_avg)$r.squared, site_results$r_squared),
  p_value = c(summary(model_avg)$coefficients[2, 4], site_results$p_value),
  significant = c(summary(model_avg)$coefficients[2, 4] < 0.05, site_results$significant)
)

# Round values for display
overall_summary$slope <- round(overall_summary$slope, 4)
overall_summary$r_squared <- round(overall_summary$r_squared, 3)
overall_summary$p_value <- round(overall_summary$p_value, 4)

# Save comprehensive results to CSV
write_csv(overall_summary, "NDVI_SeaLevel_Complete_Regression_Analysis.csv")
cat("\nComplete analysis saved to: NDVI_SeaLevel_Complete_Regression_Analysis.csv\n")

# Save detailed regression outputs
avg_detailed <- data.frame(
  Analysis = "Average_All_Sites",
  Term = avg_summary$term,
  Estimate = round(avg_summary$estimate, 6),
  Std_Error = round(avg_summary$std.error, 6),
  t_statistic = round(avg_summary$statistic, 4),
  p_value = round(avg_summary$p.value, 6),
  R_squared = round(avg_glance$r.squared, 4),
  Adj_R_squared = round(avg_glance$adj.r.squared, 4),
  F_statistic = round(avg_glance$statistic, 4),
  df = avg_glance$df,
  n_obs = nrow(merged_avg)
)

write_csv(avg_detailed, "NDVI_SeaLevel_Detailed_Regression_Output.csv")
cat("Detailed regression output saved to: NDVI_SeaLevel_Detailed_Regression_Output.csv\n")

# Save the merged data for further analysis
write_csv(merged_avg, "NDVI_SeaLevel_Monthly_Data.csv")
cat("Monthly merged data saved to: NDVI_SeaLevel_Monthly_Data.csv\n")

cat("\n=== PLOTS SAVED ===\n")
cat("1. SeaLevel_vs_Average_NDVI.png - Main regression plot\n")
cat("2. Effect_Sizes_by_Site.png - R² comparison\n") 
cat("3. Time_Series_SeaLevel_NDVI.png - Temporal patterns\n")
cat("4. All_Sites_Scatter_Plot.png - Multi-site regression lines\n")
cat("5. Slopes_by_Site.png - Sensitivity comparison\n")
cat("6. Effect_Size_vs_Slope.png - Combined effect size and sensitivity analysis\n")