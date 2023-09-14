from transformers import AutoFeatureExtractor, AutoModel
from sentence_transformers import util
import matplotlib.pyplot as plt
import torchvision.transforms as T
import torch
import numpy as np
from PIL import Image


from datasets import load_dataset

IMAGE_EMBEDDING_MODEL = "google/vit-base-patch16-224"

# extractor = AutoFeatureExtractor.from_pretrained(IMAGE_EMBEDDING_MODEL)
# model = AutoModel.from_pretrained(IMAGE_EMBEDDING_MODEL)
# hidden_dim = model.config.hidden_size

class ImageVecDataBase():
    def __init__(self, db_image_dir_path, db_image_embeding_path, update=True):
        self.model = AutoModel.from_pretrained(IMAGE_EMBEDDING_MODEL)
        extractor = AutoFeatureExtractor.from_pretrained(IMAGE_EMBEDDING_MODEL)
        # hidden_dim = model.config.hidden_size
        self.transformation_chain = T.Compose(
            [
                # We first resize the input image to 256x256 and then we take center crop.
                T.Resize(int((256 / 224) * extractor.size["height"])),
                T.CenterCrop(extractor.size["height"]),
                T.ToTensor(),
                T.Normalize(mean=extractor.image_mean, std=extractor.image_std),
            ]
        )
        # Example: ['image', 'text']
        self.db_image_embeding_path = db_image_embeding_path
        self.db_image_dir_path = db_image_dir_path
        self.dataset = load_dataset('imagefolder', data_dir=db_image_dir_path)['train']
        if update and db_image_embeding_path:
            self.db_embedding_dump(db_image_embeding_path)

    def db_embedding_dump(self, db_image_embeding_path):
        embeddings = self.embed_images([data['image'] for data in self.dataset])
        np.save(db_image_embeding_path, embeddings)

    def embed_images(self, images):
        image_batch_transformed = torch.stack(
            [self.transformation_chain(image) for image in images]
        )
        new_batch = {"pixel_values": image_batch_transformed.to("cpu")}
        with torch.no_grad():
            embeddings = self.model(**new_batch).last_hidden_state[:, 0].cpu()
        return embeddings

    #WIP
    def similarity(self, image, threshold=0.6, top_n = 2):
        embeddings = self.embed_images([image])
        # similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
        # print(similarity.item())
        pass

    # return (most_similar_img, most_similar_img_db_index, sim_score)
    def search_db(self, user_image, threshold=0.2, top_n = 5):
        query_embedding = self.embed_images([user_image])
        
        # Load db corpus embeddings
        corpus_embeddings = np.load(self.db_image_embeding_path + '.npy')
        
        # Find the most similar image
        cosine_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)        
        top_results = np.argpartition(-cosine_scores, range(top_n))[0:top_n]

        # #print("\nTop {top_n} most similar sentences in corpus:")
        score = []
        for idx in top_results[0]:
            score = cosine_scores[0][idx]
            if cosine_scores[0][idx].item() > threshold:
                return self.dataset['image'][idx], int(idx.int()), float(score.float())
            
        return None, None, None
        

if __name__ == '__main__':
    image_db = ImageVecDataBase('./db/images', './db/images/embeddings')
    # Read image
    img = Image.open('./test_data/images/test_0001.jpeg')
    most_similar_img, most_similar_img_idx, sim_score = image_db.search_db(img)
    
    print("Score: %.4f" % (sim_score))
    print("Index of most similar image in DB: %.4f" % (most_similar_img_idx))
