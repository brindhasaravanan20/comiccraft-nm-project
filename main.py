from pathlib import Path
from io import BytesIO
import os

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from huggingface_hub import InferenceClient

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as RLImage,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


# --------------------------------------------------
# PROJECT FOLDER
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"


# --------------------------------------------------
# HUGGING FACE
# --------------------------------------------------

HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN:
    hf_client = InferenceClient(
        provider="auto",
        api_key=HF_TOKEN
    )
else:
    hf_client = None


MODEL = "black-forest-labs/FLUX.1-schnell"


# --------------------------------------------------
# CREATE FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="ComicCraft - AI Comic Creator"
)


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

app.mount(
    "/images",
    StaticFiles(directory=IMAGE_DIR),
    name="images"
)


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.get("/")
def home():
    return FileResponse(
        BASE_DIR / "templates" / "index.html"
    )


# --------------------------------------------------
# GENERATE COMIC
# --------------------------------------------------

@app.post("/generate")
async def generate(data: dict):

    story = data.get("story", "").strip()

    character = data.get(
        "character",
        "Hero"
    ).strip() or "Hero"

    setting = data.get(
        "setting",
        "Forest"
    )

    tone = data.get(
        "tone",
        "Adventure"
    )

    art_style = data.get(
        "art_style",
        "Comic"
    )


    # --------------------------------------------------
    # CHECK STORY
    # --------------------------------------------------

    if not story:
        return JSONResponse(
            {
                "error": "Please enter a story prompt."
            },
            status_code=400
        )


    # --------------------------------------------------
    # CHECK HUGGING FACE TOKEN
    # --------------------------------------------------

    if hf_client is None:

        return JSONResponse(
            {
                "error": "Hugging Face token is not configured. Please set HF_TOKEN."
            },
            status_code=500
        )


    # --------------------------------------------------
    # DIFFERENT PROMPT FOR EACH PANEL
    # --------------------------------------------------

    panel_prompts = [

        f"""
        A {art_style.lower()} comic panel.
        Main character: {character}.
        Story: {story}.
        Scene 1: The beginning of the adventure.
        The character is standing at the edge of a {setting},
        preparing to start the journey.
        Mood: {tone}.
        Clear character, cinematic composition,
        colorful comic illustration, detailed background,
        no text, no speech bubbles.
        """,

        f"""
        A {art_style.lower()} comic panel.
        Main character: {character}.
        Story: {story}.
        Scene 2: The character is now deep inside the {setting}.
        The surroundings are different from the previous scene.
        Show the character exploring and discovering something unusual.
        Mood: {tone}.
        Colorful comic illustration, dynamic composition,
        detailed environment, no text, no speech bubbles.
        """,

        f"""
        A {art_style.lower()} comic panel.
        Main character: {character}.
        Story: {story}.
        Scene 3: The character discovers a mysterious glowing
        object or path inside the {setting}.
        Show surprise and curiosity on the character's face.
        Mood: {tone}.
        Dramatic comic lighting, detailed background,
        colorful illustration, no text, no speech bubbles.
        """,

        f"""
        A {art_style.lower()} comic panel.
        Main character: {character}.
        Story: {story}.
        Scene 4: The character reaches a beautiful new location
        beyond the {setting}, completing this part of the adventure.
        Show a hopeful and exciting ending scene.
        Mood: {tone}.
        Beautiful colorful comic illustration,
        cinematic wide composition, detailed background,
        no text, no speech bubbles.
        """
    ]


    # --------------------------------------------------
    # PANEL INFORMATION
    # --------------------------------------------------

    panel_details = [

        {
            "title": "The Forest's Edge",
            "scene":
                f"{character} stands at the edge of the {setting}, "
                "ready to begin the journey.",
            "caption":
                f"The {tone.lower()} begins...",
            "narration":
                f"{character} takes a deep breath and follows the path."
        },

        {
            "title": "Into the Adventure",
            "scene":
                f"{character} explores deeper into the {setting}.",
            "caption":
                "Something unusual appears ahead.",
            "narration":
                f"{character} moves carefully, watching every shadow."
        },

        {
            "title": "The Mysterious Discovery",
            "scene":
                "A strange glowing light appears in the distance.",
            "caption":
                "Something unexpected is waiting ahead.",
            "narration":
                f"{character} follows the mysterious light."
        },

        {
            "title": "A New Adventure",
            "scene":
                f"{character} reaches a beautiful new place beyond the {setting}.",
            "caption":
                "Every story has a new beginning.",
            "narration":
                f"{character} smiles as a new adventure begins."
        }

    ]


    panels = []


    # --------------------------------------------------
    # GENERATE 4 DIFFERENT AI IMAGES
    # --------------------------------------------------

    try:

        for index, prompt in enumerate(panel_prompts):

            print(
                f"Generating AI image for Panel {index + 1}..."
            )


            image = hf_client.text_to_image(
                prompt=prompt,
                model=MODEL
            )


            image_path = (
                IMAGE_DIR
                / f"panel{index + 1}.jpg"
            )


            image.save(
                image_path,
                format="JPEG"
            )


            print(
                f"Panel {index + 1} saved: {image_path}"
            )


            details = panel_details[index]


            panels.append({

                "title": details["title"],

                "image":
                    f"/images/panel{index + 1}.jpg",

                "scene":
                    details["scene"],

                "caption":
                    details["caption"],

                "narration":
                    details["narration"]

            })


    except Exception as e:

        print("Hugging Face error:", e)

        return JSONResponse(
            {
                "error":
                    "Hugging Face image generation failed: "
                    + str(e)
            },
            status_code=500
        )


    # --------------------------------------------------
    # SEND RESULT TO WEBSITE
    # --------------------------------------------------

    return {

        "story": story,

        "character": character,

        "setting": setting,

        "tone": tone,

        "art_style": art_style,

        "panels": panels
    }


# --------------------------------------------------
# EXPORT COMIC AS PDF
# --------------------------------------------------

@app.post("/export-pdf")
async def export_pdf(data: dict):

    panels = data.get(
        "panels",
        []
    )

    character = data.get(
        "character",
        "Hero"
    )

    story = data.get(
        "story",
        ""
    )


    buffer = BytesIO()


    doc = SimpleDocTemplate(

        buffer,

        pagesize=A4,

        rightMargin=36,

        leftMargin=36,

        topMargin=36,

        bottomMargin=36
    )


    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(

        "ComicTitle",

        parent=styles["Title"],

        fontSize=22,

        spaceAfter=14
    )


    heading_style = ParagraphStyle(

        "PanelHeading",

        parent=styles["Heading2"],

        fontSize=15,

        spaceAfter=8
    )


    body_style = ParagraphStyle(

        "Body",

        parent=styles["BodyText"],

        fontSize=10.5,

        leading=14,

        spaceAfter=7
    )


    story_flow = [

        Paragraph(
            "ComicCraft - Your AI Comic",
            title_style
        ),

        Paragraph(
            f"<b>Character:</b> {character}",
            body_style
        ),

        Paragraph(
            f"<b>Story:</b> {story}",
            body_style
        ),

        Spacer(1, 8)
    ]


    # --------------------------------------------------
    # ADD EACH PANEL
    # --------------------------------------------------

    for index, panel in enumerate(panels):

        story_flow.append(

            Paragraph(

                f"Panel {index + 1}: "
                f"{panel.get('title', '')}",

                heading_style
            )
        )


        image_path = (

            IMAGE_DIR
            / f"panel{index + 1}.jpg"
        )


        if image_path.exists():

            story_flow.append(

                RLImage(

                    str(image_path),

                    width=6.3 * inch,

                    height=3.92 * inch
                )
            )


        story_flow.append(
            Spacer(1, 6)
        )


        story_flow.append(

            Paragraph(

                f"<b>Scene:</b> "
                f"{panel.get('scene', '')}",

                body_style
            )
        )


        story_flow.append(

            Paragraph(

                f"<b>Caption:</b> "
                f"{panel.get('caption', '')}",

                body_style
            )
        )


        story_flow.append(

            Paragraph(

                f"<b>Narration:</b> "
                f"{panel.get('narration', '')}",

                body_style
            )
        )


        if index != len(panels) - 1:

            story_flow.append(
                PageBreak()
            )


    doc.build(story_flow)


    buffer.seek(0)


    return StreamingResponse(

        buffer,

        media_type="application/pdf",

        headers={

            "Content-Disposition":
                "attachment; "
                "filename=ComicCraft_Comic.pdf"
        }
    )