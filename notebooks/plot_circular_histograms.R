# -------------------------------------------------------------- #
#
# This script takes as input `circular_histograms_data.csv` and
# it produces as output a series of circular histograms used
# to represent the proportion of topics within a book
#
# -------------------------------------------------------------- #

#### load libraries ####
library(tidyverse)
library(fmsb)

#### load data ####
read.csv('circular_histograms_data.csv', stringsAsFactors = F, na.strings = '') -> temp
temp$isbn <- as.factor(temp$isbn)
temp$topic_number <- as.factor(temp$topic_number)

temp <- dplyr::mutate_all(temp, ~tidyr::replace_na(., 'unclassified'))
temp$nur_genre <- as.factor(temp$nur_genre)
temp$category <- as.factor(temp$category)
summary(temp)

head(temp)

genres <- unique(temp$nur_genre)

#### pre-process data for making it usable by the plot ####

# there are some topics that overlap in themes, for instance,
# in book isbn 9789402522297, topic 10 is classified in the theme "Romance/sex" AND also in "Culture"
# that is not because topic 10 has two proportions in the book, but only because topic 10 is represented in 2 themes
# so I make the proportions match by dividing the proportion by the number of themes in which a topic appear
# e.g., if topic 10 has 50% proportion of appearance in a book, but topic 10 has 2 categories, then each category takes 25% proportion.
# hope this makes sense!

adjusted_df <- temp |>
  group_by(isbn, nur_genre, topic_number) |>
  mutate(count = n()) |>
  ungroup() |>
  mutate(adjusted_prop = topic_proportion / count) |>
  group_by(isbn, nur_genre) |>
  mutate(total = sum(adjusted_prop))


labels <- adjusted_df |>
  group_by(nur_genre)|>
  summarise(book_count = n_distinct(isbn)) |>
  mutate(combined_column = paste0(nur_genre, ": ", book_count, " books"))

# to make the circular plots, we need a matrix.
# lines below make the dataframe "squared" into a matrix
prop_df_genre <- tibble()
for (genre in genres) {
  
  prop_df_genre <- bind_rows(prop_df_genre,
                             adjusted_df |>
                               filter(nur_genre == genre) |>
                               group_by(category) |>
                               summarise(total_adjusted_prop = sum(adjusted_prop))|>
                               mutate(proportion = total_adjusted_prop / sum(total_adjusted_prop)) |>
                               select(-total_adjusted_prop)|>
                               pivot_wider(names_from = category, values_from = proportion)|>
                               mutate(genre = genre)
  )
}

# replace na with 0 -- this makes sense in a barplot context
prop_df_genre <- dplyr::mutate_all(prop_df_genre, ~tidyr::replace_na(., 0))
prop_df_genre <- as.data.frame(prop_df_genre)
rownames(prop_df_genre) <- prop_df_genre$genre
prop_df_genre$genre <- NULL

head(prop_df_genre)

#### set colours for the histograms ####
colors_border = c(
  rgb(0.2, 0.5, 0.5, 0.9),
  rgb(0.8, 0.2, 0.5, 0.9),
  rgb(0.7, 0.5, 0.1, 0.9),
  rgb(0.4, 0.6, 0.6, 0.9),
  rgb(0.6, 0.4, 0.2, 0.9),
  rgb(0.3, 0.7, 0.7, 0.9),
  rgb(0.7, 0.3, 0.7, 0.9),
  rgb(0.5, 0.8, 0.4, 0.9),
  rgb(0.4, 0.4, 0.8, 0.9),
  rgb(0.6, 0.6, 0.3, 0.9),
  rgb(0.5, 0.5, 0.5, 0.9)
)

colors_in = c(
  rgb(0.2, 0.5, 0.5, 0.4),
  rgb(0.8, 0.2, 0.5, 0.4),
  rgb(0.7, 0.5, 0.1, 0.4),
  rgb(0.4, 0.6, 0.6, 0.4),
  rgb(0.6, 0.4, 0.2, 0.4),
  rgb(0.3, 0.7, 0.7, 0.4),
  rgb(0.7, 0.3, 0.7, 0.4),
  rgb(0.5, 0.8, 0.4, 0.4),
  rgb(0.4, 0.4, 0.8, 0.4),
  rgb(0.6, 0.6, 0.3, 0.4),
  rgb(0.5, 0.5, 0.5, 0.4)
)

#### set labels for the histograms ####
plots_list <- vector("list", nrow(prop_df_genre))
labels$ordering_factor <- factor(labels$nur_genre, levels = c("unclassified", "Suspense", "Young_adult", "Historical_fiction", 
                                                              "Literary_fiction", "Literary_thriller", "Children_fiction", 
                                                              "Other fiction", "Romanticism", "Non-fiction", "Fantasy_fiction"))

labels <- labels[order(labels$ordering_factor), ]

labels$ordering_factor <- NULL

#### produce and save the plots in a for loop ####
prop_df_genre <- prop_df_genre[1:11,] 

for (i in (1:nrow(prop_df_genre))) {
  png(paste0("radar_plot_", labels$nur_genre[i], ".png"), width = 6000, height = 3500, res=300)
  print(labels$nur_genre[i])
  genre_df <- prop_df_genre[i,]
  
  # Extract the maximum value for axis scaling
  max_val <- max(genre_df)
  min_val <- min(genre_df)
  
  genre_df_ <- rbind(rep(max_val, ncol(genre_df)),
                     rep(min_val, ncol(genre_df)), 
                     genre_df) # add min and max
  
  radarchart(genre_df_,                # Data for the first genre
             axistype = 1,
             pcol = colors_border[i], 
             pfcol = colors_in[i], 
             plwd = 4, 
             plty = 1,
             cglcol = "grey", 
             cglty = 1, 
             axislabcol = "grey",
             caxislabels=c("", "", "", "", paste0(round(max_val, 1)*100, "%")),
             cglwd = 0.8,
             vlcex = 2)
  plots_list[[i]] <- recordPlot()
  title(main = labels$combined_column[i])
  dev.off()
}
