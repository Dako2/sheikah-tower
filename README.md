<h1> Hey there! We are Sheikah 👋 </h1>

<h3> 👨🏻‍💻 About Us and this Project </h3>
We are driven by a humble desire to explore the immense potential of MEC and edge computing for Large Language Models Applications. We are building an ecosystem. We aim to provide the necessary infrastructure while leveraging the advantages of MEC. This involves optimizing data consumption, enhancing security and privacy, addressing the challenges between cloud, edge, and end-users, and achieving improved redundancy and resilience. We're also leveraging the wealth of additional information offered by MEC and synergizing it with large language models to enhance the overall user experience.

<h3> 🛠 Tech Stack </h3>
HW/SW co-design diagrams:

![sheikah - Page 2](https://github.com/Dako2/sheikah-tower/assets/63529538/326b6ed8-c98c-4626-9855-e2e7d2740f1e)

- 💻 &nbsp; Device side

we seamlessly integrate various user data types, including live information, location data, and inputs in multiple formats, such as images, text, audio, JSON, and video saved in the vector database. These inputs undergo embedding searches for relevant information and are then processed within our Flow Client before being transmitted to the MEC as inputs.
  
- 🌐 &nbsp; MEC side

We leverage MEC APIs and local vector databases, each housing data in diverse formats. These rich local data, along with the user inputs from the device side, empower our Large Language Models with user-specific insights and abundant local knowledge. We are also facilitating seamless streaming audio interactions through our streaming ASR TTS services, which operate on the MEC.

- 🔧 &nbsp; Edge Computing Front

We are striving to maximize the potential of edge resources, including computing, storage, and server engines, which opens up opportunities in the future such as federated learning on the edge. This approach enables us to deliver highly customized and localized services, ultimately shaping the future of our platform.

<h3> 👨🔧 Try it! </h3>

<h4> Step 1 </h4>
pip install -r requirements.txt

<h4> Step 2 </h4>

run app.py
