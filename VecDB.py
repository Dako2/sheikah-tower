#transfer any raw text data into embeddings with index

from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import pickle
import os

NAME_EMBEDDING_MODEL = 'all-MiniLM-L6-v2' #

class VecDataBase():
    def __init__(self, db_csv_paths={'loc1':'db/exhibit-info.csv', 'user1':'db/user-data.csv'}, update_db = True):
        self.model = SentenceTransformer(NAME_EMBEDDING_MODEL)
        if update_db and db_csv_paths:
            for _, db_csv_path in db_csv_paths.items():
                print(db_csv_path)
                if db_csv_path[-3::] == "csv":
                    self.text_to_ebds_csv(db_csv_path)
                elif db_csv_path[-4::] == "json":
                    self.text_to_ebds_json(db_csv_path)
                else:
                    pass
        self.cache_vector_database = {}

    def text_to_ebds_csv_old(self, db_csv_path):
        with open(db_csv_path, 'r') as file:
            rows = file.readlines()
        corpus = [row.strip() for row in rows]
        db_ebds = self.model.encode(corpus, convert_to_numpy=True)
        db_emb_path = db_csv_path + '.npy'
        np.save(db_emb_path, db_ebds)
    
    def text_to_ebds_csv(self, db_csv_path):
        with open(db_csv_path, 'r') as file:
            rows = file.readlines()
        corpus = [row.strip() for row in rows]
        print(corpus)
        result = {}
        for i, value in enumerate(corpus):
            result['id'+str(i)+'_'] = self.model.encode(value, convert_to_numpy=True)
        self.save_to_pickle(result, db_csv_path+".pkl")
        print(f"converting embeddings {db_csv_path} and saved to {db_csv_path}.pkl")

    def text_to_ebds_json(self, db_csv_path):
        with open(db_csv_path, 'r') as file:
            data = json.load(file)
            corpus = {}
        for i, event in enumerate(data):
            for name, value in event.items():
                #index all the embeddings
                corpus['id'+str(i)+'_'+name] = self.model.encode(value, convert_to_numpy=True)
        self.save_to_pickle(corpus, db_csv_path+".pkl")
        print(f"converting embeddings {db_csv_path} and saved to {db_csv_path}.pkl")

        """
        with open("embeddings_dict.pkl", "rb") as f:
            loaded_dict = pickle.load(f)
        """
        if False:
            db_ebds = self.model.encode(list(corpus.values()), convert_to_numpy=True)
            db_emb_path = db_csv_path + '.npy'
            np.save(db_emb_path, db_ebds)

            with open(db_csv_path+'.keys', 'w') as key_file:
                json.dump(list(corpus.keys()), key_file)
        
        """
        # Load keys from JSON file
        with open('keys.json', 'r') as key_file:
            loaded_keys = json.load(key_file)

        # Load values from numpy file
        loaded_values = np.load('values.npy', allow_pickle=True)

        # Example: Getting the key name from the row ID
        row_id = 1
        key_name = loaded_keys[row_id]
        """
        return corpus #{'id0_event0':[0.7,0.8,0.9]}

    def save_to_pickle(self, data, file_path):
        dir_path = os.path.dirname(file_path)
        # Ensure the directory exists
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # Save data to pickle file
        with open(file_path, 'wb') as file:
            pickle.dump(data, file)
            
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

    #the index of the list; if only corpus then return the corpus[idx]; 
    #if pickel then return corpus[idx] and parse it json_data[int(x.split('_')[0][2::])] 'id0' and find the index in the original json file. 
    def search_db(self, user_input, db_json_file, threshold=0.2, top_n = 5):
        if db_json_file in list(self.cache_vector_database.keys()):
            corpus_json = self.cache_vector_database[db_json_file]
        else:
            with open(db_json_file, 'r', encoding='utf-8') as file:
                corpus_json = json.load(file)

        db_pkl_file = db_json_file + '.pkl'        # Load corpus and corpus embedding
        if db_pkl_file in list(self.cache_vector_database.keys()):
            corpus_embeddings = self.cache_vector_database[db_pkl_file]
            print(f"loading the cached database {db_pkl_file}")
        else:
            with open(db_pkl_file, "rb") as file:
                corpus_embeddings = pickle.load(file)
            self.cache_vector_database[db_pkl_file] = list(corpus_embeddings)

        query_embedding = self.model.encode(user_input, convert_to_numpy=True)
        cosine_scores = util.pytorch_cos_sim(query_embedding, list(corpus_embeddings.values()))        
        top_results = np.argpartition(-cosine_scores, range(top_n))[0:top_n]
        result = ''
        score = []
        for idx in top_results[0]:
            if cosine_scores[0][idx].item() > threshold:
                #print(corpus[idx], "(Score: %.4f)" % (cosine_scores[0][idx]))
                result_id = list(corpus_embeddings.keys())[idx]
                result += json.dumps(corpus_json[int(result_id.split('_')[0][2::])])
                score.append(cosine_scores[0][idx].item())
        if result:
            print("\n most similar sentences in corpus:", result, "avg. score:",sum(score)/len(score),"\n")
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
        result = ''
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



