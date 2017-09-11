import glob
import os

import spacy
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools

from project_defines import UnnecessaryDuplicates


def export_entities():

    # spaCy English NLP object
    nlp = spacy.load("en")

    # Gather "person" entities from the texts
    sections = []
    entities = []
    for full_filepath in glob.glob(UnnecessaryDuplicates.section_path + "mobydick_*.txt"):
        with open(full_filepath, "rU") as section_file:
            try:
                data = unicode(section_file.read())
            except:
                print "Problem reading {0}. Continuing to process texts...".format(os.path.basename(full_filepath))
                continue
            doc = nlp(data)
            entities.extend([ent.text for ent in doc.ents if ent.label_ == "PERSON"])

    # Export person entity list to csv
    entities = sorted(list(set(entities)))
    with open(UnnecessaryDuplicates.csv_path + "mobydick_person_entities.csv", "w") as output_file:
        for entity in entities:
            output_file.write(entity + "\n")


def get_entity_counts_by_par_section(p_entity_list, p_paragraph_count):

    paragraphs = []

    # Count mentions of given entities in the text sections
    for full_filepath in glob.glob(UnnecessaryDuplicates.paragraph_path + "*mobydick*.txt"):

        with open(full_filepath, "rU") as section_file:
            
            try:
                data = unicode(section_file.read())
            except:
                print "Problem reading {0}. Continuing to process texts...".format(os.path.basename(full_filepath))
                continue

            # Keep sections in order
            # example key: 1288_mobydick_138_CHAPTER_135._The_Chase.--Third_Day_56_2515_0.txt
            base_filename = os.path.basename(full_filepath)
            filename_parts = base_filename.split("_")
            paragraph_number = int(filename_parts[len(filename_parts) - 2])
            paragraphs.append((paragraph_number, {base_filename: {}}))
            cindex = len(paragraphs) - 1
            
            for entity in p_entity_list:
                if list == type(entity):
                    paragraphs[cindex][1][base_filename][entity[0]] = 0
                else:
                    paragraphs[cindex][1][base_filename][entity] = 0
            lines = data.split("\n")
            for line in lines:
                lower_line = line.lower()
                for entity in p_entity_list:
                    if list == type(entity):
                        for alias in entity:
                            if alias in lower_line:
                                paragraphs[cindex][1][base_filename][entity[0]] += 1
                                break
                    else:
                        if entity in lower_line:
                            paragraphs[cindex][1][base_filename][entity] += 1


    # Sort sections by section number
    paragraphs = sorted(paragraphs, key=lambda x: x[0])

    return paragraphs


def get_entity_counts_by_section(p_entity_list):

    sections = []

    # Count mentions of given entities in the text sections
    for full_filepath in glob.glob(UnnecessaryDuplicates.section_path + "mobydick_*.txt"):
        with open(full_filepath, "rU") as section_file:
            
            base_filename = os.path.basename(full_filepath)

            try:
                data = unicode(section_file.read())
            except:
                print "Problem reading {0}. Continuing to process texts...".format(os.path.basename(full_filepath))
                continue

            # Keep sections in order
            # example key: 'mobydick_69_CHAPTER 66. The Shark Massacre.txt'
            section_number = int(base_filename.split("_")[1])
            sections.append((section_number, {base_filename: {}}))
            cindex = len(sections) - 1
            
            for entity in p_entity_list:
                if list == type(entity):
                    sections[cindex][1][base_filename][entity[0]] = 0
                else:
                    sections[cindex][1][base_filename][entity] = 0
            lines = data.split("\n")
            for line in lines:
                lower_line = line.lower()
                for entity in p_entity_list:
                    if list == type(entity):
                        for alias in entity:
                            if alias in lower_line:
                                sections[cindex][1][base_filename][entity[0]] += 1
                                break
                    else:
                        if entity in lower_line:
                            sections[cindex][1][base_filename][entity] += 1


    # Sort sections by section number
    sections = sorted(sections, key=lambda x: x[0])

    return sections


def plot_entity_counts_by_section(p_section_character_counts, p_plot_type, p_section_names_only=False):

    # Create section labels for X-axis of plot
    # example key: # example key: 1288_mobydick_138_CHAPTER_135._The_Chase.--Third_Day_56_2515_0.txt
    # label output: 'CHAPTER 66. The Shark Massacre'
    section_labels = []
    if p_section_names_only:
        for index in range(len(p_section_character_counts)):
            filename = p_section_character_counts[index][1].keys()[0]
            filename_parts = filename.split("_")
            section_name = "_".join(filename_parts[3:]).strip(".txt").strip()
            paragraph_number = filename_parts[len(filename_parts) - 2]
            if len(section_labels) > 0:
                if section_name != section_labels[len(section_labels) - 1]:
                    section_labels.append(section_name)
                else:
                    section_labels.append(paragraph_number)
            else:
                section_labels.append(section_name)
    else:
        for index in range(len(p_section_character_counts)):
            filename = p_section_character_counts[index][1].keys()[0]
            section_name = filename.split("_")[2].strip(".txt").strip()
            section_labels.append(section_name)

    # Get character names and alphabetically sort them
    character_names = sorted(p_section_character_counts[0][1][p_section_character_counts[0][1].keys()[0]].keys())

    # Tally longitudinal character counts across sections
    character_counts_across_sections = [[0] * len(p_section_character_counts) for i in range(len(character_names))]
    for index in range(len(p_section_character_counts)):
        filename = p_section_character_counts[index][1].keys()[0]
        for index2 in range(len(character_names)):
            character_counts_across_sections[index2][index] = p_section_character_counts[index][1][filename][character_names[index2]]

    # Create traces for plotting the entity counts
    if "bar" == p_plot_type:
        # Create plotly traces for counts per section
        all_traces = []
        for index in range(len(character_counts_across_sections)):
            all_traces.append(go.Bar(name=character_names[index], x=section_labels, y=character_counts_across_sections[index]))

        # Create layout and figure objects and plot data
        layout = go.Layout(barmode="group")
        fig = go.Figure(data=all_traces, layout=layout)
        py.plot(fig, filename="mobydick_character_counts_" + "_".join(character_names))   

    elif "scatter" == p_plot_type:

        # Remove '0' counts, to allow for gaps in the plot
        # for index in range(len(character_names)):
        #     for index2 in range(len(p_section_character_counts)):
        #         if 0 == character_counts_across_sections[index][index2]:
        #             character_counts_across_sections[index][index2] = None

        # Create plotly traces for counts per section
        all_traces = []
        for index in range(len(character_counts_across_sections)):
            all_traces.append(go.Scatter(name=character_names[index],
                                         x=section_labels,
                                         y=character_counts_across_sections[index],
                                         line=dict(shape="spline"),
                                         mode="lines+markers"))

        # Create layout and figure objects and plot data
        layout = dict(title = 'Character Mentions in Moby-Dick',
                      xaxis = dict(title = 'Book Sections'),
                      yaxis = dict(title = 'Raw Counts'))

        fig = go.Figure(data=all_traces, layout=layout)
        py.plot(fig, filename="mobydick_character_counts_" + "_".join(character_names))   


def main():

    # export_entities()

    entities_one = ["ahab", "bildad", "peleg", "ishmael", ["moby dick", "moby-dick", "white whale"]]
    entities_two = ["bulkington", "queequeg", "starbuck", "ishmael", ["moby dick", "moby-dick", "white whale"]]
    my_entities = entities_two

    # entity_counts = get_entity_counts_by_section(my_entities)
    # plot_entity_counts_by_section(entity_counts, "scatter")

    entity_counts = get_entity_counts_by_par_section(my_entities, 2524)
    # plot_entity_counts_by_section(entity_counts, "scatter", True)
    plot_entity_counts_by_section(entity_counts, "bar", True)


if "__main__" == __name__:
    main()