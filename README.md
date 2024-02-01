# JCLS 2024 From Review to genre to Novel and Back

Code and data for the JCLS 2024 paper "From Review to Genre to Novel and Back - An Attempt To Relate Reader Impact to Phenomena of Novel Text".

This consists of a number of Jupyter notebooks that generate the tables, figures and statistics that appear in the paper. 

- [Book statistics](./notebooks/book-length-statistics.ipynb) contains the statistics of the datasets and linking between books, reviews, genre information and reading impact.
- [Linking book genre and reviews](./notebook/dataset-linking-statistics.ipynb): contains the steps to link book genre information, E-pub metadata and reviews.
- [Topic to theme](./notebooks/topic-to-theme.ipynb): contains the mapping between topics from the topic model and broader themes.
- src folder. This contains a script with custom made functions used in the scripts
- [Keyness analysis per genre](./notebooks/keyness-analysis-percent_diff-genre.ipynb): contains the python script to run the keyness analysis per genre. 
- [Keyness analysis per theme](./notebooks/keyness-analysis-percent_diff-theme.ipynb): contains the python script to run the keyness analysis per theme. 
- [Linking topics to reviews](./notebooks/topics-to-reviews.ipynb): contains the code that links topics to reviews and produces a dataframe with proportions of topics per book
- [Linking topics to themes](./notebooks/topics-to-theme.ipynb): contains the code that links topics to themes, checks topical overlap between themes and counts the number of books per theme.


The `data` directory contains the following files:
- `isbn_topic_scores.tsv.gz`: the Top2Vec topic scores per ISBN
- [key_impact_terms-more_likely_per_genre.md](data/key_impact_terms-more_likely_per_genre.md): contains a table with the %Diff scores of impact terms per genre and impact type that are statistically significantly more likely to occur in reviews for the given genre than for other genres. 
- [key_impact_terms-less_likely_per_genre.md](data/key_impact_terms-less_likely_per_genre.md): contains a table with the %Diff scores of impact terms per genre and impact type that are statistically significantly less likely to occur in reviews for the given genre than for other genres. 
- [nur_genre_map.md](data/nur_genre_map.md): contains the mapping between NUR codes and the genres used in the paper.

The `images` directory contains the images used in the paper and additional images that are left out of the paper for reasons of space.

