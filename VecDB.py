from sentence_transformers import SentenceTransformer, util
import numpy as np

NAME_EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

class VecDataBase():
    def __init__(self, db_csv_paths, update_db = True):
        self.model = SentenceTransformer(NAME_EMBEDDING_MODEL)
        if update_db and db_csv_paths:
            for _, db_csv_path in db_csv_paths.items():
                self.text_to_ebds_csv(db_csv_path)

    def text_to_ebds_csv(self, db_csv_path):
        with open(db_csv_path, 'r') as file:
            rows = file.readlines()
        corpus = [row.strip() for row in rows]
        db_ebds = self.model.encode(corpus, convert_to_numpy=True)
        
        db_emb_path = db_csv_path + '.npy'
        np.save(db_emb_path, db_ebds)

    #WIP
    def similarity(self, sentences, threshold=0.6, top_n = 2):
        embeddings = self.model.encode(sentences, convert_to_numpy=True)
        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
        print(similarity.item())

    def search_db(self, user_input, db_text_file, threshold=0.6, top_n = 5):
        query_embedding = self.model.encode(user_input, convert_to_numpy=True)
        
        # Load corpus and corpus embedding
        with open(db_text_file, 'r') as file:
            corpus = [line.strip() for line in file.readlines()]
        corpus_embeddings = np.load(db_text_file + '.npy')
        
        # Find the most similar sentences
        # hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=2)
        cosine_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)        
        top_results = np.argpartition(-cosine_scores, range(top_n))[0:top_n]

        #print("\nTop {top_n} most similar sentences in corpus:")
        result = ''
        score = []
        for idx in top_results[0]:
            if cosine_scores[0][idx].item() > threshold:
                print(corpus[idx], "(Score: %.4f)" % (cosine_scores[0][idx]))
                result += corpus[idx]
                score.append(cosine_scores[0][idx].item())
        print("\n most similar sentences in corpus:",result, "score:",score)
        return result, score
    
if __name__ == "__main__":
    DATA_PATH={'loc1':'db/exhibit-info.csv', 'user1':'db/user-data.csv'}
    v = VecDataBase(DATA_PATH)
    res, score = v.search_db('Nefertiti Bust-Nefertiti','db/exhibit-info.csv')
