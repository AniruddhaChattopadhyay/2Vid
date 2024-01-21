# 2VID: Anything to video in 2 minutes

![Untitled](2VID%20Anything%20to%20video%20in%202%20minutes%20220c16266fa24a7fa6b7276cb55de20e/Untitled.png)

The Repository contains code for the project, **2Vid : Anything to Video in 2 Minutes.** 

**[LIVE DEMO](https://youtu.be/SUKkVR4JrJo)** 

**[PITCH VIDEO](https://www.youtube.com/watch?v=rBAGyoePz6Y)** 

[**PITCH DECK**](https://docs.google.com/presentation/d/1SRl3G7AIyInN25L9SUrRlYH8J-2m4H26ehlXtSbG2eQ/edit?usp=sharing)


[**WEBSITE**](https://2vid.tech/)

🎥 Transforming Text & URLs into Captivating Videos: Empowering Brands with AI-Driven Solutions 🚀

Welcome to 2Vid, a trailblazing SAAS company revolutionizing video creation for businesses. Our innovative platform leverages cutting-edge generative AI technology to transform text and URLs into visually stunning, engaging videos. No video production skills or costly resources required.

✅ Text-to-Video Transformation: Seamlessly convert text into compelling video narratives, streamlining the video production process.
✅ URL Integration: Transform web content into visually captivating videos, including articles, blog posts, and more.
✅ Customization Options: Personalize videos with fonts, colors, transitions, and effects, reflecting your brand identity.
✅ Rich Media Library: Access high-quality visuals, animations, stock footage, and soundtracks to enhance your videos.
✅ Intuitive Editing Interface: User-friendly platform for easy navigation and seamless video editing.

🎯 2Vid caters to diverse industries—marketing, advertising, e-learning, and social media. Elevate your online presence, boost engagement, and effectively communicate your message with our solution.

💡 Unlock your content's true potential with 2Vid's groundbreaking SAAS tool. Experience the power of generative AI in video creation. Together, we'll redefine how brands engage with audiences.

🌐 Visit our website to explore endless possibilities and start your video creation revolution. Connect with us for updates, inspiration, and industry discussions!

# [BACKEND TECH]

Backend Tech for 2Vid. 

## [Setup]

### [Python Setup]

1. Run
    
    ```
    pip install -r requirements.txt
    
    ```
    
2. We need Pillow python package with `libraqm` support. The previous step takes care of downloading the base Pillow package. To get `libraqm` support follow below steps:\
- Download `libraqm‑0.7.1.dll.zip` from this [link](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow)
- Extract the zip file
- Add the folder containing the `libraqm‑0.7.1.dll` to PATH (the file should be under `x64` folder)

### [Usage:]

To get the Bard token:

1. Visit [https://bard.google.com/](https://bard.google.com/)
2. F12 for console
3. Session: Application → Cookies → Copy the value of __Secure-1PSID cookie. Refer to this link for further details on the Google Bard Token: [https://github.com/dsdanielpark/Bard-API](https://github.com/dsdanielpark/Bard-API)

The `.env` file should look like this:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_DEV_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
XI_LABS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_BARD_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

```

Note: the other api keys are available at respective accounts

---

To Run the back end we need to start rabbitmq server and then celery to make the API asynchronous and then run the Django server using the commands below:

```bash
celery -A newsX_backend worker -l info
python manage.py runserver
```

Make sure that RabbitMQ is running before starting celery.

# Service Layer:

![Screenshot from 2023-09-24 18-25-41.png](2VID%20Anything%20to%20video%20in%202%20minutes%20220c16266fa24a7fa6b7276cb55de20e/Screenshot_from_2023-09-24_18-25-41.png)

# Architecture:

![Screenshot from 2023-09-24 18-25-56.png](2VID%20Anything%20to%20video%20in%202%20minutes%20220c16266fa24a7fa6b7276cb55de20e/Screenshot_from_2023-09-24_18-25-56.png)

# [FrontEnd:](https://2vid.tech/)

The Front end is connected to the backend via a google form. Once a user submits the google form it triggers a event in **ZAPIER** which then calls a webhook we have connected Zapier to, Then the video get’s made and is then sent to the users mail id using which he/she has filled the form. 

The google form is wrapped in a nice frontend template to give any new users an idea as to what services we provide and what they can expect from out website. 

**[Please visit our website](https://2vid.tech/)** 

The Code for the front end is in the folder **2vid_landing_page**

![Screenshot from 2023-09-24 18-56-42.png](2VID%20Anything%20to%20video%20in%202%20minutes%20220c16266fa24a7fa6b7276cb55de20e/Screenshot_from_2023-09-24_18-56-42.png)