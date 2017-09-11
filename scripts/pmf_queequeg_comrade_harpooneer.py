from collections import Counter
import glob
import json
import math
import os

from project_defines import UnnecessaryDuplicates
from project_defines import UD_PMFObject
from spacy_meta import spacy_pos_order
from utils_jensen_shannon import jensen_shannon_distance

import numpy as np
# from urlparse import urlparse
import plotly.plotly as py
import plotly.graph_objs as go



possible_colors_rgb = ["rgb(0,174,239)", "rgb(0,114,188)",   "rgb(46,49,146)",  "rgb(146,39,143)",
                       "rgb(236,0,140)", "rgb(237,28,36)",   "rgb(247,148,30)", "rgb(255,242,0)",
                       "rgb(141,198,63)","rgb(0,166,181)",   "rgb(186,210,237)","rgb(209,145,192)",
                       "rgb(135,129,189)","rgb(134,166,178)","rgb(122,204,200)","rgb(200,221,105)"]


names_of_interest = ["Queequeg"]
def map_with_names_of_interest():

    my_map = {}
    for name in names_of_interest:
        my_map[name] = {}
    return my_map


def CalculateAvgPOS(p_folder, p_json_filenames):

    # Retrieve POS vectos from given files
    pos_vectors = []
    for filename in p_json_filenames:
        with open(p_folder + filename, "r") as input_file:
            data = input_file.read()
            json_file = json.loads(data)
            current_vector = []
            for index in range(len(spacy_pos_order)):
                current_vector.append(json_file["pos"][spacy_pos_order[index]])
            pos_vectors.append(current_vector)

    # print "My POS Vectors:"
    # print pos_vectors

    # Calculate and return the average POS
    avg_pos_vector = [0.0] * len(spacy_pos_order)
    for v in pos_vectors:
        for index in range(len(spacy_pos_order)):
            avg_pos_vector[index] += v[index]
    for index in range(len(spacy_pos_order)):
        avg_pos_vector[index] /= float(len(pos_vectors))

    # print "My Average Vector:"
    # print avg_pos_vector
    # print "========================"

    return avg_pos_vector


def CalculateAvgPOSOfVectors(p_pos_vectors):

    # Calculate and return the average POS
    avg_pos_vector = [0.0] * len(spacy_pos_order)
    for v in p_pos_vectors:
        for index in range(len(spacy_pos_order)):
            avg_pos_vector[index] += v[index]
    for index in range(len(spacy_pos_order)):
        avg_pos_vector[index] /= float(len(p_pos_vectors))

    return avg_pos_vector



def FindClosestVectors(p_test_vector, p_vector_list):

    distance_list = []
    for index in range(len(p_vector_list)):
        distance_list.append(jensen_shannon_distance(p_test_vector, p_vector_list[index]))
    return distance_list.index(min(distance_list))


def GetCountFilenames(p_pmf_objects):

    filenames = []
    for obj in p_pmf_objects:
        filenames.append(obj.filename().strip("txt").strip(".") + "_counts.json")
    return filenames

def TransformTxtMultToCountFilenames(p_txt_filenames):

    return [TransformTxtToCountFilename(txt_filename) for txt_filename in p_txt_filenames]

def TransformTxtToCountFilename(p_txt_filename):

    return p_txt_filename.strip("txt").strip(".") + "_counts.json"


def GetClosestSentenceToAbsOfVector(p_vector, p_pmf_objects):

    # Calculate and normalize the average of the first group
    for index in range(len(p_vector)):
        p_vector[index] = abs(p_vector[index])

    distances = []
    for obj in p_pmf_objects:
        current_vector = []
        for index in range(len(spacy_pos_order)):
            current_vector.append(obj.pos()["pos"][spacy_pos_order[index]])        
        distances.append(jensen_shannon_distance(p_vector, current_vector))
    
    return p_pmf_objects[distances.index(min(distances))].sentence()


def GetPOSVectors(p_pmf_objects):

    pos_vectors = []
    for obj in p_pmf_objects:
        current_vector = []
        for index in range(len(spacy_pos_order)):
            current_vector.append(obj.pos()["pos"][spacy_pos_order[index]])
        pos_vectors.append(current_vector)
    return pos_vectors


def GetPMFPOSVectors(p_pmf_objects, p_group2sent_map):

    # Find all groups from the given objects
    my_groups = []
    for obj in p_pmf_objects:
        my_groups.append(obj.group())
    my_groups = list(set(my_groups))

    # Look up sentences for each group and find their POS for PMF profile calculation
    pos_vector_map = {}
    for group in my_groups:
        pos_vector_map[group] = []
        for sent_filename in p_group2sent_map[group]:
            with open(UnnecessaryDuplicates.pos_path + TransformTxtToCountFilename(sent_filename), "rU") as counts_file:
                json_data = json.loads(counts_file.read())
                current_vector = []
                for index in range(len(spacy_pos_order)):
                    current_vector.append(json_data["pos"][spacy_pos_order[index]])
                pos_vector_map[group].append(current_vector)

    # Calculate all PMF-POS profile vectors
    profile_vector_map = {}
    for group in my_groups:
        profile_vector_map[group] = [0] * len(spacy_pos_order)
        for index in range(len(pos_vector_map[group])):
            for pos_index in range(len(spacy_pos_order)):
                profile_vector_map[group][pos_index] += pos_vector_map[group][index][pos_index]
        for pos_index in range(len(spacy_pos_order)):
            profile_vector_map[group][pos_index] /= float(len(pos_vector_map[group]))

    return profile_vector_map


# Plot Comparison Group of Sentences POS to another Group of Sentences POS
def PlotCompareGroupToGroup(p_first_group_vector, p_second_group_vector, p_first_id, p_second_id, p_pos2ignore=[]):

    root_folder = "/Users/PeregrinePickle/Documents/School/New York University/Seminars/Melville/Presentation/"
    pmf_counts_folder = "output/sentence_bysection_pos_counts/"

    # Calculate and normalize the average of the first group
    first_sum = sum(p_first_group_vector)
    first_norm = np.array(p_first_group_vector) / float(first_sum)    

    # Calculate and normalize the average of the second group
    second_sum = sum(p_second_group_vector)
    second_norm = np.array(p_second_group_vector) / float(second_sum)
    
    # Differences between the first and second group
    diff_vector = first_norm - second_norm

    # Plot vertical bar plot (with pos/neg values)
    data = [go.Bar(x=spacy_pos_order, y=diff_vector.tolist(), marker=(dict(color=possible_colors_rgb)))]
    py.plot(data, filename="comp_group_{0}_to_group_{1}".format(p_first_id, p_second_id))

# Plot Group of Sentences POS
def PlotSentenceGroup(p_first_group, p_second_group, p_first_id, p_second_id, p_pos2ignore=[]):

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

def PlotPOSVector(p_pos_vector, p_name):

    # Plot vertical bar plot (with pos/neg values)
    data = [go.Bar(x=spacy_pos_order, y=p_pos_vector, marker=(dict(color=possible_colors_rgb)))]
    py.plot(data, filename="pos_vector_{0}".format(p_name))

def main():

    # This script attempts to determine the stylistic differences in the sentences used
    # by Melville when referring to Queequeg in two separate roles hypothesized by the Harrison Hayford
    # in his essay, "Unnecessary Duplicates." To do so we look at sentences grouped by part-of-speech counts
    # patterning under a probabilistic matrix factorization model of the sentences of all of "Moby-Dick; or, The Whale"

    # 1. Look for the names of interest (e.g. Queequeg) in the split sentence txt files

    # Indices of files_of_interest and text_of_interest will correspond
    ud_pmfobjects_map = {"Queequeg":[]}
    files_of_interest = map_with_names_of_interest()
    for full_filepath in glob.glob(UnnecessaryDuplicates.sentence_path + "*.txt"):

        sentence_filename = os.path.basename(full_filepath)
        with open(full_filepath, "rU") as input_file:
            
            data = input_file.read()
            for name in files_of_interest.keys():
                if name in data:

                    # PMF objects (initialize group number with 0, blank POS vector)
                    new_pmfobject = UD_PMFObject(sentence_filename, data.replace("\n", " "), 0, [])
                    ud_pmfobjects_map[name].append(new_pmfobject)

                    # Save a reference to the new object in map keyed on filename
                    files_of_interest[name][sentence_filename] = new_pmfobject


    # 2. Read the PMF model of the sentences
    group2sent_map = {}
    sent2group_map = {}
    name_groups = {}
    with open(UnnecessaryDuplicates.pmf_path + UnnecessaryDuplicates.pmf_model_csv_filename, "rU") as pmf_output_file:
        
        csv_lines = pmf_output_file.readlines()
        for line in csv_lines:

            sent_filename, sent_group = line.strip().split(",")
            for name in files_of_interest.keys():
                
                if sent_filename in files_of_interest[name]:

                    # Save UD_PMFObject groups here
                    files_of_interest[name][sent_filename].set_group(sent_group)

                    # Save groups for each name being looked for
                    if name not in name_groups:
                        name_groups[name] = []
                    name_groups[name].append(sent_group)

                    # Create two maps to easily move between sentence files and their PMF model groups
                    if sent_filename in files_of_interest[name]:
                        sent2group_map[sent_filename] = sent_group
                        if sent_group not in group2sent_map:
                            group2sent_map[sent_group] = []
                        group2sent_map[sent_group].append(sent_filename)    

    # 3. Get PMF groups from sentences up to and including Ch. 21, and all chapters thereafter in a separate set
    queequeg_comrade_groups = []
    queequeg_comrade_objects = []
    queequeg_harpooneer_groups = []
    queequeg_harpooneer_objects = []
    for name in names_of_interest:
        for ud_pmf_object in ud_pmfobjects_map[name]:

            # If sentence is from Chapters 21 and down, NOTE: '24' is the section ID of Chapter 21
            if int(ud_pmf_object.filename_section()) <= 24:
                queequeg_comrade_groups.append(ud_pmf_object.group())
                queequeg_comrade_objects.append(ud_pmf_object)
            # Else, this sentence is from Chapters 22+
            else:
                queequeg_harpooneer_groups.append(ud_pmf_object.group())
                queequeg_harpooneer_objects.append(ud_pmf_object)

    # Determine most common groups
    # print "Comrade sentences: {0} groups: {1}".format(len(queequeg_comrade_groups), len(set(queequeg_comrade_groups)))
    # print "Harpooneer sentences: {0} groups: {1}".format(len(queequeg_harpooneer_groups), len(set(queequeg_harpooneer_groups)))
    # if True:
    #     return
    comrade_group_mode = Counter(queequeg_comrade_groups).most_common(1)[0][0]
    harpooneer_group_mode = Counter(queequeg_harpooneer_groups).most_common(1)[0][0]
    ch_combined = []
    ch_combined_set = set(queequeg_comrade_groups).intersection(set(queequeg_harpooneer_groups))
    for group in ch_combined_set:
        for cg in queequeg_comrade_groups:
            if group == cg:
                ch_combined.append(cg)
        for hg in queequeg_harpooneer_groups:
            if group == hg:
                ch_combined.append(hg)

    # print "Number of comrade sentences: {0}".format(len(queequeg_comrade_groups))
    # dist_com_sentences = set(queequeg_comrade_groups) - set(ch_combined)
    # print "Number of distinct groups: {0}".format(len(dist_com_sentences))
    # print Counter(dist_com_sentences).most_common(len(dist_com_sentences))
    # print "======================"
    # print "Number of harpooneer sentences: {0}".format(len(queequeg_harpooneer_groups))
    # dist_harp_sentences = set(queequeg_harpooneer_groups) - set(ch_combined)
    # print "Number of distinct groups: {0}".format(len(dist_harp_sentences))
    # print Counter(dist_harp_sentences).most_common(len(dist_harp_sentences))
    # print "======================"
    # print "Number of comrade/harpooneer that share groups: {0}".format(len(ch_combined))
    # print "Number of distinct groups: {0}".format(len(set(ch_combined)))
    # print Counter(ch_combined).most_common(len(ch_combined))
    # if True:
    #     return

    # NOW: List the distinct groups for comrade and for harpooneer

    ch_combined_group_mode = Counter(ch_combined).most_common(1)[0][0]

    # print comrade_group_mode
    # print harpooneer_group_mode
    # print ch_combined_group_mode
    # if True:
    #     return

    # 4. Create sets based on the gathered Queequeg PMF sentence groups
    queequeg_comrade_groupset = set(queequeg_comrade_groups)
    queequeg_harpooneer_groupset = set(queequeg_harpooneer_groups)
    intersection_comrade_harpooneer = queequeg_comrade_groupset.intersection(queequeg_harpooneer_groupset)
    unique_comrade_groupset = queequeg_comrade_groupset - intersection_comrade_harpooneer
    unique_harpooneer_groupset = queequeg_harpooneer_groupset - intersection_comrade_harpooneer



    # 5. Now that groups have been determined, re-find the sentences that are in those groups
    intersection_objs = []
    unique_comrade_objs = []
    unique_harpooneer_objs = []
    for name in names_of_interest:
        for ud_pmf_object in ud_pmfobjects_map[name]:
            if ud_pmf_object.group() in intersection_comrade_harpooneer:
                intersection_objs.append(ud_pmf_object)
            if ud_pmf_object.group() in unique_comrade_groupset:
                unique_comrade_objs.append(ud_pmf_object)
            if ud_pmf_object.group() in unique_harpooneer_groupset:
                unique_harpooneer_objs.append(ud_pmf_object)


    # print "Unique comrade sentences: {0} groups: {1}".format(len(unique_comrade_objs), len(unique_comrade_groupset))
    # print "Unique harpooneer sentences: {0} groups: {1}".format(len(unique_harpooneer_objs), len(unique_harpooneer_groupset) )

    # print "Queequeg comrade groups({0}): {1}\n====================".format(len(queequeg_comrade_groupset), queequeg_comrade_groupset)
    # print "Queequeg harpooneer groups({0}): {1}\n====================".format(len(queequeg_harpooneer_groupset), queequeg_harpooneer_groupset)
    # print "Intersection groups({0}): {1}\n====================".format(len(intersection_comrade_harpooneer), intersection_comrade_harpooneer)
    # print "Unique comrade groups({0}): {1}\n==================".format(len(unique_comrade_groupset), unique_comrade_groupset)
    # print "Unique comrade groups({0}): {1}".format(len(unique_harpooneer_groupset), unique_harpooneer_groupset)
    # if True:
    #     return
    
    # 6. Read in relevant POS json files
    for name in ud_pmfobjects_map:
        for ud_pmf_object in ud_pmfobjects_map[name]:
            with open(UnnecessaryDuplicates.pos_path + ud_pmf_object.filename().strip("txt").strip(".") + "_counts.json",
                      "rU") as pos_file:
                json_data = json.loads(pos_file.read())
                ud_pmf_object.set_pos(json_data)

    # # Find highest pronoun count in the Comrade sentences
    # pronoun_count = 0
    # my_sentence = ""
    # for index in range(len(unique_comrade_objs)):
    #     if unique_comrade_objs[index].pos()["pos"]["PRON"] > pronoun_count:
    #         pronoun_count = unique_comrade_objs[index].pos()["pos"]["PRON"]
    #         my_sentence = unique_comrade_objs[index].sentence()

    # print "Highest pronoun count in comrade sentences: {0}".format(pronoun_count)
    # print "Sentence: {0}".format(my_sentence)

    # # Find the lowest pronoun count in the Harpooneer sentences
    # pronoun_count = 1000
    # my_sentence = ""
    # for index in range(len(unique_harpooneer_objs)):
    #     if unique_harpooneer_objs[index].pos()["pos"]["PRON"] < pronoun_count:
    #         pronoun_count = unique_harpooneer_objs[index].pos()["pos"]["PRON"]
    #         my_sentence = unique_harpooneer_objs[index].sentence()

    # print "Lowest pronoun count in harpooner sentences: {0}".format(pronoun_count)
    # print "Sentence: {0}".format(my_sentence)

    # if True:
    #     return                

    # for name in ud_pmfobjects_map:
    #     for ud_pmf_object in ud_pmfobjects_map[name]:
    #         print "{0}: {1}\n====================".format(ud_pmf_object.filename(), ud_pmf_object.pos())
    # if True:
    #     return

    uc_pmf_profiles = GetPMFPOSVectors(unique_comrade_objs, group2sent_map)
    uh_pmf_profiles = GetPMFPOSVectors(unique_harpooneer_objs, group2sent_map)
    i_pmf_profiles = GetPMFPOSVectors(intersection_objs, group2sent_map)

    uc_pmf_profiles_avgpos = CalculateAvgPOSOfVectors(uc_pmf_profiles.values())
    uh_pmf_profiles_avgpos = CalculateAvgPOSOfVectors(uh_pmf_profiles.values())

    # print "Length of Comrade avg profile: {0}".format(sum(uc_pmf_profiles_avgpos))
    # print "Length of Harpooneer avg profile: {0}".format(sum(uh_pmf_profiles_avgpos))
    # if True:
    #     return

    uc_mode_pmf_profile = CalculateAvgPOS(UnnecessaryDuplicates.pos_path, TransformTxtMultToCountFilenames(group2sent_map[comrade_group_mode]))
    uh_mode_pmf_profile = CalculateAvgPOS(UnnecessaryDuplicates.pos_path, TransformTxtMultToCountFilenames(group2sent_map[harpooneer_group_mode]))
    chcombined_mode_pmf_profile = CalculateAvgPOS(UnnecessaryDuplicates.pos_path, TransformTxtMultToCountFilenames(group2sent_map[ch_combined_group_mode]))

    # print uc_mode_pmf_profile
    # if True:
    #     return

    # print uc_pmf_profiles
    # if True:
    #     return

    # 7. Get average POS vectors for each set of sentences and plot them
    comrade_avg_pos = CalculateAvgPOS(UnnecessaryDuplicates.pos_path, GetCountFilenames(unique_comrade_objs))
    harpooneer_avg_pos = CalculateAvgPOS(UnnecessaryDuplicates.pos_path, GetCountFilenames(unique_harpooneer_objs))
    intersection_avg_pos = CalculateAvgPOS(UnnecessaryDuplicates.pos_path, GetCountFilenames(intersection_objs))

    print "Comrade sentence: {0}".format(GetClosestSentenceToAbsOfVector(uc_pmf_profiles_avgpos, unique_comrade_objs))
    print "Harpooneer sentence: {0}".format(GetClosestSentenceToAbsOfVector(uh_pmf_profiles_avgpos, unique_harpooneer_objs))

    # PlotPOSVector(uc_mode_pmf_profile, "comrade_mode_pmf_profile")
    # PlotPOSVector(uh_mode_pmf_profile, "harpooneer_mode_pmf_profile")
    # PlotPOSVector(chcombined_mode_pmf_profile, "chcombined_mode_pmf_profile")
    # PlotCompareGroupToGroup(uc_mode_pmf_profile, uh_mode_pmf_profile, comrade_group_mode, harpooneer_group_mode)
    # PlotPOSVector(uc_pmf_profiles_avgpos, "unique_comrade_profileavg")
    # PlotPOSVector(uh_pmf_profiles_avgpos, "unique_harpooneer_profileavg")
    # PlotCompareGroupToGroup(uc_pmf_profiles_avgpos, uh_pmf_profiles_avgpos, "comrade_avgprof", "harp_avgprof")
    # sPlotCompareGroupToGroup(uh_pmf_profiles_avgpos, uc_pmf_profiles_avgpos, "harp_avgprof", "comrade_avgprof")
    if True:
        return

    # 8. Find closest sentences and print them out
    comrade_pos_vectors = GetPOSVectors(unique_comrade_objs)
    harpooneer_pos_vectors = GetPOSVectors(unique_harpooneer_objs)
    intersection_pos_vectors = GetPOSVectors(intersection_objs)
   
    comrade_closest_vector = FindClosestVectors(comrade_avg_pos, comrade_pos_vectors)
    harpooneer_closest_vector = FindClosestVectors(harpooneer_avg_pos, harpooneer_pos_vectors)
    intersection_closest_vector = FindClosestVectors(intersection_avg_pos, intersection_pos_vectors)
    
    # print comrade_closest_vector
    # print harpooneer_closest_vector
    # print intersection_closest_vector
    print "Most common comrade sentence: {0}\nFrom: {1}\n====================".format(unique_comrade_objs[comrade_closest_vector].sentence(),
        unique_comrade_objs[comrade_closest_vector].filename())
    print "Most common harpooneer sentence: {0}\nFrom: {1}\n====================".format(unique_harpooneer_objs[comrade_closest_vector].sentence(),
        unique_harpooneer_objs[comrade_closest_vector].filename())
    print "Most common intersection sentence: {0}\nFrom: {1}\n====================".format(intersection_objs[comrade_closest_vector].sentence(),
        intersection_objs[comrade_closest_vector].filename())

    if True:
        return

    # Plot average

    # Debug
    # for name in files_of_interest.keys():
    #     print "{0}({1}):".format(name, len(files_of_interest[name]))
    #     for fd_tuple in files_of_interest[name]:
    #         # print "{0} | {1}\n".format(fd_tuple[0], fd_tuple[1])
    #         print "{0}".format(fd_tuple[0])



    # Debug
    # print sent2group_map
    # print queequeg_groups
    # print group2sent_map
    bset = set(bulkington_groups)
    qset = set(queequeg_groups)
    groups_in_both = list(bset.intersection(qset))
    # print "Groups in both: {0}".format(list(bset.intersection(qset)))
    # print "Groups only in Bulkington: {0}".format(list(bset - qset))
    # print "Groups only in Queequeg: {0}".format(list(qset - bset))

    # Queequeg-like Bulkington sentences
    qlb_sentences = []
    # print "Queequeg-like Bulkinton sentences"
    for group in groups_in_both:
        for filename in group2sent_map[group]:
            if filename in files_of_interest["Bulkington"]:
                # print filename
                qlb_sentences.append(filename)

    # print "======================================================"

    # Bulkington-like Queequeg sentences
    blq_sentences = []
    # print "Bulkington-like Queequeg sentences"
    for group in groups_in_both:
        for filename in group2sent_map[group]:
            if filename in files_of_interest["Queequeg"]:
                # print filename                
                blq_sentences.append(filename)

    # Show text of Queequeg-like Bulkington sentences
    for td_tuple in text_of_interest["Bulkington"]:
        if td_tuple[0] in qlb_sentences:
            print "Filename: {0}\nGroup: {1}\nSentence: {2}".format(td_tuple[0], sent2group_map[td_tuple[0]], td_tuple[1].strip())
            print "======================================================"
    if True:
        return

    # Looking at groups 50, 230, 354
    looking_at = [50, 230, 354, 232]

    # for sentence in sent2group_map:
    #     if sent2group_map[sentence] == "50":
    #         print sentence
    # if True:
    #     return

    # Find Bulkington-like Queequeg sentences with these groups
    for td_tuple in text_of_interest["Queequeg"]:
        # print "group: {0} looking_at: {1}".format(sent2group_map[td_tuple[0]], looking_at)
        if int(sent2group_map[td_tuple[0]]) in looking_at:
            print "Filename: {0}\nGroup: {1}\nSentence: {2}".format(td_tuple[0], sent2group_map[td_tuple[0]], td_tuple[1].strip())
            print "======================================================"


if __name__ == "__main__":
    main()