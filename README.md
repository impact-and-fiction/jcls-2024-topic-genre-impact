# JCLS 2024 From Review to Genre to Novel and Back

Code and data for the JCLS 2024 paper "From Review to Genre to Novel and Back - An Attempt To Relate Reader Impact to Phenomena of Novel Text".

This consists of a number of Jupyter notebooks that generate the tables, figures and statistics that appear in the paper. 

The `notebooks` directory contains the following notebooks used for the analysis in the paper:
- [Book statistics](./notebooks/book-length-statistics.ipynb) contains the statistics of the datasets and linking between books, reviews, genre information and reading impact.
- [Linking book genre and reviews](./notebook/dataset-linking-statistics.ipynb): contains the steps to link book genre information, E-pub metadata and reviews.
- [Topic to reviews](./notebooks/topic-to-reviews.ipynb): contains the mapping between topics from the topic model and the review dataset.
- [Document proportions analysis per genre](./notebooks/doc_freq-analysis-doc_proportions-genre.ipynb): contains the python script to run the keyness analysis per genre. 
- [Document proportions analysis per theme](./notebooks/doc_freq-analysis-doc_proportions-theme.ipynb): contains the python script to run the keyness analysis per theme. 
- [Linking topics to reviews](./notebooks/topics-to-reviews.ipynb): contains the code that links topics to reviews and produces a dataframe with proportions of topics per book
- [Linking topics to themes](./notebooks/topic_labels.ipynb): contains the code that links topics to themes, checks topical overlap between themes and counts the number of books per theme.
- `notebooks/src` This sub-directory contains a script with custom made functions used in the scripts

The `data` directory contains the following files:
- `isbn_topic_scores.tsv.gz`: the Top2Vec topic scores per ISBN
- `review-stats-clean.tsv.gz`: anonymised review metadata without review text.
- `review_work_genre_impact_counts.tsv.gz`: the aggregated count of affective, aesthetic and narrative impact terms per review.
- `review_work_genre_impact_terms.tsv.gz`: the occurrence of individual affective, aesthetic and narrative impact terms per review.
- `review_work_genre_theme.gz`: a mapping between review ID, work ID, genre and themes (where themes are the topic labels assigned to each topic and associated cluster of books)
- [nur_genre_map.md](data/nur_genre_map.md): contains the mapping between NUR codes and the genres used in the paper.

The `images` directory contains the images used in the paper and additional images that are left out of the paper for reasons of space.

