import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text


GENRE_MAP_SHORT = {
    'Children_fiction': 'Child. fic',
    'Fantasy_fiction': 'Fantasy',
    'Historical_fiction': 'Hist. fic',
    'Literary_fiction': 'Lit. fic',
    'Literary_thriller': 'Lit. thrill',
    'Non-fiction': 'Non-fic',
    'Other fiction': 'Oth. fic',
    'Regional_fiction': 'Reg. fic',
    'Romance': 'Romance',
    'Suspense': 'Suspense',
    'Young_adult': 'YA',
    'unknown': 'Unkn.'
}

GENRE_MAP_LONG = {
    'Children_fiction': "Children's fiction",
    'Fantasy_fiction': 'Fantasy fiction',
    'Historical_fiction': 'Historical fiction',
    'Literary_fiction': 'Literary fiction',
    'Literary_thriller': 'Literary thriller',
    'Non-fiction': 'Non-fiction',
    'Other fiction': 'Other fiction',
    'Regional_fiction': 'Regional fiction',
    'Romance': 'Romance',
    'Suspense': 'Suspense',
    'Young_adult': 'YA',
    'unknown': 'Unknown'
}


def reset_context(func):

    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        sns.set_context('notebook')
        return output

    return wrapper


def interpret_val(val):
    val = val.strip()
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


def table_1_to_frame(res):
    table = {}
    data = {
        'var': [],
        'val': []
    }
    for row in res.summary().tables[0].data:
        row = [interpret_val(cell) for cell in row]
        k1, v1, k2, v2 = row
        if k1 != '' and v1 != '':
            table[k1] = v1
            data['var'].append(k1)
            data['val'].append(v1)
        if k2 != '' and v2 != '':
            table[k2] = v2
            data['var'].append(k2)
            data['val'].append(v2)
    return pd.DataFrame(data)


# Define functions to output plot of the model coefficients
# Adapted from: https://gist.github.com/JessicaFB/30e9fbe390fb2207e9f86b25d1e686c2
def make_coef_frame(results, map_features: bool = False, label_map=None):
    # Create dataframe of results summary 
    coef_df = pd.DataFrame(results.summary().tables[1].data)
    
    # Add column names
    coef_df.columns = coef_df.iloc[0]

    # Drop the extra row with column labels
    coef_df=coef_df.drop(0)

    # Set index to variable names 
    coef_df = coef_df.set_index(coef_df.columns[0])

    # Change datatype from object to float
    coef_df = coef_df.astype(float)

    # Get errors; (coef - lower bound of conf interval)
    errors = coef_df['coef'] - coef_df['[0.025']
    
    # Append errors column to dataframe
    coef_df['errors'] = errors

    # Drop the constant for plotting
    if 'const' in coef_df.index:
        coef_df = coef_df.drop(['const'])

    # Sort values by coef ascending
    if map_features is True:
        coef_df.index = map_feature_labels(coef_df, label_map)
    return coef_df.sort_values(by=['coef'])

def map_feature_labels(df, label_map = None):
    mapped = []
    for label in df.index:
        if m := re.match(r"\w+\[(.*?)\]", label):
            label = m.group(1)
        if label_map and label in label_map:
            label = label_map[label]
        mapped.append(label)
    return mapped


def get_x_min_max(res_dict):
    xmin, xmax = None, None
    
    for it in res_dict:
        df = make_coef_frame(res_dict[it])
        it_xmin, it_xmax = df['[0.025'].min(), df['0.975]'].max()
        
        it_xmin = it_xmin - abs(it_xmin / 10)
        it_xmax = it_xmax + abs(it_xmax / 10)
        if xmin is None or it_xmin < xmin:
            xmin = it_xmin
        if xmax is None or it_xmax > xmax:
            xmax = it_xmax
    return xmin, xmax


@reset_context
def coefplot(coef_df, dep_var, xmin=None, xmax=None, save_file=None, dpi: int = 150):
    '''
    Takes in results of OLS model and returns a plot of 
    the coefficients with 95% confidence intervals.
    
    Removes intercept, so if uncentered will return error.
    '''
    ### Plot Coefficients ###

    # x-labels
    variables = list(coef_df.index.values)
    
    # Add variables column to dataframe
    coef_df['variables'] = variables
    
    # Set sns plot style back to 'poster'
    # This will make bars wide on plot
    sns.set_context("poster")

    # Define figure, axes, and plot
    height = len(variables) * 0.8
    print(f"len(variables): {len(variables)}\theight: {height}")
    fig, ax = plt.subplots(figsize=(15, height))
    #fig, ax = plt.subplots(figsize=(15, 10))
    
    # Error bars for 95% confidence interval
    # Can increase capsize to add whiskers
    coef_df.plot(x='variables', y='coef', kind='barh',
                 ax=ax, color='none', fontsize=22, 
                 ecolor='steelblue',capsize=0,
                 xerr='errors', legend=False)
    
    # Set title & labels
    #plt.title('Coefficients of Features with 95% Compatibility Intervals',fontsize=24)
    plt.title(f'Ordinary Least Squares fit for {dep_var}',fontsize=24)
    ax.set_ylabel('Features',fontsize=22)
    ax.set_xlabel('Coefficients with 95% Compatibility Intervals',fontsize=22)

    if xmin is not None and xmax is not None:
        ax.set_xlim((xmin, xmax))
    
    # Coefficients
    ax.scatter(y=np.arange(coef_df.shape[0]), 
               marker='o', s=80, 
               x=coef_df['coef'], color='steelblue')
    
    # Line to define zero on the y-axis
    ax.axvline(x=0, linestyle='--', color='red', linewidth=1)

    fig.tight_layout()
    if save_file is not None:
        fig.savefig(save_file, dpi=dpi)
    return plt.show()


def make_genre_diff(df, impact_type, genre1, genre2):
    sign_diff = (df[impact_type][genre1] - df[impact_type][genre2])
    abs_diff = abs(df[impact_type][genre1] - df[impact_type][genre2])
    diff = (pd.concat([df[impact_type][genre1], df[impact_type][genre2], sign_diff, abs_diff], axis=1)
        .rename(columns={0: 'sign_diff', 1: 'abs_diff'})
        .sort_values('sign_diff'))
    diff['sign'] = diff.sign_diff.apply(lambda x: f'more in {GENRE_MAP_LONG[genre1]}' if x >= 0.0 
                                        else f'more in {GENRE_MAP_LONG[genre2]}')
    return diff


def make_theme_diff(df, theme1, theme2):
    #print('make_diff - df.columns:', df.columns)
    sign_diff = (df[theme1] - df[theme2])
    abs_diff = abs(df[theme1] - df[theme2])
    rel_diff1 = abs(abs_diff / df[theme1])
    rel_diff2 = abs(abs_diff / df[theme2])
    max_frac = df[[theme1, theme2]].max(axis=1)
    min_frac = df[[theme1, theme2]].min(axis=1)
    min_max_diff = max_frac - min_frac
    min_max_rel_diff = (max_frac - min_frac) / max_frac
    diff = (pd.concat([df.impact_term, df[theme1], df[theme2], sign_diff, abs_diff, rel_diff1, rel_diff2, min_max_diff, min_max_rel_diff], axis=1)
        .rename(columns={0: 'sign_diff', 1: 'abs_diff', 2: 'rel_diff1', 3: 'rel_diff2', 
                         4: 'min_max_diff', 5: 'min_max_rel_diff',
                         theme1: 'doc_frac1', theme2: 'doc_frac2'})
        #.set_index('impact_term')
        .sort_values('sign_diff'))
    diff['sign'] = diff.sign_diff.apply(lambda x: f'more in {theme1}' if x >= 0.0 
                                        else f'more in {theme2}')
    #diff.index = df.index
    #diff =
    return diff


def add_identity(axes, *line_args, **line_kwargs):
    identity, = axes.plot([], [], *line_args, **line_kwargs)
    def callback(axes):
        low_x, high_x = axes.get_xlim()
        low_y, high_y = axes.get_ylim()
        low = max(low_x, low_y)
        high = min(high_x, high_y)
        identity.set_data([low, high], [low, high])
    callback(axes)
    axes.callbacks.connect('xlim_changed', callback)
    axes.callbacks.connect('ylim_changed', callback)
    return axes


def to_filename(theme):
    return theme.replace(' & ', '__').replace(' / ', '__')


def plot_theme_frac_diff(df, impact_type, theme1, theme2, topn=10, match_scales: bool = False):
    #print('plot_theme_frac - df.columns:', df.columns)
    it_df = df[df.impact_type == impact_type]
    diff = make_theme_diff(it_df, theme1, theme2)
    sign_order = [f'more in {theme1}', f'more in {theme2}']
    top_diff = pd.concat([
        diff.head(topn),
        diff.tail(topn)
    ])
    ax = sns.scatterplot(data=diff, x='doc_frac1', y='doc_frac2', hue='sign', hue_order=sign_order)
    #ax.set_xlim(1,sdf.Freq.max())
    #ax.set_xscale('log')
    ax.set_xlabel(f'Document proportion for theme {theme1}')
    ax.set_ylabel(f'Document proportion for theme {theme2}')

    if match_scales is True:
        low_x, high_x = ax.get_xlim()
        low_y, high_y = ax.get_ylim()
        low_min = min([low_x, low_y])
        high_max = max([high_x, high_y])
        ax.set_xlim((low_min, high_max))
        ax.set_ylim((low_min, high_max))
            
    num_pos_terms = len(diff[diff.sign_diff > 0.0])
    num_neg_terms = len(diff[diff.sign_diff < 0.0])
    num_neu_terms = len(diff[diff.sign_diff == 0.0])
    
    add_identity(ax, color='gray', linestyle='-')
    
    x = list(top_diff['doc_frac1'])
    y = list(top_diff['doc_frac2'])
    labels = list(top_diff.impact_term)

    if impact_type == 'stylistic':
        impact_type = 'aesthethic'
    #ax.set_xlabel(f'Impact term frequency of {num_pos_terms} positive and {num_neg_terms} negative keywords')
    ax.set_title(f'{impact_type.title()} impact terms')
    
    texts = [plt.text(x[i], y[i], labels[i]) for i in range(len(x))]
    adjust_text(texts, arrowprops=dict(arrowstyle="-", color='k', lw=0.5))
    
    ax.figure.savefig(f'../images/doc_prop/doc_prop-scatter-{impact_type}-theme-{to_filename(theme1)}-{to_filename(theme2)}.png', dpi=150)
    plt.show()


def plot_genre_frac_diff(df, impact_type, genre1, genre2, topn=10, match_scales: bool = False):
    diff = make_genre_diff(df, impact_type, genre1, genre2)
    sign_order = [f'more in {GENRE_MAP_LONG[genre1]}', f'more in {GENRE_MAP_LONG[genre2]}']
    top_diff = pd.concat([
        diff.head(topn),
        diff.tail(topn)
    ])
    ax = sns.scatterplot(data=diff, x=genre1, y=genre2, hue='sign', hue_order=sign_order)
    #ax.set_xlim(1,sdf.Freq.max())
    #ax.set_xscale('log')
    ax.set_xlabel(f'Document proportion for genre {GENRE_MAP_LONG[genre1]}')
    ax.set_ylabel(f'Document proportion for genre {GENRE_MAP_LONG[genre2]}')

    if match_scales is True:
        low_x, high_x = ax.get_xlim()
        low_y, high_y = ax.get_ylim()
        low_min = min([low_x, low_y])
        high_max = max([high_x, high_y])
        ax.set_xlim((low_min, high_max))
        ax.set_ylim((low_min, high_max))
            
    num_pos_terms = len(diff[diff.sign_diff > 0.0])
    num_neg_terms = len(diff[diff.sign_diff < 0.0])
    num_neu_terms = len(diff[diff.sign_diff == 0.0])
    
    add_identity(ax, color='gray', linestyle='-')
    
    x = list(top_diff[genre1])
    y = list(top_diff[genre2])
    labels = list(top_diff.index)

    if impact_type == 'stylistic':
        impact_type = 'aesthethic'
    #ax.set_xlabel(f'Impact term frequency of {num_pos_terms} positive and {num_neg_terms} negative keywords')
    ax.set_title(f'{impact_type.title()} impact terms')
    
    texts = [plt.text(x[i], y[i], labels[i]) for i in range(len(x))]
    adjust_text(texts, arrowprops=dict(arrowstyle="-", color='k', lw=0.5))
    
    ax.figure.savefig(f'../images/doc_prop/doc_prop-scatter-{impact_type}-genre-{genre1}-{genre2}.png', dpi=150)
    plt.show()


