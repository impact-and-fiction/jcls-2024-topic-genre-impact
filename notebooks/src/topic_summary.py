"""
This module contains classes and functions for processing and analyzing book reviews,
mapping genres to novels by ISBN, and analyzing Top2Vec models.
"""

import ast
import gzip
import warnings
import os
import re
from typing import List, Optional, Union
import numpy as np
import pandas as pd
from top2vec import Top2Vec
from tqdm import tqdm
from scipy.spatial.distance import cosine
warnings.filterwarnings("ignore", module="umap")
warnings.filterwarnings("ignore", module="numba")


class ReviewExtractor:
    """ Map reviews to novels by work-id """

    def __init__(self, review_dir: str, raw_review_data: str):
        self.review_dir = review_dir
        self.raw_review_data = raw_review_data

    def load_review_impact_matches(self) -> pd.DataFrame:
        """
        Load the review impact matches from a gzipped CSV file.

        Returns:
            pd.DataFrame: Dataframe containing the impact reviews
        """
        with gzip.open(self.review_dir, 'rt') as file:
            return pd.read_csv(file, sep='\t')

    def load_review_stats(self) -> pd.DataFrame:
        """
        Load the review statistics from a gzipped CSV file.

        Returns:
            pd.DataFrame: Dataframe containing the review info about title and authors.
        """
        with gzip.open(self.raw_review_data, 'rt') as file:
            return pd.read_csv(file, sep='\t')

    def get_impact_reviews(self) -> pd.DataFrame:
        """
        Get impact reviews by merging review statistics and review impact matches.
        Returns:
            pd.DataFrame: Dataframe containing the impact reviews with
            their relative info about the authors and titles of the books
        """

        reviews = self.load_review_stats()
        raw_data = self.load_review_impact_matches()

        reviews = reviews.rename(columns={'doc_id': 'review_id'})
        merged_reviews = pd.merge(reviews, raw_data, on='review_id')

        # Pick columns that are relevant
        merged_reviews_minimal = merged_reviews[
            ['work_id', 'review_id', 'affect', 'style',
             'narrative', 'reflection', 'impact_term',
             'review_num_words']
        ]

        return merged_reviews_minimal


class NurGenreMapper:
    """ Map genres to novels by isbn """

    def __init__(self, isbn_map: str, isbn_work_id_mappings_file: str):
        self.isbn_map = isbn_map
        self.isbn_work_id_mappings_file = isbn_work_id_mappings_file

    GENRE_VOCABS = ['nur', 'thema', 'bisac', 'brinkman', 'unesco']

    genres = [
        "Young_adult", "Historical_fiction", "Fantasy_fiction", "Romanticism",
        "Literary_thriller", "Children_fiction", "Suspense", "Regional_fiction",
        "Literary_fiction"
    ]

    NUR_MAPPINGS = {
        300: "Literary_fiction",
        301: "Literary_fiction",
        302: "Literary_fiction",
        305: "Literary_thriller",
        313: "Suspense",
        330: "Suspense",
        331: "Suspense",
        332: "Suspense",
        339: "Suspense",
        334: "Fantasy_fiction",
        280: "Children_fiction",
        281: "Children_fiction",
        282: "Children_fiction",
        283: "Children_fiction",
        284: "Young_adult",
        285: "Young_adult",
        342: "Historical_fiction",
        343: "Romanticism",
        344: "Regional_fiction"
    }

    def nur_genre(self, nur) -> str:
        """
        Categorises nur values into a genre
        Parameters:
            nur (str): The NUR code or value.

        Returns:
            Optional[str]: The corresponding genre or None.
        """
        if pd.isna(nur):
            return np.nan
        if nur in self.NUR_MAPPINGS:
            return self.NUR_MAPPINGS[nur]
        if 280 <= nur < 350:
            return "Other fiction"
        return "Non-fiction"

    @staticmethod
    def map_list(value):
        """
        Converts a string representation of a list to an actual list.

        Parameters:
            value (Union[str, None]): String representation of a list or None.

        Returns:
            Union[List, str, None]: The actual list or the original value if not a string.
        """
        if isinstance(value, str):
            return ast.literal_eval(value)
        if pd.isna(value):
            return value
        print(value, pd.isna(value))
        return value

    def map_genre(self, nurs: Union[List[str], None]) -> Optional[str]:
        """
        Maps a list of NUR codes/values to a genre.

        Parameters:
            nurs (Union[List[str], None]): List of NUR codes/values.

        Returns:
            Optional[str]: The corresponding genre or None.
        """
        if isinstance(nurs, list):
            nurs = [nur for nur in nurs if nur != '']

            for nur in self.NUR_MAPPINGS:
                if str(nur) in nurs:
                    return self.NUR_MAPPINGS[nur]

            if any((280 <= int(nur) < 350) for nur in nurs):
                return "Other fiction"
            return "Non-fiction"
        if pd.isna(nurs):
            return nurs

        print(nurs, type(nurs))
        return None

    def process_genre_mapping(self) -> pd.DataFrame:
        """
        Process the genre mappings from a file and filter based on certain conditions.

        Returns:
            pd.DataFrame: A filtered dataframe with work_id, record_id (isbn), and nur_genre.
        """
        dtype = {vocab: str for vocab in self.GENRE_VOCABS}

        mapping = pd.read_csv(self.isbn_work_id_mappings_file,
                              index_col=False, sep='\t', dtype=dtype)
        for vocab in self.GENRE_VOCABS:
            mapping[vocab] = mapping[vocab].apply(self.map_list)

        mapping['nur_genre'] = mapping['nur'].apply(self.map_genre)
        # create minimal dataframe, and select only the isbn entries
        isbn_work_id_map_filtered = mapping[
            mapping['record_id_type'] == 'isbn'][['work_id', 'record_id', 'nur_genre']]

        # note that `record_id` is our isbn
        # I rename it for clarity
        isbn_work_id_map_filtered = isbn_work_id_map_filtered.rename(columns={'record_id': 'isbn'})
        return isbn_work_id_map_filtered

    def process_isbn_nur_mapping(self) -> pd.DataFrame:
        """
        Process the ISBN to NUR mappings from a file and filter unnecessary columns.

        Returns:
            pd.DataFrame: A filtered dataframe with isbn, author, title, and nur.
        """
        dtype = {
            'isbn': str,
            'nur': str
        }

        isbn_map_df = pd.read_csv(self.isbn_map, index_col=False, sep='\t', dtype=dtype)
        # filter-out unnecessary columns
        isbn_map_filtered = isbn_map_df[['isbn', 'author', 'title', 'nur']]
        return isbn_map_filtered

    def merge_isbn_nur_genre(self) -> pd.DataFrame:
        """
        Merge the processed genre mappings and ISBN to NUR mappings on the ISBN column.

        Returns:
            pd.DataFrame: Merged dataframe with information from both mappings.
        """
        isbn_work_id_map_filtered = self.process_genre_mapping()
        isbn_map_filtered = self.process_isbn_nur_mapping()
        df_mapped_isbn = pd.merge(
            isbn_work_id_map_filtered, isbn_map_filtered, on=['isbn']
        )
        return df_mapped_isbn


class ModelAnalyser:
    """ analyses the Top2Vec output """

    @staticmethod
    def _get_file_paths(directory: str):
        """
        This function retrieves the paths of all files in the specified directory.

        Parameters:
        - directory (str): The path to the directory containing the files.

        Returns:
        - list of str: A list of paths to the files in the directory.
        """

        if not os.path.exists(directory):
            raise ValueError(f"The specified directory '{directory}' does not exist.")

        all_entries = os.listdir(directory)

        model_file_paths = [
            os.path.join(directory, entry)
            for entry in all_entries
            # filter by '.model' files
            if os.path.isfile(os.path.join(directory, entry)) and entry.endswith('.model')
        ]

        return model_file_paths

    @staticmethod
    def load_model(path: str):
        """Load top2vec model"""
        return Top2Vec.load(path)

    @staticmethod
    def get_model_name(path: str):
        """get models' name"""
        return os.path.basename(path)

    @staticmethod
    def get_vectors_from_model(model: Top2Vec):
        """get document, topic and word vectors
        from the models output"""
        return model.document_vectors, model.topic_vectors, model.word_vectors

    def load_model_components(self, path: str):
        """
        Load necessary components of the model

        Parameters:
            - path (str): Path to the model file.

        Returns:
            - tuple: (model_name, model, document_vectors, topic_vectors, word_vectors)
        """

        model_name = self.get_model_name(path)
        model = self.load_model(path)
        dv, tv, wv = self.get_vectors_from_model(model)
        document_ids = model.document_ids

        return model_name, model, dv, tv, wv, document_ids

    def extract_model_metadata(self, path: str) -> pd.DataFrame:
        """
        Generate a DataFrame from provided file paths of model files.

        Parameters:
        - path (list of str): A list of full file paths to model files.

        Returns:
        - DataFrame: A pandas DataFrame with columns:
          * Model Name
          * Type (balanced/unbalanced)
          * Frequency
          * Genre
          * Window (fine-grained/coarse-grained)
        """
        genres = NurGenreMapper.genres

        data = []

        model_name = self.get_model_name(path)

        # type
        type_ = "balanced" if "balanced" in model_name else "unbalanced"

        # frequency
        freq_match = re.search(r'(\d+\.\d+_\d+\.\d+)', model_name)
        frequency = freq_match.group(1) if freq_match else None

        # genre
        genre = None
        for genre_ in genres:
            if genre_ in model_name:
                genre = genre_
                break

        # window
        window = "5000" if "5000" in model_name else "full_doc"

        data.append([model_name, type_, frequency, genre, window])

        df = pd.DataFrame(data, columns=['model', 'type', 'frequency', 'genre', 'window'])
        return df

    @staticmethod
    def get_model_statistics(model_name, dv, tv, wv):
        """
        Retrieves model statistics

        Parameters:
        - file_paths (list of str): A list of full file paths to model files.

        Returns:
        - DataFrame: A pandas dataframe containing model statistics with columns:
          'model', 'documentCount', 'topicCount', and 'wordCount'.

        """

        topic_count = tv.shape[0]
        document_count = dv.shape[0]
        word_count = wv.shape[0]

        return [model_name, document_count, topic_count, word_count]

    @staticmethod
    def map_topics(model_name, tv, document_ids, document_topics):
        """
        Associate topics with books isbn and identifies topics that don't
        have a corresponding isbn

        Parameters:
        - model_name (str): The name of the model.
        - dv (numpy.ndarray): Document vectors.
        - tv (numpy.ndarray): Topic vectors.
        - document_ids (list): List of document IDs corresponding to the document vectors.
        - document_topics (set): Set of topic numbers

        Returns:
        - pd.DataFrame: A dataframe detailing the association between topics and books (by ISBN).
        - topics_with_isbn (set): topics that have an associated ISBN.
        - topics_without_isbn (set): topics that don't have an associated ISBN.
        """

        all_topics = set(range(tv.shape[0]))

        df = pd.DataFrame()

        df['isbn'] = [i.split('-')[0] for i in document_ids]
        df['topic_number'] = document_topics
        df['model'] = model_name

        # Identifying topics with ISBN
        topics_with_isbn = df['topic_number'].unique()

        # Identifying topics without ISBN
        topics_without_isbn = all_topics - set(topics_with_isbn)

        return df, topics_with_isbn, topics_without_isbn

    def get_topics(self, file_paths, verbose=False):
        """
        Returns topics that are both the closest to any document or not

        Parameters:
        - file_paths (str): paths to the Top2Vec models.

        Returns:
        - unused_topics: List of unused topics (topics not closest to any document)
        for the last model in the file_paths.
        - document_topics: list of document topics
        """

        document_topics = []
        model_name, _, dv, tv, _, _ = self.load_model_components(file_paths)
        if verbose:
            print(model_name)
        all_topics = set(range(tv.shape[0]))

        for d_vector in tqdm(dv):
            document_topics.append(np.argmax([cosine(d_vector, i) for i in tv]))

        unused_topics = all_topics - set(document_topics)

        return unused_topics, document_topics

    def add_isbn(self, file_paths, document_topics, non_dominant_topics_set, verbose=False):
        """
        Processes the Top2Vec models, extracts topic information,
        and identifies unmapped isbn topics.

        Parameters:
        - model_path (list of str): Path to the Top2Vec model
        - non_dominant_topics_set (set): Set of topics that are considered non-dominant.
        - verbose (bool, optional): If True, a progress bar will be printed.

        Returns:
        - tuple:
        - model_stats (DataFrame): A DataFrame containing statistics for each model.
        - model_topic (DataFrame): A DataFrame containing topic details for each model.
        - unmapped_topic_df (DataFrame): A DataFrame listing topics
        that haven't been mapped for each model.
        """

        statistics_data = []
        unmapped_topic_data = []

        model_name, _, dv, tv, wv, document_ids = self.load_model_components(file_paths)
        if verbose:
            print(model_name)

        # Collect statistics
        stats = self.get_model_statistics(model_name, dv, tv, wv)
        statistics_data.append(stats)

        # Associate topics to books
        topics_df, _, topics_without_isbn = self.map_topics(
            model_name, tv, document_ids, document_topics
        )
        # Remove non_dominant_topics from topics_without_isbn
        topics_without_isbn_ = list(topics_without_isbn - non_dominant_topics_set)

        unmapped_topic_data.append({
            'model': model_name,
            'topics_without_isbn': topics_without_isbn_
        })

        statistics_df = pd.DataFrame(
            statistics_data, columns=['model', 'documentCount', 'topicCount', 'wordCount']
        )

        return statistics_df, topics_df, pd.DataFrame(unmapped_topic_data)

    def run_summary(self, folder_path, verbose=False, out=""):
        """
        Run all analyses functions, merge its outputs and save the results as csv files.

        Parameters:
        - folder_path (list of str): folder of the Top2Vec models.
        - verbose (boolean): whether you wish to have the model name printed
        - out (string): folder where to save the results
        """
        files = self._get_file_paths(folder_path)

        # create folder if that doesn't exist
        if not os.path.exists(out):
            os.makedirs(out)

        for path in files:
            model_metadata = self.extract_model_metadata(path)
            model_name = model_metadata["model"].iloc[0]

            # extract dominant and non-dominant topics
            non_dominant_topics, document_topics = self.get_topics(path, verbose)

            # Extract stats, add isbn flag topics that are not mapped with an isbn
            model_stats, model_topic, unmapped_topic_df = self.add_isbn(
                path, document_topics, non_dominant_topics, verbose=False
            )

            # merge and save metadata
            metadata = model_metadata.merge(model_stats, on="model")
            metadata_filename = f"{out}/metadata_{model_name}.csv"
            try:
                metadata.to_csv(metadata_filename, index=False)
                print(f"Metadata for {model_name} saved successfully")
            except IOError as error:
                print(f"Error saving metadata for {model_name}: {str(error)}")

            # merge and save topics
            non_dominant_list = list(non_dominant_topics)
            non_dominant_df = pd.DataFrame({
                'model': [model_name],
                'non_dominant_topics': [non_dominant_list]})

            merged_df = model_topic.merge(unmapped_topic_df, on="model"). \
                merge(non_dominant_df, on="model")
            merged_filename = f"{out}/out_{model_name}.csv"
            try:
                merged_df.to_csv(merged_filename, index=False)
                print(f"Topics for {model_name} saved successfully")
            except IOError as error:
                print(f"Error saving topics for {model_name}: {str(error)}")

    @staticmethod
    def closest_topics(doc_vector, topic_vector, n=5):
        """
        Returns the indices of the 'n' closest topics for a given document vector.

        Parameters:
        - doc_vector (numpy array): The document vector.
        - topic_vectors (list of numpy arrays): List of all topic vectors.
        - n (int, optional): Number of closest topics to retrieve. Defaults to 5.

        Returns:
        - idx_closest_topics: Indices of the 'n' closest topics.
        - list of float: cosine distance of the topics' indices
        """
        # Calculate cosine distances for all topic vectors
        distances = [cosine(doc_vector, tv) for tv in topic_vector]
        # Get the indices of the 'n' closest topics
        idx_closest_topics = np.argsort(distances)[:n]
        return idx_closest_topics, [distances[i] for i in idx_closest_topics]

    @staticmethod
    def closest_topics_1stQuartile(doc_vector, topic_vector):

        """
        Returns the indices of the closest topics (in the 1st quartile) for a given document vector.

        Parameters:
        - doc_vector (numpy array): The document vector.
        - topic_vectors (list of numpy arrays): List of all topic vectors.

        Returns:
        - idx_closest_topics: Indices of the topics in the closest quartile.
        - list of float: cosine distance of the topics' indices
        """
        distances = [cosine(doc_vector, tv) for tv in topic_vector]
        threshold = np.percentile(distances, 25)

        # get indices of the topics in the closest quartile
        idx_closest_topics = np.where(np.array(distances) <= threshold)[0].tolist()

        return idx_closest_topics, [distances[i] for i in idx_closest_topics]



