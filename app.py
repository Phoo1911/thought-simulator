import streamlit as st

# ✅ 이 줄은 반드시 가장 먼저 호출되어야 합니다!
st.set_page_config(
    page_title="Interactive Thought Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

import yaml
import os
from dotenv import load_dotenv
from modules.prompt_manager import PromptTemplateManager
from modules.llm_connector import LLMConnector
from modules.thought_parser import parse_thoughts
from modules.visualizer import create_thought_graph, display_thought_graph, display_thoughts
import sys
print("MODULES PATH:", sys.path)

# Load environment variables
load_dotenv()

@st.cache_resource
def load_components():
    prompt_manager = PromptTemplateManager('templates.yaml')
    llm_connector = LLMConnector(api_key=os.getenv('OPENAI_API_KEY'))
    print("[DEBUG] Loaded API Key:", os.getenv('OPENAI_API_KEY'))  
    return prompt_manager, llm_connector

def main():
    prompt_manager, llm_connector = load_components()

    # Custom CSS
    with open('static/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.title("Interactive Thought Simulator")
    st.markdown("Explore different thinking patterns and cognitive processes")

    st.sidebar.title("Simulation Parameters")

    thought_type = st.sidebar.selectbox(
        "Thought Type",
        ["Decision Making", "Ethical Reasoning", "Creative Thinking", "Hypothetical Scenario"]
    )

    pattern_type = st.sidebar.selectbox(
        "Prompt Pattern",
        ["Hierarchical Structure", "Multiple Perspective", "Self-Reflective"]
    )

    depth = st.sidebar.slider("Depth of Thinking", 1, 10, 5)
    detail = st.sidebar.slider("Level of Detail", 1, 10, 5)

    priorities = st.sidebar.multiselect(
        "Priorities",
        ["Logical Consistency", "Emotional Factors", "Historical Precedent", "Future Implications"],
        default=["Logical Consistency", "Future Implications"]
    )

    st.header("Input Scenario")
    scenario = st.text_area(
        "Describe the scenario or question you want to explore",
        height=150,
        placeholder="E.g., Should a company invest in expanding to international markets given current economic uncertainties?"
    )

    if st.button("Start Simulation", type="primary"):
        if not scenario:
            st.error("Please enter a scenario to simulate.")
        else:
            with st.spinner("Simulating thought process..."):
                params = {
                    "scenario": scenario,
                    "depth": depth,
                    "detail": detail,
                    "thought_type": thought_type,
                    "priorities": ", ".join(priorities)
                }

                # ✅ 여기가 핵심 수정
                thought_type_key = thought_type.strip().lower().replace(" ", "_").replace("-", "_")
                pattern_type_key = pattern_type.strip().lower().replace(" ", "_").replace("-", "_")

                prompt = prompt_manager.generate_prompt(
                    thought_type.lower().replace(" ", "_"),      # ✅ 예: Decision Making → decision_making
                    pattern_type.lower().replace(" ", "_"),      # ✅ 예: Hierarchical Structure → hierarchical_structure
                    params
)


                if st.sidebar.checkbox("Show generated prompt"):
                    st.sidebar.code(prompt)

                response = llm_connector.generate(prompt)

                if response:
                    thoughts = parse_thoughts(response)
                    tab1, tab2 = st.tabs(["Text View", "Graph View"])

                    with tab1:
                        display_thoughts(thoughts)

                    with tab2:
                        graph = create_thought_graph(thoughts)
                        display_thought_graph(graph)

                    if st.button("Save Simulation"):
                        st.success("Simulation saved! (Functionality would be implemented in a full version)")
                else:
                    st.error("Failed to generate thought simulation. Please try again.")

    with st.expander("About this Simulator"):
        st.markdown("""
        The Interactive Thought Simulator uses large language models to simulate different thinking patterns and cognitive processes.

        **How to use:**
        1. Select the type of thinking you want to simulate
        2. Choose a prompt pattern that structures the thinking process
        3. Adjust parameters to control depth and detail
        4. Enter your scenario or question
        5. Click "Start Simulation" to generate the thought process

        This tool can be used for educational purposes, decision support, creative exploration, and more.
        """)

if __name__ == "__main__":
    main()
