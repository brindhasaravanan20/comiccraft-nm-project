
# ComicCraft - Simple VS Code Project

This is a beginner-friendly working version of the ComicCraft website.

## What it does
1. Home page collects story prompt, character, setting, tone and art style.
2. Generate Comic opens a comic preview page with 4 panels.
3. Download button creates a real PDF using FastAPI + ReportLab.
4. After download, it opens a success page.
5. Create Another Comic returns to the home page.

## Important
This version uses local demo comic images and simple story text so it can run without an AI API key.
Later, the `/generate` endpoint can be connected to Gemini/Hugging Face for real AI text/image generation.

## Run in VS Code

Open the `ComicCraft_Simple` folder in VS Code.

### 1. Open Terminal

### 2. Install packages
Windows:
```bash
python -m pip install -r requirements.txt
```

### 3. Start the website
```bash
python -m uvicorn app.main:app --reload
```

### 4. Open in browser
```text
http://127.0.0.1:8000
```

### 5. API documentation
```text
http://127.0.0.1:8000/docs
```

## If `uvicorn` is not recognized
Use:
```bash
python -m uvicorn app.main:app --reload
```

## Project structure
```text
ComicCraft_Simple/
│
├── app/
│   ├── main.py
│   ├── images/
│   │   ├── panel1.jpg
│   │   ├── panel2.jpg
│   │   ├── panel3.jpg
│   │   └── panel4.jpg
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── style.css
│       ├── preview.html
│       └── success.html
│
├── requirements.txt
└── README.md
```
