import streamlit as st
from phi.tools.tavily import TavilyTools

from assistant import get_research_assistant

st.set_page_config(
    page_title="MedLink360",
    page_icon="⚕️",
)

def get_latest_health_news():
    """Fetch latest health news using Tavily"""
    tavily = TavilyTools()
    news = tavily.web_search_using_tavily(
        "latest medical news and health discoveries last 24 hours",
        max_results=5
    )
    return news

# Add this new dictionary for quick queries
QUICK_QUERIES = {
    "❤️ Heart Attack Symptoms": "What are the warning signs and symptoms of a heart attack? Latest medical guidelines",
    "🧠 Stroke Signs": "What are the FAST signs of stroke and immediate actions to take?",
    "🦠 COVID-19 Updates": "Latest COVID-19 variants, symptoms, and treatment guidelines",
    "🫁 Asthma Management": "Current asthma management and emergency response guidelines",
    "💊 Diabetes Care": "Type 2 diabetes management, symptoms, and latest treatments",
    "🩺 High Blood Pressure": "Hypertension symptoms, risks, and current treatment approaches",
    "🤒 Flu vs. Cold": "Difference between flu and cold symptoms, when to seek medical attention",
    "🧘 Mental Health": "Common mental health conditions, symptoms, and treatment options"
}

st.title("MedLink360 - AI Medical Assistant")
st.markdown("#### Your Intelligent Healthcare Research Companion 🏥")

def main() -> None:
    # Model
    llm_model = st.sidebar.selectbox(
        "Select Model", options=["llama3-70b-8192", "llama3-8b-8192"]
    )
    # Set assistant_type in session state
    if "llm_model" not in st.session_state:
        st.session_state["llm_model"] = llm_model
    elif st.session_state["llm_model"] != llm_model:
        st.session_state["llm_model"] = llm_model
        st.rerun()

    # Get medical query
    input_topic = st.text_input(
        "🔍 Enter your medical query or condition",
        value="Latest treatments for Type 2 Diabetes",
    )

    # Add a disclaimer
    st.markdown("""
    > **Disclaimer**: This AI assistant provides general medical information for educational purposes only. 
    > Always consult healthcare professionals for medical advice, diagnosis, or treatment.
    """)

    # Button to generate report
    generate_report = st.button("Research Medical Topic")
    if generate_report:
        st.session_state["topic"] = input_topic

    # Quick Medical Queries Section
    st.sidebar.markdown("## ⚡ Quick Medical Queries")
    for label, query in QUICK_QUERIES.items():
        if st.sidebar.button(label, key=f"quick_{label}"):
            st.session_state["topic"] = query
    
    st.sidebar.markdown("---")

    # Latest Health News Sidebar
    st.sidebar.markdown("## 🏥 Latest Health News")
    
    # Add a refresh button for news
    if st.sidebar.button("🔄 Refresh News"):
        if "health_news" in st.session_state:
            del st.session_state["health_news"]
    
    # Get and display latest health news
    if "health_news" not in st.session_state:
        with st.sidebar:
            with st.spinner("Fetching latest health news..."):
                st.session_state["health_news"] = get_latest_health_news()
    
    # Display news with clickable topics
    if "health_news" in st.session_state:
        news_items = st.session_state["health_news"].split("\n")
        for idx, item in enumerate(news_items):
            if item.strip():
                if st.sidebar.button(f"📰 {item[:100]}...", key=f"news_{idx}"):
                    st.session_state["topic"] = item

    if "topic" in st.session_state:
        report_topic = st.session_state["topic"]
        research_assistant = get_research_assistant(model=llm_model)
        tavily_search_results = None

        with st.status("Searching Medical Resources", expanded=True) as status:
            with st.container():
                tavily_container = st.empty()
                tavily_search_results = TavilyTools().web_search_using_tavily(
                    f"medical research: {report_topic}"
                )
                if tavily_search_results:
                    tavily_container.markdown(tavily_search_results)
            status.update(label="Medical Research Complete", state="complete", expanded=False)
        if not tavily_search_results:
            st.error("Sorry, the medical report generation failed. Please try again.")
            return
        
        with st.spinner("Generating Medical Report"):
            final_report = ""
            final_report_container = st.empty()
            for delta in research_assistant.run(tavily_search_results):
                final_report += delta
                final_report_container.markdown(final_report)

    st.sidebar.markdown("---")
    if st.sidebar.button("Start New Search"):
        st.rerun()

main()

    

