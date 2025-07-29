import numpy as np


class VectorStore():
    def __init__(self):
        """
         Initialize an empty dictionary to store vector data with vector_id as keys
         and corresponding vectors as values.
         
         Initialize an empty dictionary to store similarity index between vectors.
         It is a nested dictionary where each vector_id has a sub-dictionary with
         other vector_ids as keys and their similarities as values.
        """
        self.vector_data = {}
        self.vector_index = {}

    def similarity(self,vector1,vector2):
        vector1_norm = vector1 / np.linalg.norm(vector1)
        vector2_norm = vector2 / np.linalg.norm(vector2)

        return np.dot(vector1_norm,vector2_norm)

    def add_vector(self,vector,vector_id):
        self.vector_data[vector_id]=vector
        
        for existing_id, existing_vector in self.vector_data.items():
            sim = self.similarity(vector,existing_vector)
            
            if existing_id not in self.vector_index:
                self.vector_index[existing_id] = {}
            
            self.vector_index[existing_id][vector_id] = sim 

        
v1 = np.array([2,3,5])
v2 = np.array([5,6,1])
vb = VectorStore()
vb.add_vector(v1,"v1")
vb.add_vector(v2,"v2")

print(vb.vector_index)