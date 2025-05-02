# Interactive Thought Simulator

A web application that simulates different thinking patterns and cognitive processes using large language models.

## Features

- Simulate various thought types: Decision Making, Ethical Reasoning, Creative Thinking, Hypothetical Scenarios
- Choose different prompt patterns: Hierarchical Structure, Multiple Perspective, Self-Reflective
- Adjust parameters like depth and detail level
- View thought processes in text and graph formats
- Interactive visualization of thought connections

## Setup Instructions

1. Clone this repository:
git clone <repository-url>
cd thought_simulator

2. Create a virtual environment and install dependencies:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Create a `.env` file with your OpenAI API key:
OPENAI_API_KEY=your_api_key_here

4. Run the application:
streamlit run app.py

5. Open your browser and navigate to `http://localhost:8501`

## Usage

1. Select the type of thinking you want to simulate
2. Choose a prompt pattern that structures the thinking process
3. Adjust parameters to control depth and detail
4. Enter your scenario or question
5. Click "Start Simulation" to generate the thought process
6. View the results in text or graph format

## Customization

- Modify `templates.yaml` to create new prompt templates
- Add new visualization options in `visualizer.py`
- Extend thought parsing logic in `thought_parser.py`

## Requirements

- Python 3.7+
- OpenAI API key
- See requirements.txt for full dependencies