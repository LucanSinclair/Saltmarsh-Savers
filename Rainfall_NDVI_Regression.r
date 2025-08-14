# Saltmarsh NDVI vs Rainfall Regression Analysis

# Load required libraries
library(readr)
library(dplyr)
library(ggplot2)
library(lubridate)
library(broom)

# Set working directory and load data
setwd("D:/Saltmarsh Savers/NDVI/Data")

# Load rainfall data
rainfall_monthly <- read_csv("Wet_Tropics_Monthly_Rainfall_1990_2024.csv")

# Load NDVI monthly data
ndvi_monthly <- read_csv("Saltmarsh_NDVI_Monthly_Sites_1990_2024.csv")

# Examine data structure
cat("=== Rainfall Data Structure ===\n")
str(rainfall_monthly)
head(rainfall_monthly)

cat("\n=== NDVI Monthly Data Structure ===\n")
str(ndvi_monthly)
head(ndvi_monthly)

# Clean rainfall data
rainfall_clean <- rainfall_monthly %>%
  rename(Rainfall = Monthly_Rainfall_mm) %>%
  select(Year, Month, Rainfall) %>%
  filter(!is.na(Rainfall))

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
cat("Rainfall: ", min(rainfall_clean$Year), "-", max(rainfall_clean$Year), "\n")
cat("NDVI: ", min(ndvi_clean$Year), "-", max(ndvi_clean$Year), "\n")

# Find overlapping period (both datasets have data)
overlap_start <- max(min(rainfall_clean$Year), min(ndvi_clean$Year))
overlap_end <- min(max(rainfall_clean$Year), max(ndvi_clean$Year))
cat("Overlapping period: ", overlap_start, "-", overlap_end, "\n")

# Filter both datasets to overlapping period
rainfall_overlap <- rainfall_clean %>% 
  filter(Year >= overlap_start & Year <= overlap_end)

ndvi_overlap <- ndvi_clean %>% 
  filter(Year >= overlap_start & Year <= overlap_end)

# Display unique sites
cat("\n=== Sites in NDVI Data ===\n")
sites <- unique(ndvi_overlap$Site)
print(sites)

# ANALYSIS 1: Average NDVI across all sites vs Rainfall
cat("\n=== ANALYSIS 1: Average NDVI vs Rainfall ===\n")

# Calculate average NDVI across all sites for each month/year
ndvi_avg <- ndvi_overlap %>%
  group_by(Year, Month) %>%
  summarise(NDVI_avg = mean(NDVI, na.rm = TRUE), 
            n_sites = n(), 
            .groups = 'drop')

# Merge with rainfall data
merged_avg <- merge(rainfall_overlap, ndvi_avg, by = c("Year", "Month"))
merged_avg <- merged_avg[complete.cases(merged_avg), ]

cat("Total observations for regression:", nrow(merged_avg), "\n")

# Run regression
model_avg <- lm(NDVI_avg ~ Rainfall, data = merged_avg)
summary(model_avg)

# Capture model summary for saving
avg_summary <- broom::tidy(model_avg)
avg_glance <- broom::glance(model_avg)

# Print to console
print(summary(model_avg))

# Create scatter plot
p1 <- ggplot(merged_avg, aes(x = Rainfall, y = NDVI_avg)) +
  geom_point(alpha = 0.6, color = "blue") +
  geom_smooth(method = "lm", se = TRUE, color = "red") +
  labs(title = "Average NDVI vs Monthly Rainfall (All Sites)",
       subtitle = paste("R² =", round(summary(model_avg)$r.squared, 3),
                       ", p =", round(summary(model_avg)$coefficients[2,4], 4)),
       x = "Monthly Rainfall (mm)",
       y = "Average NDVI") +
  theme_classic()

print(p1)
ggsave("Rainfall_vs_Average_NDVI.png", p1, width = 8, height = 6, dpi = 300)

# ANALYSIS 2: Individual site analysis
cat("\n=== ANALYSIS 2: Individual Site Analysis ===\n")

site_results <- data.frame()

for(site in sites) {
  # Filter NDVI data for this site
  site_ndvi <- ndvi_overlap %>% filter(Site == site)
  
  # Merge with rainfall data
  merged_site <- merge(rainfall_overlap, site_ndvi, by = c("Year", "Month"))
  merged_site <- merged_site[complete.cases(merged_site), ]
  
  if(nrow(merged_site) > 10) {  # Only analyze if sufficient data
    # Run regression
    model_site <- lm(NDVI ~ Rainfall, data = merged_site)
    
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
write_csv(site_results, "NDVI_Rainfall_Regression_Results_by_Site.csv")
cat("\nSite results saved to: NDVI_Rainfall_Regression_Results_by_Site.csv\n")

# Create visualization of site results
p2 <- ggplot(site_results, aes(x = reorder(Site, r_squared), y = r_squared, 
                              fill = significant)) +
  geom_col() +
  coord_flip() +
  scale_fill_manual(values = c("FALSE" = "lightgray", "TRUE" = "darkgreen")) +
  labs(title = "Effect Sizes: NDVI-Rainfall Relationships by Site",
       subtitle = "R² values show variance explained by monthly rainfall",
       x = "Site",
       y = "R² Value",
       fill = "Significant (p<0.05)") +
  theme_classic() +
  theme(axis.text.y = element_text(size = 10))

print(p2)
ggsave("Rainfall_Effect_Sizes_by_Site.png", p2, width = 10, height = 6, dpi = 300)

# Time series plot
merged_avg$Date <- as.Date(paste(merged_avg$Year, merged_avg$Month, "01", sep = "-"))

p3 <- ggplot(merged_avg, aes(x = Date)) +
  geom_line(aes(y = Rainfall / 1000, color = "Rainfall (÷1000)")) +
  geom_line(aes(y = NDVI_avg, color = "Average NDVI")) +
  scale_y_continuous(
    name = "Average NDVI",
    sec.axis = sec_axis(~.*1000, name = "Monthly Rainfall (mm)")
  ) +
  scale_color_manual(values = c("Rainfall (÷1000)" = "blue", "Average NDVI" = "green")) +
  labs(title = "Time Series: Rainfall vs Average NDVI (1990-2024)",
       subtitle = "Monthly data showing seasonal patterns",
       x = "Date",
       color = "Variable") +
  theme_classic() +
  theme(legend.position = "bottom")

print(p3)
ggsave("Time_Series_Rainfall_NDVI.png", p3, width = 12, height = 6, dpi = 300)

# Scatter plot with all sites on one plot
all_site_data <- data.frame()

for(site in sites) {
  site_ndvi <- ndvi_overlap %>% filter(Site == site)
  merged_site <- merge(rainfall_overlap, site_ndvi, by = c("Year", "Month"))
  merged_site <- merged_site[complete.cases(merged_site), ]
  
  if(nrow(merged_site) > 10) {
    merged_site$Site_clean <- site
    all_site_data <- rbind(all_site_data, merged_site)
  }
}

# Multi-site scatter plot
p4 <- ggplot(all_site_data, aes(x = Rainfall, y = NDVI, color = Site_clean)) +
  geom_point(alpha = 0.5, size = 0.8) +
  geom_smooth(method = "lm", se = FALSE, size = 0.8) +
  labs(title = "NDVI vs Rainfall: All Sites with Regression Lines",
       subtitle = "Individual site responses to monthly rainfall variation",
       x = "Monthly Rainfall (mm)",
       y = "NDVI",
       color = "Site") +
  theme_classic() +
  theme(legend.position = "right",
        legend.text = element_text(size = 8)) +
  guides(color = guide_legend(override.aes = list(alpha = 1, size = 2)))

print(p4)
ggsave("All_Sites_Rainfall_Scatter_Plot.png", p4, width = 12, height = 8, dpi = 300)

# Slope comparison plot
p5 <- ggplot(site_results, aes(x = reorder(Site, slope), y = slope)) +
  geom_col(fill = "steelblue", alpha = 0.7) +
  coord_flip() +
  labs(title = "Regression Slopes: NDVI Response to Rainfall by Site",
       subtitle = "Higher values indicate greater NDVI sensitivity to rainfall changes",
       x = "Site",
       y = "Slope (NDVI change per mm rainfall)") +
  theme_classic() +
  theme(axis.text.y = element_text(size = 10))

print(p5)
ggsave("Rainfall_Slopes_by_Site.png", p5, width = 10, height = 6, dpi = 300)

# Combined effect size and slope plot
p6 <- ggplot(site_results, aes(x = slope, y = r_squared)) +
  geom_point(size = 4, alpha = 0.7, color = "darkblue") +
  geom_text(aes(label = Site),
            vjust = -0.8, hjust = 0.5, size = 3) +
  labs(title = "Effect Size vs Sensitivity: NDVI Response to Rainfall",
       subtitle = "Top-right quadrant shows sites most responsive to rainfall changes",
       x = "Slope (NDVI sensitivity per mm rainfall)",
       y = "R² (% variance explained by rainfall)") +
  theme_classic() +
  geom_hline(yintercept = median(site_results$r_squared), linetype = "dashed", alpha = 0.5) +
  geom_vline(xintercept = median(site_results$slope), linetype = "dashed", alpha = 0.5) +
  annotate("text", x = max(site_results$slope) * 0.9, y = max(site_results$r_squared) * 0.9, 
           label = "High Effect Size\n& High Sensitivity", size = 3, alpha = 0.7) +
  annotate("text", x = min(site_results$slope) * 1.1, y = min(site_results$r_squared) * 1.1, 
           label = "Low Effect Size\n& Low Sensitivity", size = 3, alpha = 0.7)

print(p6)
ggsave("Rainfall_Effect_Size_vs_Slope.png", p6, width = 10, height = 8, dpi = 300)

# Correlation analysis
correlation <- cor(merged_avg$Rainfall, merged_avg$NDVI_avg, use = "complete.obs")
cat("\n=== CORRELATION ANALYSIS ===\n")
cat("Pearson correlation coefficient:", round(correlation, 3), "\n")

# Test correlation significance
cor_test <- cor.test(merged_avg$Rainfall, merged_avg$NDVI_avg)
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
overall_summary$slope <- round(overall_summary$slope, 6)
overall_summary$r_squared <- round(overall_summary$r_squared, 3)
overall_summary$p_value <- round(overall_summary$p_value, 4)

# Save comprehensive results to CSV
write_csv(overall_summary, "NDVI_Rainfall_Complete_Regression_Analysis.csv")
cat("\nComplete analysis saved to: NDVI_Rainfall_Complete_Regression_Analysis.csv\n")

# Save the merged data for further analysis
write_csv(merged_avg, "NDVI_Rainfall_Monthly_Data.csv")
cat("Monthly merged data saved to: NDVI_Rainfall_Monthly_Data.csv\n")

cat("\n=== PLOTS SAVED ===\n")
cat("1. Rainfall_vs_Average_NDVI.png - Main regression plot\n")
cat("2. Rainfall_Effect_Sizes_by_Site.png - R² comparison\n") 
cat("3. Time_Series_Rainfall_NDVI.png - Temporal patterns\n")
cat("4. All_Sites_Rainfall_Scatter_Plot.png - Multi-site regression lines\n")
cat("5. Rainfall_Slopes_by_Site.png - Sensitivity comparison\n")
cat("6. Rainfall_Effect_Size_vs_Slope.png - Combined effect size and sensitivity analysis\n")