import streamlit as st
from phi.assistant import Assistant
from phi.llm.groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

def get_service_assistant():
    """Get a service recommendation assistant"""
    return Assistant(
        name="medlink360_service_advisor",
        llm=Groq(id="llama3-70b-8192"),
        description="You are a healthcare service recommendation specialist who helps users find the most suitable therapy or service based on their profile.",
        instructions=[
            "Analyze user responses to recommend the most appropriate service(s)",
            "Consider age, health conditions, and preferences when making recommendations",
            "Provide clear explanations for your recommendations",
            "Be empathetic and professional in your responses",
            "Only recommend from our available services list",
            "Consider safety and medical appropriateness in recommendations",
        ],
        add_to_system_prompt="""
Available Services:
1. Fitness and Body Building
2. Yoga Therapy
3. Reading Therapy
4. Laughing Therapy
5. Audio Therapy
6. Phobia Care AI
7. Medical Research Agent

Service Guidelines:
- Fitness/Bodybuilding: Not recommended for 60+ age group or those with severe health conditions
- Yoga Therapy: Suitable for most age groups, adapt based on flexibility and health
- Reading Therapy: Consider literacy and cognitive ability
- Laughing Therapy: Generally safe for all ages
- Audio Therapy: Universal application with customization
- Phobia Care AI: Suitable for specific phobia treatment
- Medical Research: For those seeking detailed medical information

Consider these factors:
- Age appropriateness
- Physical capabilities
- Health conditions
- Personal preferences
- Safety considerations
""",
    )

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    if "assessment_complete" not in st.session_state:
        st.session_state.assessment_complete = False

def get_next_question(question_number):
    questions = {
        0: {"text": "What is your age?", "type": "number", "key": "age"},
        1: {"text": "What is your gender?", "type": "radio", "options": ["Male", "Female"], "key": "gender"},
        2: {"text": "What is your height (in cm)?", "type": "number", "key": "height"},
        3: {"text": "What is your weight (in kg)?", "type": "number", "key": "weight"},
        4: {"text": "Do you have any medical conditions? (Select all that apply)", "type": "multiselect", 
            "options": [
                "None",
                # Cardiovascular Conditions
                "Heart Disease",
                "High Blood Pressure",
                "High Cholesterol",
                "Irregular Heartbeat",
                
                # Respiratory Conditions
                "Asthma",
                "COPD",
                "Sleep Apnea",
                "Bronchitis",
                
                # Metabolic Conditions
                "Diabetes Type 1",
                "Diabetes Type 2",
                "Thyroid Disorders",
                "Obesity",
                
                # Mental Health Conditions
                "Anxiety",
                "Depression",
                "PTSD",
                "Bipolar Disorder",
                "ADHD",
                "OCD",
                "Eating Disorders",
                
                # Neurological Conditions
                "Migraine",
                "Epilepsy",
                "Multiple Sclerosis",
                "Parkinson's Disease",
                
                # Musculoskeletal Conditions
                "Arthritis",
                "Back Pain",
                "Fibromyalgia",
                "Osteoporosis",
                
                # Digestive Conditions
                "IBS",
                "Acid Reflux",
                "Celiac Disease",
                "Crohn's Disease",
                
                # Child-Specific Conditions
                "Autism",
                "Speech Delay",
                "Learning Disabilities",
                "Developmental Delays",
                
                # Sleep Disorders
                "Insomnia",
                "Narcolepsy",
                "Sleep Walking",
                
                # Allergies & Immunological
                "Food Allergies",
                "Seasonal Allergies",
                "Autoimmune Disorders",
                "Skin Conditions",
                
                # Other Common Conditions
                "Chronic Fatigue",
                "Chronic Pain",
                "Vision Problems",
                "Hearing Problems",
                "Balance Disorders",
                "Other"
            ], 
            "key": "conditions"},
        5: {"text": "Are you comfortable with reading as a therapeutic activity?", "type": "radio", 
            "options": ["Yes", "No"], "key": "reading_comfort"},
        6: {"text": "What are your main health goals?", "type": "multiselect", 
            "options": [
                "Weight Management",
                "Stress Relief",
                "Mental Health",
                "Physical Fitness",
                "Better Sleep",
                "Pain Management",
                "Anxiety Management",
                "Depression Management",
                "Social Skills",
                "Emotional Control",
                "Focus Improvement",
                "Energy Improvement",
                "Balance & Coordination",
                "Flexibility",
                "Respiratory Health",
                "Heart Health",
                "Digestive Health",
                "Immune System Support",
                "General Wellness"
            ], 
            "key": "goals"}
    }
    return questions.get(question_number)

def calculate_bmi(weight, height):
    height_m = height / 100  # Convert cm to m
    bmi = weight / (height_m * height_m)
    return round(bmi, 2)

st.set_page_config(
    page_title="MedLink360",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for Spotify-like theme
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --background: #0F0F0F;
        --card-bg: #1A1A1A;
        --accent: #E50914;
        --text: #FFFFFF;
        --subtext: #E5E5E5;
    }
    
    /* Global styles */
    .main {
        background-color: var(--background);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }
    
    /* Card styling */
    .modern-card {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .modern-card:hover {
        transform: translateY(-2px);
    }
    
    /* Service item styling */
    .service-item {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        transition: all 0.2s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .service-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
        transform: scale(1.02);
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #00C853 !important;
        color: var(--text) !important;
        border-radius: 4px;
        padding: 0.8rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
        width: 200px;
    }
    .stButton>button:hover {
        background-color: #00E676 !important;
        opacity: 0.9;
        transform: translateY(-2px);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: var(--accent);
    }
    
    /* Info boxes */
    .stInfo {
        background-color: var(--card-bg);
        color: var(--text);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.2rem;
        border-radius: 8px;
        font-size: 1.1rem;
    }
    
    /* Headers */
    h1 {
        color: var(--text);
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 2rem !important;
    }
    h3 {
        color: var(--text);
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
    }
    h4 {
        font-size: 1.4rem !important;
        color: var(--subtext);
    }
    
    /* Chat interface */
    .stChatMessage {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        font-size: 1.1rem;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: var(--background);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 5px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Text styles */
    p, li, div {
        font-size: 1.1rem !important;
    }
    small {
        font-size: 0.9rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Main title with Spotify-like styling
st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>⚕️ MedLink360</h1>", unsafe_allow_html=True)

initialize_session_state()

# Progress bar for questionnaire
if not st.session_state.assessment_complete:
    st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
    total_questions = 7  # Total number of questions
    progress = min(st.session_state.current_question / total_questions, 1.0)  # Ensure progress doesn't exceed 1
    st.progress(progress)
    st.markdown(f"#### Question {min(st.session_state.current_question + 1, total_questions)}/{total_questions}")

    current_q = get_next_question(st.session_state.current_question)
    
    if current_q:
        with st.container():
            st.markdown(f"### {current_q['text']}")
            if current_q["type"] == "number":
                value = st.number_input("", min_value=0)
            elif current_q["type"] == "radio":
                value = st.radio("", current_q["options"])
            elif current_q["type"] == "multiselect":
                value = st.multiselect("", current_q["options"])
            
            col1, col2, col3 = st.columns([1,1,1])
            with col2:
                next_button = st.button("Next →", key="next_button", use_container_width=True)
                if next_button:
                    st.session_state.user_data[current_q["key"]] = value
                    if st.session_state.current_question < total_questions - 1:
                        st.session_state.current_question += 1
                    else:
                        # Calculate BMI before completing assessment
                        if "weight" in st.session_state.user_data and "height" in st.session_state.user_data:
                            st.session_state.user_data["bmi"] = calculate_bmi(
                                st.session_state.user_data["weight"],
                                st.session_state.user_data["height"]
                            )
                        st.session_state.assessment_complete = True
                    st.rerun()
    else:
        st.session_state.assessment_complete = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # Display health profile in a card
    st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
    st.markdown("### Your Health Profile 👤")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Age:** {st.session_state.user_data.get('age')}")
        st.info(f"**Gender:** {st.session_state.user_data.get('gender')}")
        st.info(f"**BMI:** {st.session_state.user_data.get('bmi')}")
    
    with col2:
        st.info(f"**Health Conditions:** {', '.join(st.session_state.user_data.get('conditions', []))}")
        st.info(f"**Goals:** {', '.join(st.session_state.user_data.get('goals', []))}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Generate recommendations only once
    if not st.session_state.messages:
        # Prepare context for the assistant
        context = f"""
Based on the user profile:
- Age: {st.session_state.user_data.get('age')}
- Gender: {st.session_state.user_data.get('gender')}
- BMI: {st.session_state.user_data.get('bmi')}
- Health Conditions: {', '.join(st.session_state.user_data.get('conditions', []))}
- Reading Comfort: {st.session_state.user_data.get('reading_comfort')}
- Health Goals: {', '.join(st.session_state.user_data.get('goals', []))}

Analyze this profile and provide:
1. Top 2-3 recommended services from our available services
2. Brief explanation for each recommendation
3. Suggested next steps

Format your response as follows:

**Recommended Services:**
[List the services]

**Brief Explanation for each recommendation:**
[Provide clear, concise explanation for why each service is recommended based on the user's profile]

**Suggested Next Steps:**
[List 2-3 actionable steps the user can take to get started]
"""
        # Get assistant response
        assistant = get_service_assistant()
        response = ""
        with st.spinner("Analyzing your profile..."):
            for chunk in assistant.run(context):
                response += chunk
        
        # Display the response in a card
        with st.container():
            st.markdown("""
                <div class='health-card'>
                    <h3 style='color: #00ADB5;'>Personalized Recommendations 🎯</h3>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(response)
            
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Chat interface for follow-up questions
    st.markdown("""
        <div class='health-card'>
            <h3 style='color: #00ADB5;'>Have Questions? 💭</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if prompt := st.chat_input("Ask about your recommendations..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            assistant = get_service_assistant()
            response = ""
            for chunk in assistant.run(f"User asks: {prompt}\nConsider the previous recommendations and user profile when answering."):
                response += chunk
            st.markdown(response)

    # Reset button with improved styling
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("Start New Assessment ⟲"):
            st.session_state.clear()
            st.rerun()

# Sidebar with improved styling
with st.sidebar:
    st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
    st.markdown("### Available Services 🏥")
    
    services = {
        "💪 Fitness and Body Building": "Professional fitness training",
        "🧘‍♀️ Yoga Therapy": "Therapeutic yoga sessions",
        "📚 Reading Therapy": "Therapeutic reading programs",
        "😊 Laughing Therapy": "Stress relief sessions",
        "🎯 Audio Therapy": "Guided therapeutic sessions",
        "🌈 Phobia Care AI": "AI-assisted phobia treatment",
        "⚕️ Medical Research": "Evidence-based research"
    }
    
    for service, description in services.items():
        st.markdown(f"""
            <div class='service-item'>
                <b style='font-size: 1.1rem'>{service}</b><br>
                <small style='color: var(--subtext)'>{description}</small>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True) 