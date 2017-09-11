
class UnnecessaryDuplicates:

    project_path = "/Users/PeregrinePickle/Documents/School/New York University/Seminars/Melville/unnecessary_duplicates/"
    
    input_path = project_path + "data/input/"
    section_path = input_path + "split/by_section/"
    paragraph_path = input_path + "split/by_paragraph/"
    sentence_path = input_path + "split/bysection_bysentence/"
    
    output_path = project_path + "data/output/"
    csv_path = output_path + "csv/"
    plots_path = output_path + "plots/"
    pmf_path = output_path + "pmf/"
    pos_path = output_path + "pos_counts/presentation/sentence_bysection_pos_counts/"

    pmf_model_csv_filename = "mobydick_sentence_clusters_1490819354731.csv"


class PMFObject:

    def __init__(self, p_filename, p_content, p_group):

        self.m_filename = p_filename
        self.m_content = p_content
        self.m_group = p_group

    def filename(self):
        return self.m_filename

    def content(self):
        return self.m_content

    def group(self):
        return self.m_group
    def set_group(self, p_group):
        self.m_group = p_group


class UD_PMFObject(PMFObject):

    def __init__(self, p_filename, p_sentence, p_group, p_pos):
        PMFObject.__init__(self, p_filename, p_sentence, p_group)
        self.m_pos = p_pos

    def filename_chapter(self):
        return UD_PMFObject.get_chapter(self.m_filename)
    def filename_order(self):
        return UD_PMFObject.get_order(self.m_filename)
    def filename_section(self):
        return UD_PMFObject.get_section(self.m_filename)
    def filename_title(self):
        return UD_PMFObject.get_title(self.m_filename)

    def pos(self):
        return self.m_pos
    def set_pos(self, p_pos_vector):
        self.m_pos = p_pos_vector

    def sentence(self):
        return PMFObject.content(self)


    # Utility functions
    @staticmethod
    def get_chapter(p_filename):

        filename_pieces = p_filename.split("_")
        for piece in filename_pieces:
            if "chapter" in piece:
                return piece[piece.rfind("r")+1:]
        return "NA"

    @staticmethod
    def get_order(p_filename):

        filename_pieces = p_filename.split("_")
        return filename_pieces[len(filename_pieces) - 2]

    @staticmethod
    def get_section(p_filename):

        return p_filename.split("_")[2]

    @staticmethod
    def get_title(p_filename):

        filename_pieces = p_filename.split("_")
        
        if 5 == len(filename_pieces):
            title = filename_pieces[3]
        else: # len == 6
            title = filename_pieces[3] + "_" + filename_pieces[4]
        return title

