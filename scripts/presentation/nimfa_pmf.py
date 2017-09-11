import nimfa
import numpy
import scipy.cluster.hierarchy
from scipy.cluster.hierarchy import fcluster


class Nimfa:

    def __init__(self, p_data_rows, p_row_count, p_col_count):
        
        self.m_row_count = p_row_count
        self.m_col_count = p_col_count
        self.m_data_matrix = self.__build_data_matrix(p_data_rows)


    def __build_data_matrix(self, p_data_rows):

        # A zeroed data matrix NxM
        data_matrix = numpy.zeros((self.m_row_count, self.m_col_count))

        # Save poem pos counts for the fascicle to the matrix
        for row_index in range(self.m_row_count):
            for col_index in range(self.m_col_count):
                data_matrix[row_index, col_index] = p_data_rows[row_index][col_index]
                
        # Normalize all matrix entries to account for data source length for each source
        for row_index in range(self.m_row_count):

            entry_sum = 0
            for entry in data_matrix[row_index]:
                entry_sum += entry

            if entry_sum > 0:
                for col_index in range(self.m_col_count):
                    data_matrix[row_index, col_index] /= float(entry_sum) 

        # Return the data matrix
        return data_matrix


    def pmf(self, p_factorization_rank=2, p_max_iterations=10, p_runs=10):

        pmf_args = {
            "data_matrix": self.m_data_matrix,
            "rank": p_factorization_rank,
            "seed": "random_vcol",
            "max_iter": p_max_iterations,
            "n_run": p_runs,
            "rel_error": 1e-5
        }

        pmf = nimfa.Pmf(pmf_args["data_matrix"].T, rank=pmf_args["rank"], seed=pmf_args["seed"], 
                        max_iter=pmf_args["max_iter"], n_run=pmf_args["n_run"], rel_error=pmf_args["rel_error"],
                        track_factor=True)

        return pmf


    def pmf_clusters(self, p_pmf):

        pmf_fit = p_pmf()
        consensus = 1 - pmf_fit.fit.consensus()
        hierarchical_clusters = scipy.cluster.hierarchy.linkage(consensus, method="ward")
        flattened_clusters = fcluster(hierarchical_clusters, self.m_row_count, criterion="maxclust")

        return flattened_clusters
