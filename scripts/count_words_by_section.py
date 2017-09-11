import glob
import math
import os
import plotly.plotly as py
import plotly.graph_objs as go
from project_defines import UnnecessaryDuplicates
import string

def sectionnames_in_wordcount_range(p_section_tuples, p_min_wordcount, p_max_wordcount):

    # Index 0: filename
    # Index 1: text data
    # Index 2: section number
    section_names = []
    for index in range(len(p_section_tuples)):
        word_count = get_word_count(p_section_tuples[index][1])
        if word_count >= p_min_wordcount and word_count <= p_max_wordcount:
            section_names.append(get_section_name(p_section_tuples[index][0]))

    return section_names

def get_buckets(p_word_counts, p_bucket_size):

    # Determine min, max, and number of buckets
    min_count = min(p_word_counts)
    max_count = max(p_word_counts)
    bucket_count = int(math.ceil(float(max_count - min_count) / p_bucket_size)) + 1

    bucket_names = []
    buckets = [0] * bucket_count
    bucket_ranges = [0] * bucket_count

    # Save bucket names for plotting
    current_range_bottom = min_count
    for index in range(len(buckets)):
        current_range_top = current_range_bottom + p_bucket_size
        if current_range_top > max_count:
            current_range_top = max_count
        bucket_ranges[index] = (current_range_bottom, current_range_top)
        bucket_names.append("{0}-{1}".format(current_range_bottom, current_range_top))
        current_range_bottom += p_bucket_size

    # Populate buckets with counts of the sections in the ranges
    
    for index in range(len(p_word_counts)):
        for index2 in range(len(bucket_ranges)):
            if p_word_counts[index] >= bucket_ranges[index2][0] and \
               p_word_counts[index] <= bucket_ranges[index2][1]:
                buckets[index2] += 1 
                # buckets[int(math.floor(p_word_counts[index] / p_bucket_size))] += 1


    return buckets, bucket_names


def get_section_name(p_filename):

    return p_filename.split("_")[2].strip("txt").strip(".")


def get_section_number(p_filename):

    return p_filename.split("_")[1]


def get_unique_words(p_text_data):

    words = p_text_data.replace("\n", " ").split(" ")
    cleaned_words = []
    for w in words:
        cw = strip_punctuation(w.lower()).strip()
        if len(cw) > 0:
            cleaned_words.append(cw)
    return list(set(cleaned_words))

def get_unique_word_count(p_text_data):

    unique_word_set = get_unique_words(p_text_data)
    return len(unique_word_set)


def get_additive_unique_word_counts(p_section_list):

    # Create unique word sets for each section
    word_sets = []
    for index in range(len(p_section_list)):
        word_sets.append(get_unique_words(p_section_list[index]))

    # Save a set of all words
    all_words = []
    for index in range(len(word_sets)):
        all_words.extend(word_sets[index])
    all_words = list(set(all_words))

    # Build a list of all the unique words being used as the sections progress
    additive_word_set_lengths = []
    words_used = []
    for index in range(len(word_sets)):
        words_used.extend(word_sets[index])
        words_used = list(set(words_used))
        additive_word_set_lengths.append(len(words_used))

    return additive_word_set_lengths   

def get_subtractive_unique_word_counts(p_section_list):

    # Create unique word sets for each section
    word_sets = []
    for index in range(len(p_section_list)):
        word_sets.append(get_unique_words(p_section_list[index]))

    # Save a set of all words
    all_words = []
    for index in range(len(word_sets)):
        all_words.extend(word_sets[index])
    all_words = list(set(all_words))

    # Subtractive word sets
    subtractive_word_set_lengths = []
    for index in range(len(word_sets)):
        subtractive_word_set_lengths.append(len(set(all_words) - set(word_sets[index])))
        all_words = list(set(all_words) - set(word_sets[index]))

    # for index in reversed(range(len(p_section_list))):
    #     my_word_set = []
    #     for index2 in range(len(p_section_list)):
    #         if index2 < index:
    #             my_word_set.extend(word_sets[index2])
    #         else:
    #             break
    #     my_word_set = list(set(my_word_set))
    #     subtractive_word_set_lengths.append(len(my_word_set))

    return subtractive_word_set_lengths


def get_word_count(p_text_data):

    words = p_text_data.replace("\n", " ").split(" ")
    cleaned_words = []
    for w in words:
        cw = w.strip()
        if len(cw) > 0:
            cleaned_words.append(cw)
    return len(cleaned_words)    

def get_slopes_from_list(p_count_list):

    slope_list = []
    for index in range(len(p_count_list) - 1):
        slope_list.append(p_count_list[index] - p_count_list[index + 1])
    return slope_list

def get_reverse_slopes_from_list(p_count_list):

    slope_list = []
    for index in range(len(p_count_list) - 1):
        slope_list.append(p_count_list[index + 1] - p_count_list[index])
    return slope_list    

def strip_punctuation(p_word):

    return "".join([c for c in p_word if c not in string.punctuation]).strip()



def main():

    # 1. Read in sections of Moby-Dick
    md_sections = []
    for section_filepath in glob.glob(UnnecessaryDuplicates.section_path + "mobydick_*.txt"):
        with open(section_filepath, "rU") as section_file:
            filename = os.path.basename(section_filepath)
            md_sections.append((filename, section_file.read(), int(get_section_number(filename))))

    # 2. Total word counts of sections
    md_word_total = 0
    all_unique_words = []
    total_unique_words = 0
    for index in range(len(md_sections)):
        section_word_count = get_word_count(md_sections[index][1])
        all_unique_words.extend(get_unique_words(md_sections[index][1]))
        # print "{0}: {1} words".format(get_section_name(md_sections[index][0]), section_word_count)
        md_word_total += section_word_count
    all_unique_words = list(set(all_unique_words))

    # Debug output of total word count
    # print "Total words in Moby-Dick: {0}".format(md_word_total)
    # print "Total unique words in Moby-Dick: {0}".format(len(all_unique_words))

    # 3. Sort section list by section number
    md_sections = sorted(md_sections, key=lambda x: x[2])
    md_sections_words_only = [md_sections[index][1] for index in range(len(md_sections))]

    # 4. Save section names and word counts in separate lists for plotting
    section_names = [get_section_name(md_sections[index][0]) for index in range(len(md_sections))]
    section_word_counts = [get_word_count(md_sections[index][1]) for index in range(len(md_sections))]
    section_unique_word_counts = [get_unique_word_count(md_sections[index][1]) for index in range(len(md_sections))]

    mode_sections = sectionnames_in_wordcount_range(md_sections, 844, 944)
    for index in range(len(mode_sections)):
        print mode_sections[index]
    if True:
        return

    # # 5a. Output a bar graph listing in-order word counts of each section
    # data = [go.Bar(x=section_names, y=section_word_counts)]
    # layout = go.Layout(xaxis=dict(tickangle=-45))
    # fig = go.Figure(data=data, layout=layout)
    # py.plot(fig, filename="section_wordcounts_mobydick")

    # 5a-i. Plot bucketed view of the section word counts (w/ suggested bucket size)
    buckets, bucket_names = get_buckets(section_word_counts, 100)
    print "Average: {0}".format(float(sum(section_word_counts)) / len(section_word_counts))
    print "Mode: {0}".format(buckets.index(max(buckets)))
    data = [go.Bar(x=bucket_names, y=buckets)]
    layout = go.Layout(xaxis=dict(tickangle=-45))
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename="wordcount_buckets_mobydick")

    # data = [go.Bar(x=section_names, y=section_word_counts)]
    # layout = go.Layout(xaxis=dict(tickangle=-45))
    # fig = go.Figure(data=data, layout=layout)
    # py.plot(fig, filename="section_wordcounts_mobydick")


    # 5b. Output a bar graph listing in-order unique word counts of each section
    # data = [go.Bar(x=section_names, y=section_unique_word_counts)]
    # layout = go.Layout(xaxis=dict(tickangle=-45))
    # fig = go.Figure(data=data, layout=layout)
    # py.plot(fig, filename="section_unique_wordcounts_mobydick")

    # 5c. Unique word to words ratios
    # unique_word_to_words_ratio = []
    # for index in range(len(section_unique_word_counts)):
    #     unique_word_to_words_ratio.append(float(section_unique_word_counts[index]) / section_word_counts[index])
    # data = [go.Bar(x=section_names, y=unique_word_to_words_ratio)]
    # layout = go.Layout(xaxis=dict(tickangle=-45))
    # fig = go.Figure(data=data, layout=layout)
    # py.plot(fig, filename="unique_word_to_words_ratio_mobydick")

    # # 5d. Output a bar graph listing in-order a subtractive accounting of unique word counts of each section
    # subtractive_unique_word_counts = get_subtractive_unique_word_counts(md_sections_words_only)
    # data = [go.Bar(x=section_names, y=subtractive_unique_word_counts)]
    # layout = go.Layout(xaxis=dict(tickangle=-45))
    # fig = go.Figure(data=data, layout=layout)
    # py.plot(fig, filename="section_subtractive_unique_wordcounts_mobydick")

    # # 5e. Slope plot of 5c
    # subtractive_unique_word_counts = get_subtractive_unique_word_counts(md_sections_words_only)
    # ssuw_section_slopes = get_slopes_from_list(subtractive_unique_word_counts)
    # data = [go.Scatter(x=section_names, y=ssuw_section_slopes, mode="lines")]
    # layout = go.Layout(xaxis=dict(tickangle=-45))
    # fig = go.Figure(data=data, layout=layout)
    # py.plot(fig, filename="nsuw_slopes_mobydick")

    # # 5f. Output a bar graph listing in-order a additive accounting of unique word counts of each section
    # additive_unique_word_counts = get_additive_unique_word_counts(md_sections_words_only)
    # data = [go.Bar(x=section_names, y=additive_unique_word_counts)]
    # layout = go.Layout(xaxis=dict(tickangle=-45))
    # fig = go.Figure(data=data, layout=layout)
    # py.plot(fig, filename="section_additive_unique_wordcounts_mobydick")

    # # 5g. Slope plot of 5f
    # additive_unique_word_counts = get_additive_unique_word_counts(md_sections_words_only)
    # sauw_section_slopes = get_reverse_slopes_from_list(additive_unique_word_counts)
    # data = [go.Scatter(x=section_names, y=sauw_section_slopes, mode="lines")]
    # layout = go.Layout(xaxis=dict(tickangle=-45))
    # fig = go.Figure(data=data, layout=layout)
    # py.plot(fig, filename="sauw_slopes_mobydick")




if "__main__" == __name__:
    main()