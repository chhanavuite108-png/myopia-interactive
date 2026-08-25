---
title: Myopia Interactive
emoji: 👁️
colorFrom: blue
colorTo: purple
sdk: gradio
python_version: 3.11
pinned: false
---

# Myopia Interactive

A Gradio classroom visualization for explaining how a myopic eye focuses light in front of the retina. The sliders update the ray diagram as they move.

## Run it on Windows

Open Command Prompt in this folder and run:

```bash
python -m pip install -r requirements.txt
python app.py
```

Then open the local address shown in the terminal (normally http://localhost:8501).

## Deploy to Hugging Face

1. Sign in at [Hugging Face Spaces](https://huggingface.co/spaces).
2. Select **Create new Space**, give it a name such as myopia-interactive, and choose **Gradio** as the Space SDK.
3. Choose **Public** if every student should be able to open the link without signing in.
4. Upload every file and folder from this project, then select **Commit changes**.
5. Wait for the automatic build to finish. Your permanent classroom link will be shown at the top of the Space page.

No model, GPU, or token is needed for this visualization.

## Deploy free on Render

1. Create a free account at https://render.com.
2. Put these project files in a GitHub repository.
3. In Render, select **New** → **Blueprint** and connect that repository.
4. Confirm the free service, then select **Apply**. Render uses render.yaml to install and start the app.

The first visit after about 15 minutes of inactivity can take around a minute while Render wakes the free service. Open the link shortly before class to avoid that delay.

## What changes with each control

- **Object distance** changes the incoming-ray geometry and image distance in real time.
- **Eye optical power** changes focal length: higher power brings the focus closer to the lens.
- **Retina distance / axial length** moves the retinal surface relative to the focus.

The visual model uses the thin-lens relation `1/v = P - 1/u`, where `P` is optical power in dioptres and `u` is object distance in metres.
