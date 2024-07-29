import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from login import login, logout, is_authenticated, get_current_user, change_password
from datetime import datetime
import json

# Set page configuration first
st.set_page_config(page_title="YouTube Summarizer", page_icon="📑", layout="wide")

load_dotenv()  # Load all environment variables

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the prompt for summarization
prompt = """Your task is to summarize the content into concise and to-the-point notes in English of given a transcript from a YouTube video. Make sure to make the notes in English Language. The summary should include headings, subheadings, and key notes. Ensure the summary captures the main points of the video accurately and effectively."""

# Function to extract transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        
        # Show progress bar while extracting transcript
        progress_bar = st.progress(0)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        
        transcript = ""
        for i, entry in enumerate(transcript_text):
            transcript += " " + entry["text"]
            progress_bar.progress((i + 1) / len(transcript_text))
        
        progress_bar.empty()  # Remove progress bar after completion
        return transcript
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None

# Function to generate summary using generative AI
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Function to load history from file
def load_history():
    if os.path.exists("history.json"):
        with open("history.json", "r") as file:
            return json.load(file)
    return {}

# Function to save history to file
def save_history(history):
    with open("history.json", "w") as file:
        json.dump(history, file)

# ---  CSS Styling ---
st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6; /* Set your desired background color here */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333; /* Main Text Color */
    }

    .title {
        text-align: center;
        font-size: 2.5rem;
        color: #4f8ef7; /* Light Blue Title Color */
        margin-bottom: 20px;
    }

    .summary-container {
        background-color: #ffffff;
        border: 1px solid #ddd;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    .summary-container h2 {
        font-size: 1.5rem;
        margin-bottom: 10px;
        color: #333;
    }

    .download-link {
        text-decoration: none;
        color: #4f8ef7; /* Light Blue Link Color */
        font-weight: bold;
    }

    .download-link:hover {
        text-decoration: underline;
    }

    .nav-links {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 20px;
    }

    .nav-links a {
        text-decoration: none;
        color: #4f8ef7; /* Light Blue Link Color */
        font-size: 1.2rem;
    }

    .nav-links a:hover {
        text-decoration: underline;
    }

    /* Style for input fields */
    .stTextInput input {
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
        width: 100%;
        box-sizing: border-box;
    }

    /* Style for buttons */
    .stButton button {
        background-color: #4f8ef7; /* Light Blue Button Color */
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    .stButton button:hover {
        background-color: #337ab7; /* Darker Blue Button Hover Color */
    }

    /* Style for checkboxes */
    .stCheckbox label {
        color: #333;
    }

    /* Style for sidebar */
    .css-1r6slb {
        background-color: #f0f2f6; /* Set your desired sidebar background color here */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Authentication
if not is_authenticated():
    if not login():
        st.stop()
else:
    st.sidebar.header(f"Welcome {st.session_state['username']}")
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()

# App title
st.markdown("<div class='title'>YouTube Summarizer</div>", unsafe_allow_html=True)
st.write("Get concise summaries of YouTube videos from their transcripts.")

# Main app sections
section = st.selectbox("Select Section", ["Summarizer", "History", "Settings"])

if section == "Summarizer":
    # Input section
    youtube_link = st.text_input("Enter YouTube Video Link:", key="youtube_link")
    summary_length = st.slider("Desired Summary Length (words)", min_value=50, max_value=10000, value=150, key="summary_length")
    display_transcript = st.checkbox("Display Full Transcript", key="display_transcript")

    if youtube_link:
        video_id = youtube_link.split("=")[1]
        
        # Display video thumbnail and options
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
        
        if st.button("Get Detailed Notes"):
            with st.spinner("Extracting transcript..."):
                transcript_text = extract_transcript_details(youtube_link)
            
            if transcript_text:
                with st.spinner("Generating summary..."):
                    summary = generate_gemini_content(transcript_text, prompt)
                
                if summary:
                    # Display summary
                    st.markdown("<div class='summary-container'><h2>Detailed Notes:</h2>", unsafe_allow_html=True)
                    st.write(summary[:summary_length])  # Truncate summary
                    
                    # Save to history
                    history = load_history()
                    history_entry = {
                        "video_id": video_id,
                        "youtube_link": youtube_link,
                        "summary": summary[:summary_length],
                        "transcript": transcript_text,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    user_history = history.get(st.session_state['username'], [])
                    user_history.append(history_entry)
                    history[st.session_state['username']] = user_history
                    save_history(history)
                    
                    # Display transcript and download option
                    if display_transcript:
                        st.subheader("Full Transcript:")
                        st.write(transcript_text)
                    
                else:
                    st.error("Failed to generate summary.")
            else:
                st.error("Failed to extract transcript.")

elif section == "History":
    st.header("Summary History")
    history = load_history()
    user_history = history.get(st.session_state['username'], [])
    
    if user_history:
        for entry in user_history:
            st.markdown("<div class='summary-container'><h2>Summary:</h2>", unsafe_allow_html=True)
            st.write(f"**Date:** {entry['timestamp']}")
            st.write(f"**YouTube Link:** {entry['youtube_link']}")
            st.write(f"**Summary:** {entry['summary']}")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("No history available.")

elif section == "Settings":
    st.header("Settings")
    st.subheader("Change Password")
    new_password = st.text_input("New Password", type="password", key="new_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
    if st.button("Change Password"):
        if new_password == confirm_password:
            change_password(st.session_state['username'], new_password)
            st.success("Password changed successfully.")
        else:
            st.error("Passwords do not match.")
