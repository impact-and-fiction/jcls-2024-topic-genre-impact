# -------------------------------------------------------- #
#
# This script takes as input `prevalence_keyness.csv`
# and provides as output a series of scatter plots showing
# the results of the keyness analysis for one genre vs
# the other genres.
# 
# -------------------------------------------------------- #

#### load libraries ####
library(tidyverse)
library(ggrepel)

#### load `prevalence_keyness` ####
read_csv("prevalence_keyness.csv", na = 'nan') -> df
head(df)
df <- na.omit(df)

df$impact_term <- as.factor(df$impact_term)
df$nur_genre <- as.factor(df$nur_genre)
df_minimal <- df

head(df_minimal)

#### Function to plot keyness as a scatterplot ####
plot_genre_vs_others <- function(df_keyness, label, top_n = 50, colour_by_impact = FALSE) {
  
  # Separate the label and other genres
  df_genre1 <- droplevels(df_keyness[df_keyness$nur_genre == label, ])
  df_other_genres <- droplevels(df_keyness[df_keyness$nur_genre != label, ])
  
  # Group by 'impact_term' and calculate average
  df_other_genres <- df_other_genres |> 
    group_by(impact_term) |> 
    summarise_if(is.numeric, mean, na.rm = TRUE) |> 
    mutate(nur_genre = 'Other genres')
  
  # Merge dataframes
  merged <- left_join(df_genre1, df_other_genres,
                      by = "impact_term",
                      keep=TRUE,
                      suffix = c("_genre1", "_other")
  )
  
  #merged[is.na(merged)] <- 0
  # Compute keyness of other genres
  merged$Keyness_other <- log((merged$NF_W_other) / merged$NF_WC_other)
  
  # Compute difference between that genre and others
  merged$Keyness_diff <- abs(merged$Keyness_genre1 - merged$Keyness_other)
  
  # Take only the top_n largests impact terms
  merged_topn <- merged |> top_n(top_n, Keyness_diff)
  
  # Colour by strong/weak association for that genre vs others
  colors <- ifelse(merged_topn$Keyness_genre1 > merged_topn$Keyness_other, "blue", "gray")
  if(colour_by_impact) {
    colors <- wesanderson::wes_palette("Darjeeling1")
    colors[3] <- 'blue'
    names(colors) <- levels(merged_topn$prevalent_impact)
    
  }
  colScale <- scale_colour_manual(name = "grp", values = colors)
  
  merged_topn$prevalent_impact <- as.factor(merged_topn$prevalent_impact)
  
  # Plot
  color_selected <- colors
  if(colour_by_impact) {
    color_selected <- prevalent_impact
  }
  p <- ggplot(merged_topn, aes(x = Keyness_genre1, y = Keyness_other, color = color_selected)) +
    geom_point(aes(col = color_selected), alpha = 0.6) +
    geom_text_repel(aes(label = impact_term_genre1,
                        segment.square  = FALSE,
                        segment.inflect = TRUE
    ), 
    size = 3,
    segment.curvature = -0.1,
    segment.ncp = 3,
    nudge_x = .15,
    segment.angle = 20,
    max.overlaps = 10) +
    geom_abline(intercept = 0, slope = 1, color = "black") +
    labs(x = paste("Keyness in", gsub("_", " ", label)),
         y = 'Keyness in Other genres',
         title = paste('Term in', gsub("_", " ", label), 'vs Other genres'),
         color = "") +
    theme_bw() +
    theme(legend.title = element_blank(),
          legend.position = "top")
  
  p <- p + scale_color_identity()
  if(colour_by_impact){
    p <- p + colScale
  }
  return(p)
}


#### save plots in a for loop ####
all_genres <- unique(df_minimal$nur_genre)

for (label in all_genres) {
  plot_genre_vs_others(df_keyness = df_minimal, 
                       label = label, 
                       top_n = length(unique(df_minimal$impact_term)))
  ggsave(paste0("prevalence_term_association_", label, ".png"), dpi = 300, width = 7.6, height = 7.47)
  
}