import openai
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import PyPDF2
import os, base64, io
from gtts import gTTS
from fpdf import FPDF

#API Keys
OPENAI_API_KEY = ""
ASSEMBLYAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY




st.set_page_config(
    page_title = "Smart Media & Document Assistant: Analyze Videos, Chat with PDFs, Interact with Content & Generate Notes",
    page_icon="🎥📄",
    layout="wide"
)

st.sidebar.title("Welcome To NextGenAI💡")
app_mode = st.sidebar.radio("Choose an option", ["Home", "YouTube Video Analyzer", "Chat with Video", "Chat with PDF", "Notes Generator"])


if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""




#Funtionalities



# Function to get the transcript of a YouTube video from the video URL
def get_video_transcript(video_url):
    try:
        # Extract video ID from YouTube URL
        video_id = YouTube(video_url).video_id
        # Retrieve the transcript using YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # Format the transcript by joining the text from each segment
        formatted_transcript = "\n".join([item['text'] for item in transcript])
        return formatted_transcript
    except Exception as e:
        return f"Error: {str(e)}"

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    try:
        # Read the PDF file using PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pdf_text = ""
        # Extract text from each page of the PDF
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
        return pdf_text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to answer a user's question based on the content of a PDF
def answer_question_from_pdf(question, pdf_text):
    try:
        # Use OpenAI's chat-based API to generate an answer based on the PDF content
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[ 
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Here is a document: {pdf_text}\n\nAnswer the following question: {question}"}
            ],
            max_tokens=200
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Function to convert text into speech using gTTS (Google Text-to-Speech)
def text_to_speech(text, lang="en"):
    try:
        # Generate speech audio in memory using gTTS
        tts = gTTS(text=text, lang=lang)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)  # Reset buffer position
        return audio_buffer
    except Exception as e:
        st.error(f"Error generating speech: {e}")
        return None

# Function to display a PDF file in the Streamlit app
def displayPDF(uploaded_file):
    # Read file as bytes and encode in base64
    bytes_data = uploaded_file.getvalue()
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    # Embed PDF in HTML for viewing in the app
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1020" height="600" type="application/pdf"></iframe>'
    # Display the PDF file in the Streamlit interface
    st.markdown(pdf_display, unsafe_allow_html=True)

# Function to answer a user's question based on a video transcript
def answer_question_from_transcript(question, transcript):
    try:
        # Use OpenAI's chat-based API to generate an answer based on the video transcript
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[ 
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Here is a video transcript: {transcript}\n\nAnswer the following question: {question}"}
            ],
            max_tokens=200
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate a detailed course structure for a given topic and level
def generate_topic_structure(topic, level):
    prompt = (
        f"Generate a detailed course structure for the topic '{topic}' at the {level} level. "
        "The structure should consist of 3 chapters, and each chapter should include 3 subtopics. "
        "Do not provide detailed explanations—only list the chapters and their subtopics. "
        "Use the following format:\n\n"
        "1: 'Chapter Title':\n"
        "   Subtopic 1\n"
        "   Subtopic 2\n"
        "   Subtopic 3\n\n"
        "2: 'Next Chapter Title':\n"
        "   Subtopic 1\n"
        "   Subtopic 2\n"
        "   Subtopic 3\n\n"
        "Continue in this format for all 5 chapters."
    )
    try:
        # Use OpenAI's chat-based API to generate the course structure
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=1000,  # Adjust based on desired response length
            temperature=0.7
        )
        # Extract and return the course structure from the response
        content = response['choices'][0]['message']['content'].strip()
        return content
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate detailed notes for a given subtopic
def generate_notes_for_subtopic(subtopic):
    prompt = (
    f"Provide a detailed explanation for the subtopic '{subtopic}' from chapter '{chapter}'. "
    "Ensure the explanation is comprehensive, covering both theoretical and practical aspects. "
    "Include examples and code where applicable. "
    "Begin your response strictly in this format."
)

    try:
        # Use OpenAI's chat-based API to generate notes for the subtopic
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=1000,  # Adjust based on desired response length
            temperature=0.7
        )
        # Extract and return the generated notes from the response
        content = response['choices'][0]['message']['content'].strip()
        return content
    except Exception as e:
        return f"Error: {str(e)}"


# Initialize session state for storing content progressively
if "full_content" not in st.session_state:
    st.session_state.full_content = ""


# Function to generate PDF from content
def generate_pdf(content):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set font
    pdf.set_font("Arial", size=12)

    # Add content
    pdf.multi_cell(0, 10, content)

    # Specify the output path (ensure the directory exists)
    output_path = os.path.join(os.getcwd(), "generated_notes.pdf")

    # Check if the directory exists, create if it doesn't
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Output the PDF to the specified file
    try:
        pdf.output(output_path)
        return output_path
    except Exception as e:
        return f"Error generating PDF: {str(e)}"





#Application




if app_mode == "Home":
    st.markdown('<div style="background-color:#4caf50; color:white; padding:1px; text-align:center; border-radius:10px;">'
                '<h2>NextGenAI: Analyze Videos, Chat with PDFs, Interact with Content & Generate Notes</h2></div>', unsafe_allow_html=True)

    st.markdown('######')
    st.image(
    "https://media.licdn.com/dms/image/v2/D4D12AQFVlrSPq9aZqQ/article-cover_image-shrink_600_2000/article-cover_image-shrink_600_2000/0/1699617421559?e=2147483647&v=beta&t=s0XUzlT8oxDe0tyA9t-JwHtap_A2vzP9JuPQMZyRPCo", 
    width=1400, 
)

    st.markdown("""
        <style>
        img {
            height: 400px;  /* Specify the desired height here */
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    Welcome to our advanced productivity web application, where we integrate cutting-edge tools designed to streamline your workflow. The app offers two core features that empower you to effortlessly work with YouTube videos and PDF documents. 
    Select a feature below to explore how this web app can enhance your productivity.
""")

    selected_option = st.radio(
        "Choose an option",
        ["YouTube Video Analyzer", "Chat with PDF", "Chat with Video", "Notes Generator"]
    )




    if selected_option == "YouTube Video Analyzer":
        st.subheader("YouTube Video Analyzer")
        st.markdown("""
            **The YouTube Video Analyzer tool helps you save time by automating tasks such as transcription, summarization, and translation.**
        
            ### How it Works:
            1. **Input the YouTube Link**: Paste the URL of any YouTube video into the provided input field.
            2. **Generate the Transcript**: Our tool automatically processes the video and generates a text transcript of the audio.
            3. **Summarize Key Insights**: The transcript is then summarized to highlight essential points and key messages.
            4. **Translate for Global Reach**: You can translate the summarized content into multiple languages (e.g., French, Spanish, Mandarin, and more) for international accessibility.
            
            **Example**:
            - For example, if you have a YouTube video on "Machine Learning Basics," paste the link and get a concise transcript of the key concepts, followed by a summary that highlights the most important points like algorithms, models, and examples.

            **Perfect for:**
            - **Content Creators**: Streamline video production by quickly summarizing long videos.
            - **Researchers**: Extract and analyze key information from long lecture or tutorial videos.
            - **Multilingual Audiences**: Make global content accessible by translating summaries.

            This tool makes your video analysis smarter, faster, and more efficient.
        """)


    elif selected_option == "Chat with PDF":
        st.subheader("Chat with PDF")
        st.markdown("""
            **The "Chat with PDF" feature allows you to interact with your PDF files, making it easier to extract information and answer specific questions directly from the document.**
        
            ### How it Works:
            1. **Upload Your PDF**: Upload any PDF document—whether it’s a research paper, report, or textbook.
            2. **Text Extraction**: The tool extracts the text from the PDF, making it ready for interaction.
            3. **Ask Anything**: Once the text is extracted, you can ask questions related to the document. The AI will process your query and provide an answer based on the content in the PDF.
            4. **Instant Results**: No more scrolling through pages. Get instant, accurate responses to specific sections, paragraphs, or even phrases.
            
            **Example**:
            - If you're reading a research paper on "Climate Change," you can upload the PDF, then ask specific questions like "What are the main causes of climate change?" and get a quick, detailed answer.

            **Perfect for:**
            - **Students**: Quickly find specific information in textbooks or class notes.
            - **Researchers**: Extract and analyze key insights from long academic papers without manually searching.
            - **Professionals**: Interact with reports, manuals, and documents to find key points efficiently.

            With "Chat with PDF," you can engage with your documents in a whole new way—smart, intuitive, and fast!
        """)


    elif selected_option == "Chat with Video":
        st.subheader("Chat with Video")
        st.markdown("""
            **The "Chat with Video" feature allows you to interact with YouTube videos, making it easier to ask questions and get detailed answers based on the video content.**
        
            ### How it Works:
            1. **Input the YouTube Video Link**: Paste the URL of the YouTube video you want to analyze.
            2. **Generate Insights**: The tool processes the video and extracts key details, which allows you to engage with the content.
            3. **Ask Questions**: You can ask questions related to the video, and the AI will provide answers based on the video’s content.
            4. **Instant Answers**: Get accurate, detailed answers to any questions you have about the video.
            
            **Example**:
            - If you're watching a tutorial video on "Python Functions," you can ask questions like "What is a lambda function?" and receive a clear, concise answer based on the video content.

            **Perfect for:**
            - **Educators**: Extract key points or answer questions based on video content to enhance learning.
            - **Students**: Quickly understand important takeaways from lecture videos or tutorials.
            - **Content Consumers**: Dive deeper into videos without the need to re-watch them.

            This tool lets you interact with video content like never before—an intuitive, question-and-answer system right at your fingertips.
        """)


    elif selected_option == "Notes Generator":
        st.subheader("Notes Generator")
        st.markdown("""
            **The Notes Generator tool helps you create custom notes tailored to your learning level by selecting from Beginner, Intermediate, or Advanced modes.**

            ### How it Works:
            1. **Select Your Topics**: Choose the topics you would like notes for. You can select multiple topics based on your interests or requirements.
            2. **Choose Your Learning Mode**: Select your preferred learning mode (Beginner, Intermediate, or Advanced).
            3. **Generate Notes**: The tool will generate a set of notes according to your selected topics and mode. The notes are designed to match your current level of understanding.
            4. **Download Notes**: After generating the notes, you have the option to download them in PDF format for easy reference and offline study.
            
            **Example**:
            - If you select topics like "Python Basics" and choose the Beginner mode, you'll receive simple, easy-to-understand notes with code examples. For an advanced level, the notes will be more detailed, including complex concepts and techniques.

            **Perfect for:**
            - **Students**: Get structured notes at your preferred learning level.
            - **Self-learners**: Deepen your understanding at your own pace.
            - **Professionals**: Quickly generate and refresh your knowledge on any topic.

            With the Notes Generator, you can tailor your study materials to fit your needs and easily download them for offline use.
        """)


    

if app_mode == "YouTube Video Analyzer":
    st.markdown('<div style="background-color:#4caf50; color:white; padding:10px; text-align:center; border-radius:5px;">'
                '<h1>YouTube Video Analyzer 🎥</h1></div>', unsafe_allow_html=True)
    
    st.sidebar.info(""" 
        1. Enter a YouTube video link.
        2. Generate the transcript of the video.
        3. Summarize the transcript.
        4. Translate the summary into any language.
    """)

    youtube_link = st.text_input("Enter YouTube Video Link", placeholder="https://www.youtube.com/watch?v=example")

    if youtube_link:
        
        st.video(youtube_link)  

        if st.button("Generate Transcript"):
            st.info("Fetching transcript from YouTube...")
            transcript = get_video_transcript(youtube_link)
            if "Error:" in transcript:
                st.error(transcript)
            else:
                st.success("Transcript generated successfully!")
                st.session_state.transcript = transcript 

    if st.session_state.transcript:
        with st.container(height=300):
            st.write("Generated Script: ")
            st.markdown(st.session_state.transcript)

        summary_length = st.radio(
            "Select the desired length of the summary:",
            ["Short", "Long", "Very Long"]
        )

        if st.button("Summarize"):
            st.info(f"Summarizing transcript ({summary_length.lower()} summary)...")
            max_tokens = 150 if summary_length == "Short" else 250 if summary_length == "Long" else 350
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  
                    messages=[{
                        "role": "system", "content": "You are a helpful assistant."
                    }, {
                        "role": "user", "content": f"Please summarize the following text into a {summary_length.lower()} summary: {st.session_state.transcript}"
                    }],
                    max_tokens=max_tokens
                )
                summary = response.choices[0].message['content'].strip()
                st.success("Summary generated!")
                st.session_state.summary = summary  
            except Exception as e:
                st.error(f"Summarization failed: {e}")

        if st.session_state.summary:
            st.text_area("Summary", st.session_state.summary, height=300)

            # Text-to-Speech for Summary
            if st.button("🔊 Listen to Summary"):
                audio_data = text_to_speech(st.session_state.summary)
                if audio_data:
                    st.audio(audio_data, format="audio/mp3")

        # Step 3: Translation
        language = st.selectbox(
            "Select Language for Translation",
            ["French", "Spanish", "German", "Chinese", "Japanese", "Italian"]
        )

        if st.button("Translate"):
            st.info(f"Translating summary into {language}...")
            try:
                translation_prompt = f"Translate the following {summary_length.lower()} summary into {language}: {st.session_state.summary}"
                translation_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", 
                    messages=[{"role": "user", "content": translation_prompt}],
                    max_tokens=350
                )
                translated_text = translation_response.choices[0].message['content'].strip()
                st.success(f"Translation completed in {language}!")

                # Save translated text to session state to preserve it
                st.session_state.translated_text = translated_text

            except Exception as e:
                st.error(f"Translation failed: {e}")

        if 'translated_text' in st.session_state:
            # Display Translated Text
            st.text_area("Translated Text", st.session_state.translated_text, height=200)

            # Text-to-Speech for Translated Text
            if st.button(f"🔊 Listen to Translation in {language}"):
                audio_data = text_to_speech(st.session_state.translated_text, lang="fr" if language == "French" else "es" if language == "Spanish" else "de" if language == "German" else "zh" if language == "Chinese" else "ja" if language == "Japanese" else "it")
                if audio_data:
                    st.audio(audio_data, format="audio/mp3")




if app_mode == "Chat with PDF":
    st.markdown('<div style="background-color:#4caf50; color:white; padding:10px; text-align:center; border-radius:5px;">'
                '<h1>Chat with PDF 📄</h1></div>', unsafe_allow_html=True)

    st.sidebar.info(""" 
        1. Upload a PDF document.
        2. Ask questions related to the content of the PDF.
    """)

    uploaded_pdf = st.file_uploader("Upload PDF", type="pdf", help="Only PDF files are supported")

    if uploaded_pdf:
        pdf_text = extract_text_from_pdf(uploaded_pdf)
        displayPDF(uploaded_pdf)
        st.success("PDF text extracted successfully!")

        question = st.text_input("Ask a question related to the document:")

        if question:
            if st.button("Get Answer"):
                st.info("Processing your question...")
                answer = answer_question_from_pdf(question, pdf_text)
                st.markdown(f'<div style="background-color: #2e2e2e; color: #f4f4f9; padding: 20px; font-size: 16px; border-radius: 5px;">{answer}</div>', unsafe_allow_html=True)





if app_mode == "Chat with Video":
    st.title("Chat with Video 🎥")
    youtube_link = st.text_input("Enter YouTube Video Link")

    if youtube_link:
        st.video(youtube_link)
        if st.button("Submit"):
            transcript = get_video_transcript(youtube_link)
            if "Error:" in transcript:
                st.error(transcript)
            else:
                st.session_state.transcript = transcript
                st.success("Video Uploaded successfully!")
    
    if st.session_state.transcript:
        question = st.text_input("Ask a question about the video")
        if st.button("Get Answer"):
            answer = answer_question_from_transcript(question, st.session_state.transcript)
            st.text_area("Answer", answer, height=380)




if app_mode == "Notes Generator":
    st.title("Notes Generator")

    # User input for topic and level
    topic = st.text_input("Enter Topic")  
    level = st.selectbox("Select Level", ["Beginner", "Intermediate", "Advanced"])

    # Button to generate notes and topics
    if st.button("Generate Notes"):
        if topic:
            st.write(f"Generating notes for topic: **{topic}** at the **{level}** level...")

            # Generate topic structure to retrieve subtopics
            topics = generate_topic_structure(topic, level)

            # Display the generated topic structure
            st.subheader(f"Generated Topic Structure for {topic} ({level} Level)")

            # Display the content with chapters and subtopics
            st.write(topics)

            # Split the topic structure into chapters and subtopics
            chapters = topics.split("\n")

            # For each chapter, generate notes for each subtopic
            for chapter in chapters:
                st.subheader(chapter)
                subtopics = chapter.split(",")  # Assuming each chapter has subtopics separated by commas
                for subtopic in subtopics:
                    st.write(subtopic.strip())
                    notes = generate_notes_for_subtopic(subtopic.strip())
                    st.write(notes)
		    # Accumulate content for PDF generation in session state
                    st.session_state.full_content += f"Chapter: {subtopics[0].strip()}\nSubtopic: {subtopic}\n{notes}\n\n"
	     # Option to download PDF if content has been generated
            if st.session_state.full_content:
                st.subheader("Download Notes as PDF")
                pdf_file = generate_pdf(st.session_state.full_content)

                # Provide the option to download the generated PDF
                st.download_button(
                    label="Download PDF",
                    data=open(pdf_file, "rb").read(),
                    file_name="generated_notes.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Please enter a topic to generate notes.")
