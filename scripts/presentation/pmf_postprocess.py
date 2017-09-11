import glob
import json
import os

import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools

from spacy_meta import spacy_pos_order
from utils_jensen_shannon import jensen_shannon_distance


# Paletted colors for plotting POS
possible_colors_rgb = ["rgb(0,174,239)", "rgb(0,114,188)",   "rgb(46,49,146)",  "rgb(146,39,143)",
                       "rgb(236,0,140)", "rgb(237,28,36)",   "rgb(247,148,30)", "rgb(255,242,0)",
                       "rgb(141,198,63)","rgb(0,166,181)",   "rgb(186,210,237)","rgb(209,145,192)",
                       "rgb(135,129,189)","rgb(134,166,178)","rgb(122,204,200)","rgb(200,221,105)"]

# Global lists and dictionaries
counts_json_filenames = []
section_dict = {}
cluster_filename_dict = {}
filename_cluster_dict = {}
cluster_ids_int = []
allg_set = set([])
bq_sent_files = []
queequeg_sentences = []
bulkington_sentences = []
queequeg_comrade_sentences = []
groups_for_bqs = {}
bulkington_groups = {}
queequeg_groups = {}
queequeg_comrade_groups = {}
bg_set = set([])
qg_set = set([])
qfg_set = set([])
bq_intersection_set = []
sections_pos_dict = {}
pos_profile_vectors = {}
all_sentences = []
chapter_indices = []

qnf_groups = {}
qnfg_set = set([])

# Global paths and values
root_folder = "/Users/PeregrinePickle/Documents/School/New York University/Seminars/Melville/Presentation/"
pmf_output_folder = "output/pmf_results/"
pmf_output_filename = "mobydick_sentence_clusters_1490819354731.csv"
pmf_counts_folder = "output/sentence_bysection_pos_counts/"
sentence_count = 9196
max_cluster_val = 0
total_chapters = 135


def GetBulkingtonGroups(p_root_folder):

    input_folder = "text/split/bysection_bysentence/"
    names_of_interest = {"Bulkington":[], "Queequeg":[]}
    text_of_interest = {"Bulkington":[], "Queequeg":[]}
    for full_filepath in glob.glob(root_folder + input_folder + "*.txt"):
        with open(full_filepath, "r") as input_file:
            data = input_file.read()
            for name in names_of_interest.keys():
                if name in data:
                    names_of_interest[name].append(os.path.basename(full_filepath))
                    text_of_interest[name].append((os.path.basename(full_filepath), data.replace("\n", " ")))

    pmf_output_folder = "/output/pmf_results/"
    pmf_output_file = "mobydick_sentence_clusters_1490819354731.csv"
    sentence_to_group = {}
    bulkington_groups = []
    queequeg_groups = []
    groups_to_sentences = {}
    with open(p_root_folder + pmf_output_folder + pmf_output_file, "r") as pmf_file:
        csv_lines = pmf_file.readlines()
        for line in csv_lines:
            sent_filename,sent_group = line.strip().split(",")
            for name in names_of_interest:
                if sent_filename in names_of_interest[name]:
                    if "Bulkington" == name:
                        print bulkington_groups
                        bulkington_groups.append(sent_group)
                    else:
                        queequeg_groups.append(sent_group)
                    if sent_filename in names_of_interest[name]:
                        sentence_to_group[sent_filename] = sent_group
                        if sent_group not in groups_to_sentences:
                            groups_to_sentences[sent_group] = []
                        groups_to_sentences[sent_group].append(sent_filename)

    return bulkington_groups

# Utility functions
def GetSection(p_filename):

    return p_filename.split("_")[2]

def GetOrder(p_filename):

    filename_pieces = p_filename.split("_")
    return filename_pieces[len(filename_pieces) - 2]

def GetTitle(p_filename):

    filename_pieces = p_filename.split("_")
    
    if 6 == len(filename_pieces):
        title = p_filename[3] + "_" + p_filename[4]
    else: # len == 7
        title = p_filename[3] + "_" + p_filename[4] + "_" + p_filename[5]

    return title

def GetChapter(p_filename):

    filename_pieces = p_filename.split("_")
    for piece in filename_pieces:
        if "chapter" in piece:
            return piece[piece.rfind("r")+1:]
    return "NA"

def GetSentenceNumber(p_filename):

    # Find section and order numbers in filename
    section = GetSection(p_filename)
    order = GetOrder(p_filename)

    # Iterate through sentences by section to determine sentence number in novel
    sentence_number = 0
    for index in range(1, len(section_dict.keys()) + 1):
        for index2 in range(len(section_dict[str(index)])):
            if section == index and order == section_dict[str(index)][index2]:
                return sentence_index
            else:
                sentence_index += 1

def SumPOSVectorStr(p_pos_vector):

    vector_sum = 0
    for index in range(len(p_pos_vector)):
        vector_sum += int(p_pos_vector[index])
    return vector_sum


def CalculateAvgPOS(p_folder, p_json_filenames):

    # Retrieve POS vectors from given files
    pos_vectors = []
    for filename in p_json_filenames:
        with open(p_folder + filename, "r") as input_file:
            data = input_file.read()
            json_file = json.loads(data)
            current_vector = []
            for index in range(len(spacy_pos_order)):
                current_vector.append(json_file["pos"][spacy_pos_order[index]])
            pos_vectors.append(current_vector)

    # Calculate and return the average POS
    avg_pos_vector = [0.0] * len(spacy_pos_order)
    for v in pos_vectors:
        for index in range(len(spacy_pos_order)):
            avg_pos_vector[index] += v[index]
    for index in range(len(spacy_pos_order)):
        avg_pos_vector[index] /= float(len(pos_vectors))

    return avg_pos_vector


def FindClosestVectors(p_test_vector, p_vector_list):

    distance_list = []
    for index in range(len(p_vector_list)):
        distance_list.append(jensen_shannon_distance(p_test_vector, p_vector_list[index]))
    return distance_list.index(min(distance_list))
    

def GetPOSVector(p_folder, p_filename):

    with open(p_folder + p_filename, "r") as counts_file:
        data = counts_file.read()
        json_data = json.loads(data)
    pos_vector = []
    for index in range(len(spacy_pos_order)):
        pos_vector.append(json_data["pos"][spacy_pos_order[index]])
    return pos_vector


def GetText(p_folder, p_filename):

    with open(p_folder + p_filename, "r") as counts_file:
        data = counts_file.read()
        json_data = json.loads(data)
    return json_data["full_text"].strip().replace("\n", " ")

def ConvertJSONFilenameToTxt(p_filename):

    return p_filename[0:p_filename.rfind("_counts.json")] + ".txt"

def IsInTraceInfoGroups(p_sentence, p_traceinfos):

    not_in_groups = True
    for key in p_traceinfos:
        sentence_group = filename_cluster_dict[p_sentence]
        if sentence_group in p_traceinfos[key]["groups"]:
            not_in_groups = False
            break
    return not_in_groups


# 0. Populate the section and cluster dictionaries
def BuildGlobalDictsAndLists():

    global counts_json_filenames
    global section_dict
    global cluster_filename_dict
    global filename_cluster_dict
    global cluster_ids_int
    global allg_set

    global sections_pos_dict
    global pos_profile_vectors  

    global chapter_indices

    # Chapter indices for plotting
    for index in range(total_chapters):
        chapter_indices.append(str(index + 1)) 

    with open(root_folder + pmf_output_folder + pmf_output_filename, "rU") as cluster_file:
        
        lines = cluster_file.readlines()
        
        for line in lines:

            # Example counts filenames
            # md_mobydick_1_etymology_8_counts.json
            # md_mobydick_2_extracts_subsublibrarian_1_counts.json
            
            row = line.strip().split(",")

            # a. Get the counts file json
            counts_filename = os.path.splitext(row[0])[0] + "_counts.json"
            counts_json_filenames.append(counts_filename)
            with open(root_folder + pmf_counts_folder + counts_filename) as counts_file:
                json_data = counts_file.read()
                counts_json = json.loads(json_data)

            # b. Determine section number, order number, and segment title from filename
            filename_pieces = counts_filename.split("_")
            section_number = filename_pieces[2]
            order_number = filename_pieces[len(filename_pieces) - 2]
            if 6 == len(filename_pieces):
                title = counts_filename[3] + "_" + counts_filename[4]
            else: # len == 7
                title = counts_filename[3] + "_" + counts_filename[4] + "_" + counts_filename[5]

            # c. Add this information and the cluster ID and POS counts to the section dictionary
            if section_number not in section_dict:
                section_dict[section_number] = []
            pos_vector = []
            for index in range(len(spacy_pos_order)):
                pos_vector.append(counts_json["pos"][spacy_pos_order[index]])
            section_dict[section_number].append({"cluster": row[1], 
                                                 "order": order_number,
                                                 "title": title,
                                                 "file": counts_json["filename"],
                                                 "counts": pos_vector})

            # d. Add this information to the cluster -> filename dictionary
            cluster_id = row[1]
            if cluster_id not in cluster_filename_dict:
                cluster_filename_dict[cluster_id] = []
            cluster_filename_dict[cluster_id].append({"section": section_number,
                                                      "order": order_number,
                                                      "title": title,
                                                      "file": counts_json["filename"]})

            # e. Add this information to the filename -> cluster dictionary
            filename_cluster_dict[row[0]] = row[1]

            # f. Save all sentences from chapters
            if "NA" != GetChapter(row[0]):
                all_sentences.append(row[0])

    # f. Sort the section dictionary in ascending sentence order by sentence order id
    for index in range(1, len(section_dict.keys()) + 1):
        # Special Case: Section 3 has been removed for Moby-Dick because it is just quotations from other authors
        if 3 == index:
            continue
        section_dict[str(index)] = sorted(section_dict[str(index)], key=lambda k: int(k["order"]))

    # g. Create an integer list of cluster ID values
    cluster_ids_int = filename_cluster_dict.values()
    for index in range(len(cluster_ids_int)):
        cluster_ids_int[index] = int(cluster_ids_int[index])

    # h. Save the number of clusters
    max_cluster_val = max(cluster_ids_int)

    # g. Save all groups as set
    allg_set = set(cluster_filename_dict.keys())


# 1. Determine POS profile mean vectors
def DeterminePOSProfileVectors(p_counts_folder, p_json_filenames, p_cluster_filename_dict):

    total_section_count = 0

    # Get all text section POS vectors
    for index in range(len(p_json_filenames)):

        filename_pieces = p_json_filenames[index].split("_")
        section_number = filename_pieces[2]
        order_number = filename_pieces[len(filename_pieces) - 2]
        if section_number not in sections_pos_dict:  
            sections_pos_dict[section_number] = []

        with open(p_counts_folder + p_json_filenames[index], "r") as json_file:

            sentence_json = json.load(json_file)
            pos_vector = [0] * len(spacy_pos_order)
            for pos_index in range(len(spacy_pos_order)):
                if spacy_pos_order[pos_index] in sentence_json["pos"]:
                    pos_vector[pos_index] = sentence_json["pos"][spacy_pos_order[pos_index]]
                else:
                    pos_vector[pos_index] = 0                       
            sections_pos_dict[section_number].append(pos_vector)

    # Determine mean and variance of the clustered POS vectors
    for cluster_id in p_cluster_filename_dict:
        
        # Get the POS vectors
        pos_vectors = []
        for section_index in range(len(p_cluster_filename_dict[cluster_id])):
            section = p_cluster_filename_dict[cluster_id][section_index]["section"]
            order = p_cluster_filename_dict[cluster_id][section_index]["order"]
            pos_vectors.append(sections_pos_dict[section][int(order) - 1])

        # Calculate the mean of the POS vectors
        pos_mean_vector = [0] * len(spacy_pos_order)
        for section_index in range(len(pos_vectors)):
            for pos_index in range(len(spacy_pos_order)):
                pos_mean_vector[pos_index] += pos_vectors[section_index][pos_index]
        for pos_index in range(len(spacy_pos_order)):
            pos_mean_vector[pos_index] /= float(len(pos_vectors))

        # Calculate the variance of the POS vectors
        pos_variance = 0
        for poem_index in range(len(pos_vectors)):
            delta = np.linalg.norm(np.array([float(i) for i in pos_vectors[poem_index]]) - np.array(pos_mean_vector))
            delta *= delta
            pos_variance += delta

        # Add the mean and variance to the POS profile dict
        pos_profile_vectors[cluster_id] = {}
        pos_profile_vectors[cluster_id]["mean"] = pos_mean_vector
        pos_profile_vectors[cluster_id]["variance"] = pos_variance

    # PMF-POS profile vectors, debug
    # for key in pos_profile_vectors:
    #     print "Cluster ID: {0} PMF-POS info: {1}".format(key, pos_profile_vectors[key])

    # POS vectors by Section, debug
    # for key in sections_pos_dict:
    #     print "Section: {0} POS Vectors: {1}".format(key, sections_pos_dict[key])


# 2. Get list of all Bulkington-Queequeg sentences
def GetAllBulkingtonQueequegSentences():

    bq_file_folder = "output/bq_files/"
    bq_filename = "bq_qb_sentences.txt"
    bulkington_filename = "bulkington_sentences.txt"
    queequeg_filename = "queequeg_sentences.txt"
    queequeg_comrade_filename = "queequeg_comrade_sentences.txt"

    global bq_sent_files
    global bulkington_sentences
    global queequeg_sentences    
    global queequeg_comrade_sentences
    global groups_for_bqs
    global bulkington_groups
    global queequeg_groups
    global queequeg_comrade_groups
    global bg_set
    global qg_set
    global qfg_set
    global bq_intersection_set
    global qnf_groups
    global qnfg_set

    # Get all Bulkington-Queequeg sentences
    with open(root_folder + bq_file_folder + bq_filename, "r") as bq_file:
        lines = bq_file.readlines()
        for line in lines:
            bq_sent_files.append(line.strip().replace(".txt", "_counts.json"))

    # Get all Bulkington sentences
    with open(root_folder + bq_file_folder + bulkington_filename, "r") as bulkington_file:
        lines = bulkington_file.readlines()
        for line in lines:
            bulkington_sentences.append(line.strip())

    # Get all Queequeg sentences
    with open(root_folder + bq_file_folder + queequeg_filename, "r") as queequeg_file:
        lines = queequeg_file.readlines()
        for line in lines:
            queequeg_sentences.append(line.strip())

    # Get all Queequeg comrade sentences (up to ch.21)
    with open(root_folder + bq_file_folder + queequeg_comrade_filename, "r") as queequeg_comrade_file:
        lines = queequeg_comrade_file.readlines()
        for line in lines:
            queequeg_comrade_sentences.append(line.strip())            

    # Find all groups for Bulkington-Queequeg sentences
    for bsf in bq_sent_files:
        groups_for_bqs[bsf] = filename_cluster_dict[bsf[0:bsf.rfind("_counts.json")] + ".txt"] 

    # Get groups for Bulkington and Queequeg sentences (in separate dictionaries)
    for index in range(len(bulkington_sentences)):
        bulkington_groups[bulkington_sentences[index]] = filename_cluster_dict[bulkington_sentences[index]]
    for bsf in groups_for_bqs:
        bsf_text = bsf[0:bsf.rfind("_counts.json")] + ".txt"
        if bsf_text not in bulkington_groups:
            queequeg_groups[bsf_text] = filename_cluster_dict[bsf_text]
            chapter_number = GetChapter(bsf_text)
            if "NA" != chapter_number:
                if int(chapter_number) <= 21:
                    queequeg_comrade_groups[bsf_text] = filename_cluster_dict[bsf_text]
                else:
                    qnf_groups[bsf_text] = filename_cluster_dict[bsf_text]

    # Bulkington and Queequeg groups as sets
    bg_set = set(bulkington_groups.values())
    qg_set = set(queequeg_groups.values())
    qfg_set = set(queequeg_comrade_groups.values())
    bq_intersection_set = bg_set.intersection(qg_set)
    qnfg_set = set(qnf_groups.values())


# 2a. Bulkington-Queequeg group comparisons
def PlotBulkingtonQueequegGroupComparisons():

    bq_sg_dict = { "50": [], "230": [], "232": [], "354": [] }
    bq_sg_dict["50"].append("md_mobydick_26_chapter23_2_counts.json")
    bq_sg_dict["50"].append("md_mobydick_129_chapter126_19_counts.json")
    bq_sg_dict["50"].append("md_mobydick_20_chapter17_17_counts.json")
    bq_sg_dict["50"].append("md_mobydick_20_chapter17_69_counts.json")
    bq_sg_dict["50"].append("md_mobydick_24_chapter21_59_counts.json")
    bq_sg_dict["50"].append("md_mobydick_37_chapter34_58_counts.json")
    bq_sg_dict["50"].append("md_mobydick_50_chapter47_2_counts.json")
    bq_sg_dict["50"].append("md_mobydick_51_chapter48_176_counts.json")
    bq_sg_dict["50"].append("md_mobydick_75_chapter72_39_counts.json")

    bq_sg_dict["230"].append("md_mobydick_26_chapter23_5_counts.json")
    bq_sg_dict["230"].append("md_mobydick_15_chapter12_6_counts.json")
    bq_sg_dict["230"].append("md_mobydick_16_chapter13_41_counts.json")
    bq_sg_dict["230"].append("md_mobydick_30_chapter27_29_counts.json")
    bq_sg_dict["230"].append("md_mobydick_75_chapter72_64_counts.json")

    bq_sg_dict["354"].append("md_mobydick_6_chapter3_82_counts.json")
    bq_sg_dict["354"].append("md_mobydick_18_chapter15_25_counts.json")
    bq_sg_dict["354"].append("md_mobydick_20_chapter17_78_counts.json")

    bq_sg_dict["232"].append("md_mobydick_26_chapter23_1_counts.json")
    bq_sg_dict["232"].append("md_mobydick_102_chapter99_103_counts.json")
    bq_sg_dict["232"].append("md_mobydick_15_chapter12_1_counts.json")
    bq_sg_dict["232"].append("md_mobydick_15_chapter12_8_counts.json")
    bq_sg_dict["232"].append("md_mobydick_64_chapter61_45_counts.json")
    bq_sg_dict["232"].append("md_mobydick_84_chapter81_84_counts.json")

    # Plot Groups compared to all Bulkington-Queequeg sentences
    # Group 50
    # bq_s50 = list(set(bq_sent_files) - set(bq_sg_dict["50"]))
    # PlotCompareGroupToGroup(bq_sg_dict["50"], bq_s50, "50", "bq_s50")

    # Group 230
    # bq_s230 = list(set(bq_sent_files) - set(bq_sg_dict["230"]))
    # PlotCompareGroupToGroup(bq_sg_dict["230"], bq_s230, "230", "bq_s230")
    
    # Group 354
    # bq_s354 = list(set(bq_sent_files) - set(bq_sg_dict["354"]))
    # PlotCompareGroupToGroup(bq_sg_dict["354"], bq_s354, "354", "bq_s354")

    # Group 232
    # bq_s232 = list(set(bq_sent_files) - set(bq_sg_dict["232"]))
    # PlotCompareGroupToGroup(bq_sg_dict["232"], bq_s232, "232", "bq_s232")

    bulk_50_vector = GetPOSVector(root_folder + pmf_counts_folder, "md_mobydick_26_chapter23_2_counts.json")
    bulk_230_vector = GetPOSVector(root_folder + pmf_counts_folder, "md_mobydick_26_chapter23_5_counts.json")
    bulk_354_vector = GetPOSVector(root_folder + pmf_counts_folder, "md_mobydick_6_chapter3_82_counts.json")

    queeq_50_vectors = []
    queeq_230_vectors = []
    queeq_354_vectors = []

    for group_key in bq_sg_dict:
        for index in range(len(bq_sg_dict[group_key])):
            if "50" == group_key and "md_mobydick_26_chapter23_2_counts.json" != bq_sg_dict[group_key][index]:
                queeq_50_vectors.append(GetPOSVector(root_folder + pmf_counts_folder, bq_sg_dict[group_key][index]))
            elif "230" == group_key and "md_mobydick_26_chapter23_5_counts.json" != bq_sg_dict[group_key][index]:
                queeq_230_vectors.append(GetPOSVector(root_folder + pmf_counts_folder, bq_sg_dict[group_key][index]))
            elif "354" == group_key and "md_mobydick_6_chapter3_82_counts.json" != bq_sg_dict[group_key][index]:
                queeq_354_vectors.append(GetPOSVector(root_folder + pmf_counts_folder, bq_sg_dict[group_key][index]))

    print queeq_354_vectors

    print "50: {0}".format(queeq_50_vectors)
    print "230: {0}".format(queeq_230_vectors)
    print "354: {0}".format(queeq_354_vectors)

    indices_50 = FindClosestVectors(bulk_50_vector, queeq_50_vectors) + 1
    indices_230 = FindClosestVectors(bulk_230_vector, queeq_230_vectors) + 1
    indices_354 = FindClosestVectors(bulk_354_vector, queeq_354_vectors) + 1

    print "50: {0}".format(indices_50)
    print "230: {0}".format(indices_230)
    print "354: {0}".format(indices_354)

    print "Closest to Bulkington 50: {0}".format(bq_sg_dict["50"][indices_50])
    print "Closest to Bulkington 230: {0}".format(bq_sg_dict["230"][indices_230])
    print "Closest to Bulkington 354: {0}".format(bq_sg_dict["354"][indices_354])

    print "Bulkington 50: {0}".format(GetText(root_folder + pmf_counts_folder, "md_mobydick_26_chapter23_2_counts.json"))
    print "==========================================================================="
    print "Bulkington 230: {0}".format(GetText(root_folder + pmf_counts_folder, "md_mobydick_26_chapter23_5_counts.json"))
    print "==========================================================================="
    print "Bulkington 354: {0}".format(GetText(root_folder + pmf_counts_folder, "md_mobydick_6_chapter3_82_counts.json"))
    print "==========================================================================="
    print bq_sg_dict["50"][indices_50]
    print "Queequeg closest 50: {0}".format(GetText(root_folder + pmf_counts_folder, bq_sg_dict["50"][indices_50]))
    print "==========================================================================="
    print bq_sg_dict["230"][indices_230]
    print "Queequeg closest 230: {0}".format(GetText(root_folder + pmf_counts_folder, bq_sg_dict["230"][indices_230]))
    print "==========================================================================="
    print bq_sg_dict["354"][indices_354]
    print "Queequeg closest 354: {0}".format(GetText(root_folder + pmf_counts_folder, bq_sg_dict["354"][indices_354]))


# 3a. Plot Tiled POS for sections
def PlotSimilarPoemsPOSTiled(p_section, p_order, p_rows, p_cols, p_pos2ignore):

    int_order = (int)(p_order) - 1
    pos_vectors_toplot = []
    sentence_titles = []
    pos_order_wo_ignore = []
    for index in range(len(pos_order)):
        if pos_order[index] not in p_pos2ignore:
            pos_order_wo_ignore.append(pos_order[index])
    profile_sum = sum(pos_profile_vectors[section_dict[p_section][int_order]["cluster"]]["mean"])

    # Gather POS vectors for all similar poems including the selected poem
    for sentence in cluster_dict[section_dict[p_section][int_order]["cluster"]]:
        
        # Proportionalize the pos counts in [0,1] and then save
        pos_vector = fascicle_pos_dict[str(int(sentence["section"]) + 1)][int(sentence["order"])]
        pos_counts_sum = sum(pos_vector)
        for pos_index in range(len(pos_order)):
            pos_vector[pos_index] /= float(pos_counts_sum)
        pos_vectors_toplot.append(pos_vector)

        # Save the title
        sentence_titles.append(sentence["title"])

    for index in range(len(sentence_titles)):
        print "{0}. {1}".format(index, sentence_titles[index])

    # Create vertical POS vectors for poems
    pos_verticles = []
    for index in range(len(pos_order)):
        current_pos_list = []
        for index2 in range(len(pos_vectors_toplot)):
            current_pos_list.append(pos_vectors_toplot[index2][index])
        # Append the POS from the profile vector as the last
        current_pos_list.append(pos_profile_vectors[section_dict[p_section][int_order]["cluster"]]["mean"][index] / float(profile_sum))
        print len(current_pos_list)
        pos_verticles.append(current_pos_list)

    # Plot the POS of all poems in a horizontal bar graph
    trace_list = []
    # sentence_titles.reverse()
    for index in range(len(pos_order)):
        # pos_verticles[index].reverse()
        if pos_order[index] not in p_pos2ignore:
            color_list = [possible_colors_rgb[index]] * (len(sentence_titles) + 1)
            color_list[len(color_list) - 1] = "rgb(128,128,128)" 
            color_list[12] = "rgb(0,0,0)"
            trace = go.Bar(
                y = pos_verticles[index],
                x = range(1,len(sentence_titles) + 1),
                name = "{0}".format(pos_order[index]),
                orientation = "v",
                marker=(dict(color=color_list))
            )
            trace_list.append(trace)
    # trace_list.reverse()

    # Append the POS profile vector with an outline
    #trace = go.Bar(pos_profile_vectors[section_dict[p_section][int_order]["cluster"]]["mean"]

    # layout = go.Layout(barmode="stack")
    layout = go.Layout(xaxis=dict(autotick=False,
                                  dtick=2,
                                  tickfont=dict(size=10, color="black")),
                       yaxis=dict(tickfont=dict(size=10, color="black")))
    fig = go.Figure(data=trace_list, layout=layout)
    fig = tools.make_subplots(rows=p_rows, cols=p_cols, subplot_titles=tuple(pos_order_wo_ignore))
    current_trace = 0
    for rindex in range(p_rows):
        for cindex in range(p_cols):
            fig.append_trace(trace_list[current_trace], rindex + 1, cindex + 1)
            current_trace += 1
    # py.plot(fig, filename="fascicle{0}poem{1}_similarpoems_pos_tiled_withprof".format(p_section, p_order)) 

# 3b. Plot Tiled POS for select sentences
def PlotSentencesPOSTiled(p_ordered_filenames, p_section_dict, p_rows, p_cols, p_descriptor, p_pos2ignore=[]):

    # 1. Determine which POS will be plotted
    pos_order_wo_ignore = []
    for index in range(len(spacy_pos_order)):
        if spacy_pos_order[index] not in p_pos2ignore:
            pos_order_wo_ignore.append(spacy_pos_order[index])

    # 2. Retrieve and normalize the POS vectors and titles (for plotting) for each sentence
    pos_vectors_toplot = []
    sentence_titles = []
    for filename in p_ordered_filenames:

        # print "Filename: {0}".format(filename)
        # print "Section: {0}".format(GetSection(filename))
        pos_vector = p_section_dict[GetSection(filename)][int(GetOrder(filename)) - 1]["counts"]
        for index in range(len(pos_vector)):
            pos_vector[index] = float(pos_vector[index])
        pos_counts_sum = sum(pos_vector)

        for pos_index in range(len(spacy_pos_order)):
            pos_vector[pos_index] /= float(pos_counts_sum)
        pos_vectors_toplot.append(pos_vector)

        sentence_titles.append(GetTitle(filename))

    for index in range(len(pos_vectors_toplot)):
        print pos_vectors_toplot[index]

    # 3. Create vertical POS vectors for the tiled plot
    pos_verticles = []
    for index in range(len(spacy_pos_order)):
        current_pos_list = []
        for index2 in range(len(pos_vectors_toplot)):
            current_pos_list.append(pos_vectors_toplot[index2][index])
        pos_verticles.append(current_pos_list)    

    # 4. Create traces for the plot
    trace_list = []
    for index in range(len(spacy_pos_order)):
        
        if spacy_pos_order[index] not in p_pos2ignore:

            color_list = [possible_colors_rgb[index]] * (len(sentence_titles))

            trace = go.Bar(
                y = pos_verticles[index],
                x = range(1,len(sentence_titles)),
                name = "{0}".format(spacy_pos_order[index]),
                orientation = "v",
                marker=(dict(color=color_list))
            )            
            trace_list.append(trace)    

    # 5. Create layout and figure objects
    layout = go.Layout(xaxis=dict(autotick=False,
                                  dtick=2,
                                  tickfont=dict(size=10, color="black")),
                       yaxis=dict(tickfont=dict(size=10, color="black")))
    fig = go.Figure(data=trace_list, layout=layout)
    fig = tools.make_subplots(rows=p_rows, cols=p_cols, subplot_titles=tuple(pos_order_wo_ignore))
    current_trace = 0
    for rindex in range(p_rows):
        for cindex in range(p_cols):
            fig.append_trace(trace_list[current_trace], rindex + 1, cindex + 1)
            current_trace += 1    

    # 6. Plot the graph
    py.plot(fig, filename=p_descriptor) 

# 3c. Compare Group of Sentences POS to another Group of Sentences POS
def PlotCompareGroupToGroup(p_first_group, p_second_group, p_first_id, p_second_id, p_pos2ignore=[]):

    root_folder = "/Users/PeregrinePickle/Documents/School/New York University/Seminars/Melville/Presentation/"
    pmf_counts_folder = "output/sentence_bysection_pos_counts/"

    # Calculate and normalize the average of the first group
    first_avg_pos = CalculateAvgPOS(root_folder + pmf_counts_folder, p_first_group)
    first_sum = sum(first_avg_pos)
    first_norm = np.array(first_avg_pos) / float(first_sum)    

    # Calculate and normalize the average of the second group
    second_avg_pos = CalculateAvgPOS(root_folder + pmf_counts_folder, p_second_group)
    second_sum = sum(second_avg_pos)
    second_norm = np.array(second_avg_pos) / float(second_sum)
    
    # Differences between the first and second group
    diff_vector = first_norm - second_norm

    # Plot vertical bar plot (with pos/neg values)
    data = [go.Bar(x=spacy_pos_order, y=diff_vector.tolist(), marker=(dict(color=possible_colors_rgb)))]
    py.plot(data, filename="comp_group_{0}_to_group_{1}".format(p_first_id, p_second_id))

# 3d. Plot Bulkington-Queequeg groups in histogram across the novel's sentences
def PlotNovelHistogram():

    group_traces = []
    for bg in bulkington_groups:
        x0 = [0] * sentence_count
        sent_index = 0

        for index in range(1,3):
            for index2 in range(len(section_dict[str(index)])):
                if section_dict[str(index)][index2]["cluster"] == bg:
                    x0[sent_index] = sum(section_dict[str(index)][index2]["counts"])
                sent_index += 1

        for index in range(4, len(section_dict)):
            for index2 in range(len(section_dict[str(index)])):
                if section_dict[str(index)][index2]["cluster"] == bg:
                    x0[sent_index] = sum(section_dict[str(index)][index2]["counts"])
                sent_index += 1

        trace = go.Histogram(y=x0,opacity=0.75)
        group_traces.append(trace)
    
    layout = go.Layout(barmode='overlay')
    fig = go.Figure(data=group_traces, layout=layout)
    py.plot(fig, filename='overlaid histogram')    

# 3e. Plot instances of Bulkington and Queequeg "comrade" sentences
def PlotBulkingtonQueequegComrades():

    pass


def main():

    # 0. Populate the section and cluster dictionaries
    BuildGlobalDictsAndLists()

    # 1. Build POS profile vectors
    DeterminePOSProfileVectors(root_folder + pmf_counts_folder, counts_json_filenames, cluster_filename_dict)

    # 2. Get list of all Bulkington-Queequeg sentences
    GetAllBulkingtonQueequegSentences()

    # 3. Plots

    # a. PlotSimilarPoemsPOSTiled(29, 9, 3, 4, ["NUM", "INTJ", "X", "SYM"])

    # b. Select sentences to plot based on research question
    # bulkington_sentence_filenames = ["md_mobydick_26_chapter23_2_counts.json",
    #                                  "md_mobydick_26_chapter23_5_counts.json",
    #                                  "md_mobydick_6_chapter3_82_counts.json"]

    # queequeg_sentence_filenames = ["md_mobydick_26_chapter23_1_counts.json",
    #                                "md_mobydick_26_chapter23_10_counts.json",
    #                                "md_mobydick_26_chapter23_16_counts.json",
    #                                "md_mobydick_26_chapter23_2_counts.json",
    #                                "md_mobydick_26_chapter23_5_counts.json",
    #                                "md_mobydick_6_chapter3_82_counts.json",
    #                                "md_mobydick_6_chapter3_83_counts.json",
    #                                "md_mobydick_6_chapter3_84_counts.json"]

    # all_filenames = []
    # all_filenames.extend(bulkington_sentence_filenames)
    # all_filenames.extend(queequeg_sentence_filenames)

    # PlotSentencesPOSTiled(all_filenames, section_dict, 3, 4, "bulk_vs_queeq_cid_50_230_354", ["NUM", "X", "SYM", "INTJ"])

    # c. Plotting sentences for groups 50, 230, 232, and 354
    # PlotBulkingtonQueequegGroupComparisons()

    # d. Plot Bulkington-Queequeg groups in histogram across the novel's sentences
    # PlotNovelHistogram()

    global bg_set
    global qg_set
    global qfg_set
    global allg_set
    global qnfg_set
    global bq_intersection_set
    global chapter_indices

    # print "bg_set: {0}".format(bg_set)
    # print "================================================"
    # print "qg_set: {0}".format(qg_set)
    # print "================================================"
    # print "allg_set: {0}".format(allg_set)

    groups_not_bulkington = list(allg_set - bg_set)
    groups_not_queequeg = list(allg_set - qg_set)
    groups_not_queequeg_comrade = list(qg_set - qfg_set)
    queequeg_not_comrade_sentences = list(set(queequeg_sentences) - set(queequeg_comrade_sentences))
    qnfg_set = []
    comrade_total_ch_count = 21
    notcomrade_total_ch_count = 114

    # print "Unique Bulkington groups: {0}".format(groups_not_bulkington)
    # print "================================================"
    # print "Unique Queequeg groups: {0}".format(groups_not_queequeg)

    print "Queequeg comrade groups: {0}".format(qfg_set)
    print "Queequeg comrade group count: {0}".format(len(list(qfg_set)))
    print "Queequeg comrade sentence count: {0}".format(len(queequeg_comrade_sentences))
    print "Queequeg comrade sentence to group ratio: {0}".format(float(len(queequeg_comrade_sentences)) / float(len(list(qfg_set))))
    
    print "================================================"
    
    print "Queequeg not comrade groups: {0}".format(groups_not_queequeg_comrade)
    print "Queequeg not comrade group count: {0}".format(len(list(groups_not_queequeg_comrade)))
    print "Queequeg not comrade sentence count: {0}".format(len(queequeg_not_comrade_sentences))
    print "Queequeg not comrade sentence to group ratio: {0}".format(float(len(queequeg_not_comrade_sentences)) / float(len(list(groups_not_queequeg_comrade))))

    print "================================================"

    print "Queequeg comrade to not comrade sentence ratio: {0}".format(float(len(queequeg_comrade_sentences)) / float(len(queequeg_not_comrade_sentences)))
    chdict = []
    for sentence_name in queequeg_comrade_sentences:
        chname = GetChapter(sentence_name)
        if chname not in chdict:
            chdict.append(chname)
    fch_count = len(chdict)
    chdict = []
    for sentence_name in queequeg_not_comrade_sentences:
        chname = GetChapter(sentence_name)
        if chname not in chdict:
            chdict.append(chname)    
    nfch_count = len(chdict)
    print "Queequeg comrade to not comrade sentence ratio (adjusted by chapter count): {0}".format((fch_count * float(len(queequeg_comrade_sentences)))/ (nfch_count * float(len(queequeg_not_comrade_sentences))))
    print "Queequeg comrade chapters featured/not featured ratio: {0}".format(float(fch_count) / comrade_total_ch_count)
    print "Queequeg not comrade chapters featured/not featured ratio: {0}".format(float(nfch_count) / notcomrade_total_ch_count)
    
    print "================================================"

    print "Queequeg comrade / not comrade intersection: {0}".format(qfg_set.intersection(qnfg_set))

    print "================================================"
    
    print "Bulkington groups: {0}".format(bg_set)
    print "Bulkington group count: {0}".format(len(list(bg_set)))
    print "Bulkington sentence count: {0}".format(len(bulkington_sentences))
    print "Bulkington sentence to group ratio: {0}".format(float(len(bulkington_sentences)) / float(len(list(bg_set))))

    print "================================================"

    print "Bulkington chapters featured/not featured ratio: {0}".format(float(2.0) / float(135.0))

    print "================================================"

    bqf_intersection = list(qfg_set.intersection(bg_set))
    bqnf_intersection = list(set(groups_not_queequeg_comrade).intersection(bg_set))
    print "Bulkington groups in Queequeg comrade chapters: {0}".format(bqf_intersection)
    print "Bulkington groups in Queequeg not comrade chapters: {0}".format(bqnf_intersection)
    print "Bulkington group count in Queequeg comrade chapters: {0}".format(len(list(bqf_intersection)))
    print "Bulkington group count in Queequeg not comrade chapters: {0}".format(len(list(bqnf_intersection)))


    # Four traces for histogram plot of all sentences
    # 1. bulkington comrade 
    #    - all MD sentences in groups from bulkington sentences in ch. 3
    # 2. bulkington-queequeg comrade overlap
    #    - all MD sentences in groups from queequeg sentences through ch. 21
    # 3. bulkington truthseeker 
    #    - all MD sentences in groups from bulkington sentences in ch. 23
    # 4. queequeg harpooneer
    #    - all MD sentences in groups from queequeg sentences ch 22 - 135    
    trace_info = { "bulkington_comrade": {},
                   "bq_comrade_overlap": {},
                   "bulkington_truthseeker": {},
                   "queequeg_harpooneer": {},
                   "bq_intersection": {},
                   "queequeg_comrade": {},
                   "queequeg_overlap": {} }
    trace_info["bulkington_comrade"]["data"] = [0] * total_chapters
    trace_info["bulkington_comrade"]["groups"] = []
    trace_info["bq_comrade_overlap"]["data"] = [0] * total_chapters
    trace_info["bq_comrade_overlap"]["groups"] = []
    trace_info["bulkington_truthseeker"]["data"] = [0] * total_chapters
    trace_info["bulkington_truthseeker"]["groups"] = []
    trace_info["queequeg_harpooneer"]["data"] = [0] * total_chapters
    trace_info["queequeg_harpooneer"]["groups"] = []
    trace_info["bq_intersection"]["data"] = [0] * total_chapters
    trace_info["bq_intersection"]["groups"] = []
    trace_info["queequeg_comrade"]["data"] = [0] * total_chapters
    trace_info["queequeg_comrade"]["groups"] = []
    trace_info["queequeg_overlap"]["data"] = [0] * total_chapters
    trace_info["queequeg_overlap"]["groups"] = []

    sentences_being_looked_at = []
    sentences_being_looked_at.extend(bulkington_sentences)
    sentences_being_looked_at.extend(queequeg_sentences)
    

    # Queequeg comrade and harpooner sentences
    for sentence in queequeg_sentences:

        current_chapter = int(GetChapter(sentence))

        if current_chapter <= 21: # Comrade sentences
            trace_info["queequeg_comrade"]["groups"].append(filename_cluster_dict[sentence])
            trace_info["queequeg_comrade"]["data"][current_chapter - 1] += 1
        else: # Harpooneer sentences
            trace_info["queequeg_harpooneer"]["groups"].append(filename_cluster_dict[sentence])
            trace_info["queequeg_harpooneer"]["data"][current_chapter - 1] += 1

    queequeg_overlap_set = list(set(trace_info["queequeg_comrade"]["groups"]).intersection(set(trace_info["queequeg_harpooneer"]["groups"])))
    # print "Queequeg overlap set: {0}".format(queequeg_overlap_set)
    # print "Queequeg sentence count: {0}".format(len(queequeg_sentences))
    # if True:
    #     return

    # Queequeg comrade and harpooner overlap sentences
    for sentence in queequeg_sentences:

        current_chapter = int(GetChapter(sentence))            

        if filename_cluster_dict[sentence] in queequeg_overlap_set:
            trace_info["queequeg_overlap"]["groups"].append(filename_cluster_dict[sentence])
            trace_info["queequeg_overlap"]["data"][current_chapter - 1] += 1

    trace_info["queequeg_comrade"]["groups"] = list(set(trace_info["queequeg_comrade"]["groups"]))

    # Test this group is it 13 or 47?
    trace_info["queequeg_harpooneer"]["groups"] = list(set(trace_info["queequeg_harpooneer"]["groups"]))
    trace_info["queequeg_overlap"]["groups"] = list(set(trace_info["queequeg_overlap"]["groups"]))

    queequeg_harpooneer_sentences = list(set(queequeg_sentences) - set(queequeg_comrade_sentences))

    print "\n==========================================================="
    print "Queequeg as Comrade ======================================="
    print "Queequeg comrade POS pattern count: {0}".format(len(list(qfg_set)))
    print "Queequeg comrade sentence count: {0}".format(len(queequeg_comrade_sentences))
    print "Queequeg comrade sentence to group ratio: {0}".format(float(len(queequeg_comrade_sentences)) / float(len(list(qfg_set))))
    print "Queequeg comrade chapters featured/not featured ratio: {0}".format(float(fch_count) / comrade_total_ch_count)
    print ""
    print "==========================================================="
    print "Queequeg as Harpooneer ===================================="
    print "Queequeg harpooneer POS pattern count: {0}".format(len(trace_info["queequeg_harpooneer"]["groups"]))
    print "Queequeg harpooner sentence count: {0}".format(len(queequeg_not_comrade_sentences))
    print "Queequeg harpooneer sentence to group ratio: {0}".format(float(len(queequeg_not_comrade_sentences)) / float(len(list(groups_not_queequeg_comrade))))
    print "Queequeg harpooneer chapters featured/not featured ratio: {0}".format(float(nfch_count) / notcomrade_total_ch_count)
    print ""

    if True:
        return

    # all_traces = []
    # all_traces.append(go.Bar(name="queequeg_comrade", x=chapter_indices, y=trace_info["queequeg_comrade"]["data"]))
    # all_traces.append(go.Bar(name="queequeg_harpooneer", x=chapter_indices, y=trace_info["queequeg_harpooneer"]["data"]))
    # all_traces.append(go.Bar(name="queequeg_overlap", x=chapter_indices, y=trace_info["queequeg_overlap"]["data"]))
    # layout = go.Layout(barmode="group")
    # fig = go.Figure(data=all_traces, layout=layout)
    # py.plot(fig, filename='comrade_and_harpooneer')

    # if True:
    #     return    

    # Bulkington and Queequeg comrade overlap sentences
    for sentence in sentences_being_looked_at:

        current_chapter = int(GetChapter(sentence))

        if current_chapter <= 21: # Implicitly excludes Bulkington in Chapter 23
            if sentence in bulkington_sentences:
                trace_info["bulkington_comrade"]["groups"].append(filename_cluster_dict[sentence])
                trace_info["bulkington_comrade"]["data"][current_chapter - 1] += 1
            if sentence in queequeg_sentences:
                trace_info["queequeg_comrade"]["groups"].append(filename_cluster_dict[sentence])
                trace_info["queequeg_comrade"]["data"][current_chapter - 1] += 1
            if filename_cluster_dict[sentence] in bq_intersection_set:
                trace_info["bq_comrade_overlap"]["groups"].append(filename_cluster_dict[sentence])
                trace_info["bq_comrade_overlap"]["data"][current_chapter - 1] += 1

    trace_info["bulkington_comrade"]["groups"] = list(set(trace_info["bulkington_comrade"]["groups"]))
    trace_info["queequeg_comrade"]["groups"] = list(set(trace_info["queequeg_comrade"]["groups"]))
    trace_info["bq_comrade_overlap"]["groups"] = list(set(trace_info["bq_comrade_overlap"]["groups"]))

    print "\n==========================================================="
    print "Bulkington as Comrade ====================================="
    print "Bulkington comrade POS pattern count: {0}".format(len(trace_info["bulkington_comrade"]["groups"]))
    print "Bulkington comrade sentence count: {0}".format(sum(trace_info["bulkington_comrade"]["data"]))
    print "Bulkington comrade sentence to group ratio: {0}".format(float(sum(trace_info["bulkington_comrade"]["data"])) / float(len(trace_info["bulkington_comrade"]["groups"])))
    print ""
    print "==========================================================="
    print "Bulkington as Truthseeker ================================="
    bt_group_count = len(list(bg_set)) - len(trace_info["bulkington_comrade"]["groups"])
    bt_sentence_count = len(bulkington_sentences) - sum(trace_info["bulkington_comrade"]["data"])
    print "Bulkington truthseeker POS pattern count: {0}".format(bt_group_count)
    print "Bulkington truthseeker sentence count: {0}".format(bt_sentence_count)
    print "Bulkington truthseeker sentence to group ratio: {0}".format(float(bt_sentence_count) / float(bt_group_count))
    print ""
    print "==========================================================="
    print "Bulkington POS in Queequeg Chapters ======================="
    print "Bulkington POS patterns in Queequeg as Comrade chapters: {0}".format(len(list(bqf_intersection)))
    print "Bulkington POS patterns in Queequeg as Harpooneer chapters: {0}".format(len(list(bqnf_intersection)))
    print ""

    if True:
        return

    all_traces = []
    all_traces.append(go.Bar(name="bulkington_comrade", x=chapter_indices, y=trace_info["bulkington_comrade"]["data"]))
    all_traces.append(go.Bar(name="queequeg_comrade", x=chapter_indices, y=trace_info["queequeg_comrade"]["data"]))
    all_traces.append(go.Bar(name="bq_comrade_overlap", x=chapter_indices, y=trace_info["bq_comrade_overlap"]["data"]))
    layout = go.Layout(barmode="group")
    fig = go.Figure(data=all_traces, layout=layout)
    py.plot(fig, filename='bq_comrades')

    if True:
        return




    # Queequeg comrade and Queequeg harpooneer sentences


    sentences_being_looked_at = []
    for sentence in all_sentences:
        current_chapter = GetChapter(sentence)
        if "3" == current_chapter and sentence in bulkington_sentences:
            if filename_cluster_dict[sentence] not in trace_info["bulkington_comrade"]["groups"]:
                trace_info["bulkington_comrade"]["groups"].append(filename_cluster_dict[sentence])
        elif int(current_chapter) <= 21 and sentence in queequeg_sentences:
            if filename_cluster_dict[sentence] not in trace_info["queequeg_comrade"]["groups"]:
                trace_info["queequeg_comrade"]["groups"].append(filename_cluster_dict[sentence])

        # NOTE this should really be bq intersection of comrade groups!
        elif filename_cluster_dict[sentence] in bq_intersection_set:
            if filename_cluster_dict[sentence] not in trace_info["bq_intersection"]["groups"]:
                trace_info["bq_intersection"]["groups"].append(filename_cluster_dict[sentence])
    current_chapter = 1
    for index in range(1, len(section_dict.keys()) + 1):
        if 3 == index:
            continue
        for index2 in range(len(section_dict[str(index)])):
            chapter = GetChapter(section_dict[str(index)][index2]["file"])
            if "NA" == chapter:
                break
            if chapter != current_chapter:
                current_chapter = int(chapter)
            if section_dict[str(index)][index2]["cluster"] in trace_info["bulkington_comrade"]["groups"]:
                trace_info["bulkington_comrade"]["data"][current_chapter - 1] += 1
            if section_dict[str(index)][index2]["cluster"] in trace_info["queequeg_comrade"]["groups"]:
                trace_info["queequeg_comrade"]["data"][current_chapter - 1] += 1
            if section_dict[str(index)][index2]["cluster"] in trace_info["bq_intersection"]["groups"]:
                trace_info["bq_intersection"]["data"][current_chapter - 1] += 1




    all_traces = []
    all_traces.append(go.Bar(name="bulkington_comrade", x=chapter_indices, y=trace_info["bulkington_comrade"]["data"]))
    all_traces.append(go.Bar(name="queequeg_comrade", x=chapter_indices, y=trace_info["queequeg_comrade"]["data"]))
    all_traces.append(go.Bar(name="bq_intersection", x=chapter_indices, y=trace_info["bq_intersection"]["data"]))
    layout = go.Layout(barmode="group")
    fig = go.Figure(data=all_traces, layout=layout)
    py.plot(fig, filename='grouped-bar')

    if True:
        return

    # Traces 1 and 3

    # Get groups for the sentences
    for sentence in bulkington_sentences:
    # for sentence in all_sentences:
    # for sentence in sentences_being_looked_at:
        if filename_cluster_dict[sentence] in bq_intersection_set:
            current_chapter = GetChapter(sentence)
            if "3" == current_chapter:
                if filename_cluster_dict[sentence] not in trace_info["bulkington_comrade"]["groups"]:
                    trace_info["bulkington_comrade"]["groups"].append(filename_cluster_dict[sentence])
            elif "23" == current_chapter:
                if filename_cluster_dict[sentence] not in trace_info["bulkington_truthseeker"]["groups"]:
                    trace_info["bulkington_truthseeker"]["groups"].append(filename_cluster_dict[sentence])
    
    # Fill out histogram data for each trace
    current_chapter = 1
    for index in range(1, len(section_dict.keys()) + 1):
        if 3 == index:
            continue
        for index2 in range(len(section_dict[str(index)])):
            chapter = GetChapter(section_dict[str(index)][index2]["file"])
            if "NA" == chapter:
                break
            if chapter != current_chapter:
                current_chapter = int(chapter)
            if section_dict[str(index)][index2]["file"] in bulkington_sentences:
            # if section_dict[str(index)][index2]["file"] in sentences_being_looked_at:
            # if section_dict[str(index)][index2]["file"] in all_sentences:
                if section_dict[str(index)][index2]["cluster"] in trace_info["bulkington_comrade"]["groups"]:
                    trace_info["bulkington_comrade"]["data"][current_chapter - 1] += 1
                elif section_dict[str(index)][index2]["cluster"] in trace_info["bulkington_truthseeker"]["groups"]:
                    trace_info["bulkington_truthseeker"]["data"][current_chapter - 1] += 1


    # Traces 2 and 4

    # Get groups for the sentences
    for sentence in queequeg_sentences:
    # for sentence in all_sentences:
        if filename_cluster_dict[sentence] in bq_intersection_set:
            current_chapter = GetChapter(sentence)
            if int(current_chapter) <= 21:
                if filename_cluster_dict[sentence] not in trace_info["bq_comrade_overlap"]["groups"]:
                    trace_info["bq_comrade_overlap"]["groups"].append(filename_cluster_dict[sentence])
            else: # int(current_chapter) > 21:
                if filename_cluster_dict[sentence] not in trace_info["queequeg_harpooneer"]["groups"]:
                    trace_info["queequeg_harpooneer"]["groups"].append(filename_cluster_dict[sentence])
    
    # Fill out histogram data for each trace
    current_chapter = 1
    for index in range(1, len(section_dict.keys()) + 1):
        if 3 == index:
            continue
        for index2 in range(len(section_dict[str(index)])):
            chapter = GetChapter(section_dict[str(index)][index2]["file"])
            if "NA" == chapter:
                break
            if chapter != current_chapter:
                current_chapter = int(chapter)
            if section_dict[str(index)][index2]["file"] in queequeg_sentences:
            # if section_dict[str(index)][index2]["file"] in sentences_being_looked_at:
            # if section_dict[str(index)][index2]["file"] in all_sentences:
                if section_dict[str(index)][index2]["cluster"] in trace_info["bq_comrade_overlap"]["groups"]:
                    trace_info["bq_comrade_overlap"]["data"][current_chapter - 1] += 1
                elif section_dict[str(index)][index2]["cluster"] in trace_info["queequeg_harpooneer"]["groups"]:
                    trace_info["queequeg_harpooneer"]["data"][current_chapter - 1] += 1  


    print sum(trace_info["bulkington_comrade"]["data"])
    print sum(trace_info["bulkington_truthseeker"]["data"])
    print sum(trace_info["bq_comrade_overlap"]["data"])
    print sum(trace_info["queequeg_harpooneer"]["data"])

    chapter_indices = []
    for index in range(total_chapters):
        chapter_indices.append(str(index + 1))

    all_traces = []
    all_traces.append(go.Bar(name="bulkington_comrade", x=chapter_indices, y=trace_info["bulkington_comrade"]["data"]))
    all_traces.append(go.Bar(name="bulkington_truthseeker", x=chapter_indices, y=trace_info["bulkington_truthseeker"]["data"]))
    all_traces.append(go.Bar(name="bq_comrade_overlap", x=chapter_indices, y=trace_info["bq_comrade_overlap"]["data"]))
    all_traces.append(go.Bar(name="queequeg_harpooneer", x=chapter_indices, y=trace_info["queequeg_harpooneer"]["data"]))  
    layout = go.Layout(barmode="group")
    fig = go.Figure(data=all_traces, layout=layout)
    py.plot(fig, filename='grouped-bar')

    # Plot traces
    # all_traces = []
    # all_traces.append(go.Histogram(
    #     x=trace_info["bulkington_comrade"]["data"],
    #     name="bulkington_comrade",
    #     opacity=0.5,
    #     histnorm="count",
    #     autobinx=False, 
    #     xbins={ "start": 0,
    #              "end": 9196,
    #              "size": 1 } ))
    # all_traces.append(go.Histogram(
    #     x=trace_info["bulkington_truthseeker"]["data"],         
    #     name="bulkington_truthseeker",
    #     opacity=0.5,
    #     histnorm="count",
    #     autobinx=False, 
    #     xbins={ "start": 0,
    #              "end": 9196,
    #              "size": 1 } ))
    # all_traces.append(go.Histogram(
    #     x=trace_info["bq_comrade_overlap"]["data"],  
    #     name="bq_comrade_overlap",       
    #     opacity=0.5,
    #     histnorm="count",
    #     autobinx=False, 
    #     xbins={ "start": 0,
    #              "end": 9196,
    #              "size": 1 } ))
    # all_traces.append(go.Histogram(
    #     x=trace_info["queequeg_harpooneer"]["data"],         
    #     name="queequeg_harpooneer",  
    #     opacity=0.5,
    #     histnorm="count",
    #     autobinx=False, 
    #     xbins={ "start": 0,
    #              "end": 9196,
    #              "size": 1 } ))
    # layout = go.Layout(barmode='overlay')
    # fig = go.Figure(data=all_traces, layout=layout)
    # py.plot(fig, filename='overlaid histogram')    





if "__main__" == __name__:
    main()
