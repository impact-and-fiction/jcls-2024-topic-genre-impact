# JCLS 2024 From Review to genre to Novel and Back

Code and data for the JCLS 2024 paper "From Review to Genre to Novel and Back - An Attempt To Relate Reader Impact to Phenomena of Novel Text".

This consists of a number of Jupyter notebooks that generate the tables, figures and statistics that appear in the paper. 

- [Book statistics](./notebooks/book-statistics.ipynb) contains the statistics of the datasets and linking between books, reviews, genre information and reading impact.
- [Linking book genre and reviews](./notebook/dataset-linking-statistics.ipynb): contains the steps to link book genre information, E-pub metadata and reviews.
- [Topic to theme](./notebooks/topic-to-theme.ipynb): contains the mapping between topics from the topic model and broader themes.
- src folder. This contains a script with custom made functions used in the scripts
- [Keyness analysis](./notebooks/keyness-analysis.ipynb): contains the python script to run the keyness analysis. 
- [Keyness plots](./notebooks/plot_keyness.R): this is an R script that produces the scatter plots with the impact words sorted by keyness. Takes as input the output of the [Keyness Analysis](./notebooks/keyness-analysis.ipynb) notebook.
- [Linking topics to reviews](./notebooks/topics-to-reviews.ipynb): contains the code that links topics to reviews and produces a dataframe with proportions of topics per book
- [Plot themes per genre](./notebooks/plot_circular_histograms.R): this is an R script that produces the circular histograms. Takes as input the output of the [Linking topics to reviewsp](./notebooks/topics-to-reviews.ipynb) notebook.



