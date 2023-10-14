#transfer any raw text data into embeddings with index
from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import pickle
import os

NAME_EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

class VecDataBase():

    def __init__(self, db_paths, update_db = True):
        self.cache_vector_database = {}
        self.model = SentenceTransformer(NAME_EMBEDDING_MODEL)
        if update_db and db_paths: #initalialize embeddings
            for _, db_path in db_paths.items():
                self.convert_json_to_embeddings(db_path) 

    def convert_json_to_embeddings(self, db_paths):
        with open(db_paths, 'r') as file:
            corpus_list = json.load(file)
        
        embeddings = {}
        
        # Processing the embeddings
        for i, event in enumerate(corpus_list):
            for name, value in event.items():
                embeddings['id'+str(i)+'_'+name] = self.model.encode(value, convert_to_numpy=True).tolist()  # embedding
        
        # Writing the embeddings
        ebd_file_path = f"{db_paths}.ebd"
        with open(ebd_file_path, 'w', encoding='utf-8') as file:
            json.dump(embeddings, file, ensure_ascii=False, indent=4)
        
        print(f"Converting embeddings {db_paths} and saved to {ebd_file_path}")
        return 0

    def encode_sentences(self, corpus_dict):
        if not all(isinstance(key, str) and isinstance(value, str) for key, value in corpus_dict.items()):
            raise ValueError("All keys and values in corpus_dict must be strings")
        sentences = list(corpus_dict.values())
        embeddings = self.model.encode(sentences, convert_to_numpy=True)
        embeddings_dict = {key: embedding for key, embedding in zip(corpus_dict.keys(), embeddings)}
        return embeddings_dict
 
    def similarity(self, sentences, threshold=0.6, top_n = 2):
        embeddings = self.model.encode(sentences, convert_to_numpy=True)
        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
        print(similarity.item())

    def search_db(self, user_input, db_json_file, threshold=0.2, top_n = 5):

        if db_json_file in list(self.cache_vector_database.keys()): #quick load corpus_json 
            corpus_json = self.cache_vector_database[db_json_file]
            print(f"loaded json {db_json_file}")
        else:
            with open(db_json_file, 'r', encoding='utf-8') as file:
                corpus_json = json.load(file)
            self.cache_vector_database[db_json_file] = corpus_json 

        db_ebd_file = db_json_file + '.ebd'
        if not os.path.exists(db_ebd_file):
            self.convert_json_to_embeddings(db_json_file)
        
        print(f"{db_ebd_file}...........123")
        if db_ebd_file in list(self.cache_vector_database.keys()): #quick load embeddings corpus_ebd
            corpus_ebd = self.cache_vector_database[db_ebd_file]
            print(f"loaded vdb {db_ebd_file}")
        else:
            if os.path.getsize(db_ebd_file) > 0:
                with open(db_ebd_file, 'r', encoding='utf-8') as file:
                    try:
                        corpus_ebd = json.load(file)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
            else:
                print(f"File is empty: {db_ebd_file}")
                
            self.cache_vector_database[db_ebd_file] = corpus_ebd

        query_embedding = self.model.encode(user_input, convert_to_numpy=True) #user input -> query_embedding
        cosine_scores = util.pytorch_cos_sim(query_embedding, corpus_ebd.values())       
        top_results = np.argpartition(-cosine_scores, range(top_n))[0:top_n]

        result = ''
        score = []
        for idx in top_results[0]:
            if cosine_scores[0][idx].item() > threshold:
                #print(corpus[idx], "(Score: %.4f)" % (cosine_scores[0][idx]))
                result_id = list(corpus_ebd.keys())[idx]
                result += json.dumps(corpus_json[int(result_id.split('_')[0][2::])])
                score.append(cosine_scores[0][idx].item())
        if result:
            print("\n most similar sentences in corpus:", result, "\n avg. score:",sum(score)/len(score),"\n")
        return result, score

    def search_db_v0(self, user_input, db_text_file, threshold=0.2, top_n = 5):
        query_embedding = self.model.encode(user_input, convert_to_numpy=True)
        # Load corpus and corpus embedding
        if db_text_file in list(self.cache_vector_database.keys()):
            corpus_embeddings = self.cache_vector_database[db_text_file]
            print(f"loading the cached database {db_text_file}")
        else:
            if db_text_file[-3::] == 'npy':
                with open(db_text_file, 'r') as file:
                    corpus = [line.strip() for line in file.readlines()] #List
                corpus_embeddings = np.load(db_text_file)
                self.cache_vector_database[db_text_file] = corpus_embeddings
                
            elif db_text_file[-3::] == 'pkl':
                with open(db_text_file, "rb") as file:
                    corpus_embeddings = pickle.load(file)
                self.cache_vector_database[db_text_file] = list(corpus_embeddings.values())
                corpus_mapper = list(corpus_embeddings.keys())
            else:
                print(f"error in opening the database {db_text_file}")
        
        return self.search_db_raw(query_embedding, corpus, corpus_embeddings, threshold, top_n)
    
    def search_db_raw(self, query_embedding, corpus, corpus_embeddings, threshold=0.6, top_n = 1):
        # Find the most similar sentences
        # hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=2)
        cosine_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)        
        top_results = np.argpartition(-cosine_scores, range(top_n))[0:top_n]
        result = ""
        score = []
        for idx in top_results[0]:
        #the index of the list; if only corpus then return the corpus[idx]; 
        #if pickel then return corpus[idx] and parse it json_data[int(x.split('_')[0][2::])] 'id0' and find the index in the original json file. 
            if cosine_scores[0][idx].item() > threshold:
                #print(corpus[idx], "(Score: %.4f)" % (cosine_scores[0][idx]))
                result += corpus[idx]
                score.append(cosine_scores[0][idx].item())
        if result:
            print("\n most similar sentences in corpus:", result, "avg. score:",sum(score)/len(score),"\n")
        return result, score
    
if __name__ == "__main__":
    DATA_PATH={'loc1':'./db/ocp/ocp.json'} #{'loc1':'db/exhibit-info.csv', 'user1':'db/user-data.csv'}
    v = VecDataBase(DATA_PATH, True)
    #res, score = v.search_db('Nefertiti Bust-Nefertiti','db/exhibit-info.csv')
    #x = v.text_to_ebds_json('./db/ocp/ocp.jsonl')



