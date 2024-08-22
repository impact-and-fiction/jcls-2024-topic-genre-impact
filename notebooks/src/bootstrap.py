import numpy as np


def resample(sample, resample_length):
    resample_index = np.random.randint(0, len(sample), resample_length)
    return sample[resample_index]


def two_sample_bootstrap_test(sample1, sample2, stat_func, num_samples: int = 1000):
    sample1 = np.array(sample1)
    sample2 = np.array(sample2)
    resampled_stats = []
    resampled_signs = []
    for n in range(num_samples):
        resample1 = resample(sample1, len(sample1))
        resample2 = resample(sample2, len(sample2))
        res1 = stat_func(resample1)
        res2 = stat_func(resample2)
        if res2 > 0.0:
            stat = res1 / res2
            sign = 1 if stat > 1.0 else 0
        else:
            stat = np.inf if res1 > 0.0 else 0.0
            sign = 1 if res1 > 0.0 else 0
        resampled_stats.append(stat)
        resampled_signs.append(sign)
    p_value = sum(resampled_signs) / len(resampled_signs)
    return p_value, np.array([resampled_stats, resampled_signs])

