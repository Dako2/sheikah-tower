from transformers import AutoFeatureExtractor, AutoModel
from sentence_transformers import util
import matplotlib.pyplot as plt
import torchvision.transforms as T
import torch
import numpy as np
from PIL import Image
from datasets import load_dataset

IMAGE_EMBEDDING_MODEL = "google/vit-base-patch16-224"
PROMPT_TEMPLATE_OLD = """
The user just took a photo of “{name}”. 
Tell the user a story about the photo, it can be history related, a fun fact, 
future event or just any stories that can raise the user's interests.
More info about the image: “{text}”.
At the end of the conversation, ask the user a related question that the user might be able to guess.
"""

PROMPT_TEMPLATE = """
Found local information:
The photo name is “{name}”. More details “{text}”.
"""

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
        
        # Load db corpus embeddings
        self.corpus_embeddings = np.load(self.db_image_embeding_path + '.npy')
        print(self.corpus_embeddings.shape)
       
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

    # return (most_similar_img, most_similar_img_db_index, sim_score)
    def search_db(self, user_image, threshold=0.2, top_n = 1):
        top_n = min(top_n, len(self.dataset))
        query_embedding = self.embed_images([user_image])
        
        # Find the most similar image
        cosine_scores = util.pytorch_cos_sim(query_embedding, self.corpus_embeddings)        
        top_results = np.argpartition(-cosine_scores, range(top_n))[0:top_n]

        print(cosine_scores, top_results, )

        # #print("\nTop {top_n} most similar sentences in corpus:")
        score = []
        for idx in top_results[0]:
            score = cosine_scores[0][idx]
            if cosine_scores[0][idx].item() > threshold:
                return self.dataset['image'][idx], int(idx.int()), float(score.float())
            
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
    image_db = ImageVecDataBase('./db/images-ocp', './db/images-ocp/embeddings')
    # Read image
    img = Image.open('./test_data/images/test_google_logo2.jpg')
    most_similar_img, most_similar_img_idx, sim_score = image_db.search_db(img)
    
    print("Score: %.4f" % (sim_score))
    print("Index of most similar image in DB: %.4f" % (most_similar_img_idx))
    plt.imshow(most_similar_img)
    plt.show()
