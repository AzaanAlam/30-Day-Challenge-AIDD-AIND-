import os
import chainlit as cl
import google.generativeai as genai
from pdf_ops import extract_text_from_pdf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

@cl.on_chat_start
async def on_chat_start():
    # Ask the user to upload a PDF file
    files = None
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload a PDF file to begin.",
            accept=["application/pdf"],
            max_size_mb=100,
            timeout=180,
        ).send()

    # Process the first uploaded file
    file = files[0]

    # Inform the user that the file is being processed
    msg = cl.Message(content=f"Processing `{file.name}`...")
    await msg.send()

    # Read the file content from the path
    with open(file.path, "rb") as f:
        file_bytes = f.read()

    # Extract text from the PDF
    text = extract_text_from_pdf(file_bytes)

    # Store the extracted text in the user session
    cl.user_session.set("pdf_text", text)

    # Generate the summary using Gemini
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Summarize the following document for a student:\n\n{text}"
    response = await model.generate_content_async(prompt)

    # Send the summary to the user
    summary_message = cl.Message(content=f"**Summary:**\n{response.text}")
    await summary_message.send()

    # Add the "Create Quiz" action
    await cl.Message(
        content="Would you like to create a quiz from this document?",
        actions=[cl.Action(name="create_quiz", label="Create Quiz", description="Generate a quiz from the PDF content")]
    ).send()

@cl.action_callback("create_quiz")
async def create_quiz(action: cl.Action):
    # Retrieve the original text from the user session
    text = cl.user_session.get("pdf_text")

    if not text:
        await cl.Message(content="Sorry, I couldn't find the document text to create a quiz.").send()
        return

    # Inform the user that the quiz is being created
    await cl.Message(content="Creating your quiz...").send()

    # Generate the quiz using Gemini
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Generate a mixed-style quiz (including multiple-choice and open-ended questions) based on the following text:\n\n{text}"
    response = await model.generate_content_async(prompt)

    # Send the quiz to the user
    await cl.Message(content=response.text).send()