import torch
from transformers import CLIPProcessor, CLIPTokenizer, CLIPModel
from PIL import Image
from sentence_transformers import util
import os
import json
import numpy as np
import matplotlib.pyplot as plt


IMAGE_EMBEDDING_MODEL = "openai/clip-vit-base-patch16"
PROMPT_TEMPLATE = """
Found local information:
The photo name is “{name}”. More details “{text}”.
"""

# def embed_image_with_clip(image_path):
#     # Load the model and processor
#     model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16")
#     processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")

#     # Load the image and preprocess
#     image = Image.open(image_path)
#     image_input = processor(text="dummy", images=image, return_tensors="pt", padding=True)

#     # Get the image embeddingr
#     with torch.no_grad():
#         outputs = model(**image_input)
#         image_features = outputs.image_embeds

#     return image_features


class ImageVecDataBaseV2():
    def __init__(self, db_image_dir_path, db_image_embeding_path, update=True):
        self.model = CLIPModel.from_pretrained(IMAGE_EMBEDDING_MODEL)
        self.processor = CLIPProcessor.from_pretrained(IMAGE_EMBEDDING_MODEL)
        self.db_image_embeding_path = db_image_embeding_path
        self.dataset = self.__load_img_dataset(db_image_dir_path)
        if update or db_image_embeding_path:
            self.db_embedding_dump(db_image_embeding_path)
        
        # Load db corpus embeddings
        self.corpus_embeddings = np.load(self.db_image_embeding_path + '.npy')
       
    def __load_img_dataset(self, db_image_dir_path):
        with open(os.path.join(db_image_dir_path, 'metadata.jsonl'), 'r') as file:
            json_list = list(file)

        dataset = []
        for json_str in json_list:
            img_data = json.loads(json_str)
            img = Image.open(os.path.join(db_image_dir_path, img_data['file_name']))
            if img is not None:
                img_data['image'] = img
            dataset.append(img_data)
        return dataset


    def db_embedding_dump(self, db_image_embeding_path):
        embeddings = self.embed_images([data['image'] for data in self.dataset])
        np.save(db_image_embeding_path, embeddings)

    def embed_images(self, images):
        embeddings = []
        for image in images:
            image_input = self.processor(text="dummy", images=image, return_tensors="pt", padding=True)

            # Get the image embeddingr
            with torch.no_grad():
                outputs = self.model(**image_input)
                # print("embeding dims:" + str(outputs.image_embeds[0].shape))
                embeddings.append(outputs.image_embeds[0])

        return embeddings

    # return (most_similar_img, most_similar_img_db_index, sim_score)
    def search_db(self, user_image, threshold=0.2, top_n = 5):
        top_n = min(top_n, len(self.dataset))
        query_embedding = self.embed_images([user_image])

        # Find the most similar image
        cosine_scores = util.pytorch_cos_sim(query_embedding[0], self.corpus_embeddings)        
        top_results = np.argpartition(-cosine_scores, range(top_n))[0:top_n]

        # #print("\nTop {top_n} most similar sentences in corpus:")
        score = []
        for idx in top_results[0]:
            score = cosine_scores[0][idx]
            if cosine_scores[0][idx].item() > threshold:
                return self.dataset[idx]['image'], int(idx.int()), float(score.float())
            
        return None, None, None
    
    def db_image_prompt(self, idx):
        if idx >= 0 and idx < len(self.dataset):
           return PROMPT_TEMPLATE.format(name=self.dataset[idx]["name"], text=self.dataset[idx]["text"])
        
        return ""
    
    def db_image_info(self, idx):
        if idx >= 0 and idx < len(self.dataset):
            return self.dataset[idx]
        
        return ""


if __name__ == '__main__':
    # image folder path, and the image metadata json file path
    image_db = ImageVecDataBaseV2('./db/images-ocp', './db/images-ocp/embeddings')
    # Read image
    # img = Image.open('./test_data/images/test_google_logo2.jpg')
    img = Image.open('./test_data/images/test_google_logo.jpg')
    # img = Image.open('./test_data/images/test_etsi_logo.jpeg')
    most_similar_img, most_similar_img_idx, sim_score = image_db.search_db(img)
    
    print("Score: %.4f" % (sim_score))
    print("Index of most similar image in DB: %.4f" % (most_similar_img_idx))
    plt.imshow(most_similar_img)
    plt.show()



