import glob
import json

from project_defines import UnnecessaryDuplicates
from project_defines import UD_PMFObject

import plotly.plotly as py
import plotly.graph_objs as go

import numpy as np

def smoothTriangle(data, degree, dropVals=False):
    triangle=np.array(range(degree) + [degree] + range(degree)[::-1]) + 1
    smoothed=[]

    for i in range(degree, len(data) - degree * 2):
        point=data[i:i + len(triangle)] * triangle
        smoothed.append(sum(point)/sum(triangle))
    if dropVals:
        return smoothed
    smoothed=[smoothed[0]]*(degree + degree/2) + smoothed
    while len(smoothed) < len(data):
        smoothed.append(smoothed[-1])
    return smoothed


def read_pmf_groups_from_model():

    pmf_groups = {}
    with open(UnnecessaryDuplicates.pmf_path + UnnecessaryDuplicates.pmf_model_csv_filename, "rU") as pmf_file:
        csv_lines = pmf_file.readlines()
        for line in csv_lines:
            sent_filename, sent_group = line.strip().split(",")
            clean_sent_group = sent_group.strip()
            if clean_sent_group not in pmf_groups:
                pmf_groups[clean_sent_group] = []     
            pmf_groups[clean_sent_group].append(sent_filename)

    return pmf_groups


def read_pmf_objects_from_model():

    pmf_objects = []

    # Read filename, sentence, and POS counts from JSON
    # (Creates a temporary filename to object map)
    pmf_objectmap_byfilename = {}
    for full_filepath in glob.glob(UnnecessaryDuplicates.pos_path + "*.json"):
        with open(full_filepath, "rU") as pos_file:
            json_data = json.loads(pos_file.read())
            pmf_object = UD_PMFObject(json_data["filename"],
                                      json_data["full_text"].replace("\n", " "),
                                      0,
                                      json_data["pos"])
            pmf_objects.append(pmf_object)
            pmf_objectmap_byfilename[json_data["filename"]] = pmf_object

    # Find group
    with open(UnnecessaryDuplicates.pmf_path + UnnecessaryDuplicates.pmf_model_csv_filename, "rU") as pmf_file:
        csv_lines = pmf_file.readlines()
        for line in csv_lines:
            sent_filename, sent_group = line.strip().split(",")
            pmf_objectmap_byfilename[sent_filename.strip()].m_group = sent_group.strip()

    return pmf_objects


def plot_pmf_group2sentence_ratios_bysection():

    # 1. Determine a groups per section ratio

    # Read groups from the model
    pmf_groups = read_pmf_groups_from_model()

    # Get all section IDs and their respective groups into a map
    section_groups = {}
    section_group_sets = {}
    for group in pmf_groups:
        for filename in pmf_groups[group]:
            title = UD_PMFObject.get_title(filename)
            section_id = UD_PMFObject.get_section(filename)
            title_section_id = title + "_" + section_id
            if title_section_id not in section_groups:
                section_groups[title_section_id] = []
                section_group_sets[title_section_id] = []
            section_groups[title_section_id].append(group)
    for title_section_id in section_groups:
        section_group_sets[title_section_id] = list(set(section_groups[title_section_id]))

    # Calculate group / sentence ratios for each section
    section_ratios = []
    for title_section_id in section_groups:

        parts = title_section_id.split("_")
        if len(parts) > 2:
            title = parts[0] + "_" + parts[1]
            section_id = parts[2]
        else:
            title = parts[0]
            section_id = parts[1]

        section_ratios.append((title,
                               int(section_id),
                               float(len(section_group_sets[title_section_id])) / len(section_groups[title_section_id]) ))
    section_ratios = sorted(section_ratios, key=lambda x: x[1])

    # 2. Plot the ratios
    titles_for_plot = []
    ratios_for_plot = []
    for index in range(len(section_ratios)):
        titles_for_plot.append(section_ratios[index][0])
        ratios_for_plot.append(section_ratios[index][2])
    data = [go.Scatter(x=titles_for_plot, y=ratios_for_plot, mode="lines")]
    layout = go.Layout(xaxis=dict(tickangle=-45))
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename="group2sentence_ratios_mobydick")


def plot_pmf_group2sentence_ratios_deltaaverage_bysection():

    # 1. Determine a groups per section ratio

    # Read groups from the model
    pmf_groups = read_pmf_groups_from_model()

    # Get all section IDs and their respective groups into a map
    section_groups = {}
    section_group_sets = {}
    for group in pmf_groups:
        for filename in pmf_groups[group]:
            title = UD_PMFObject.get_title(filename)
            section_id = UD_PMFObject.get_section(filename)
            title_section_id = title + "_" + section_id
            if title_section_id not in section_groups:
                section_groups[title_section_id] = []
                section_group_sets[title_section_id] = []
            section_groups[title_section_id].append(group)
    for title_section_id in section_groups:
        section_group_sets[title_section_id] = list(set(section_groups[title_section_id]))

    # Calculate group / sentence ratios for each section
    section_ratios = []
    for title_section_id in section_groups:

        parts = title_section_id.split("_")
        if len(parts) > 2:
            title = parts[0] + "_" + parts[1]
            section_id = parts[2]
        else:
            title = parts[0]
            section_id = parts[1]

        section_ratios.append((title,
                               int(section_id),
                               float(len(section_group_sets[title_section_id])) / len(section_groups[title_section_id]) ))
    section_ratios = sorted(section_ratios, key=lambda x: x[1])

    # Calculate the section ratio average
    ratio_sum = 0
    for index in range(len(section_ratios)):
        ratio_sum += section_ratios[index][2]
    ratio_avg = ratio_sum / float(len(section_ratios))

    # Section ratio deltas for plotting
    section_ratio_deltas = []
    for index in range(len(section_ratios)):
        section_ratio_deltas.append(section_ratios[index][2] - ratio_avg)

    # 2. Plot the ratios
    titles_for_plot = []
    ratios_for_plot = []
    for index in range(len(section_ratios)):
        titles_for_plot.append(section_ratios[index][0])
        ratios_for_plot.append(section_ratio_deltas[index])
    # data = [go.Scatter(x=titles_for_plot, y=ratios_for_plot, mode="lines")]
    data = [go.Scatter(x=titles_for_plot, y=smoothTriangle(ratios_for_plot, 1), mode="lines")]
    layout = go.Layout(xaxis=dict(tickangle=-45))
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename="group2sentence_ratios_deltaaverage_mobydick")

    
def main():

    plot_pmf_group2sentence_ratios_deltaaverage_bysection()

    # pmf_objects = read_pmf_objects_from_model()
    # for obj in pmf_objects:
    #     print obj.filename()
    # if True:
    #     return

    # # Determine a groups per section ratio

    # # Get all section IDs and their respective groups into a map
    # section_groups = {}
    # section_group_sets = {}
    # for group in pmf_groups:
    #     for filename in pmf_groups[group]:
    #         section_id = UD_PMFObject.get_section(filename)
    #         if section_id not in section_groups:
    #             section_groups[section_id] = []
    #             section_group_sets[section_id] = []
    #         section_groups[section_id].append(group)
    # for section_id in section_groups:
    #     section_group_sets[section_id] = list(set(section_groups[section_id]))

    # section_ratios = []
    # # sentence_count = 0
    # for section_id in section_groups:
    #     section_ratios.append((section_id, float(len(section_group_sets[section_id])) / len(section_groups[section_id]) ))
    #     # sentence_count += len(section_groups[section_id])
    # section_ratios = sorted(section_ratios, key=lambda x: x[1], reverse=True)

    # # print "Sentence count: {0}".format(sentence_count)

    # for index in range(len(section_ratios)):
    #     print section_ratios[index]

  
if "__main__" == __name__:
    main()