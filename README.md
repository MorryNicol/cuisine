# Cuisine App

Cuisine App is a simple application that recommends Chinese cuisine based on the ingredients in your photo. It provides detailed information about the dishes, including finished product photos, gradients, taste, and cooking steps. You can also personalize your recommendations based on taste preferences.

## Features

- Detect ingredients in your photo using **SAM2 + CLIP_CN_VIT_b_16** model.
- Recommend Chinese dishes from a large dataset.
- Show dish details: finished photo, gradient, taste, and cooking steps.
- Personalized recommendations based on taste preferences.

## Installation

To run the app on your local machine, follow these steps:

1. **Clone the repository**  
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app**
   ```bash
   streamlit run streamlit_app.py
   ```
