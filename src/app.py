import gradio as gr
from dotenv import load_dotenv

from code_analyzer.analysis import create_code_analysis_report
from code_analyzer.scoring import create_code_score

load_dotenv()


# Create Gradio interfaces for code analysis
analysis_report_demo = gr.Interface(
    fn=create_code_analysis_report,
    inputs=gr.Textbox(label="Enter Code Here", lines=20),
    outputs=gr.Textbox(label="Analysis Report", lines=20),
    description="Generate a basic code analysis report.",
)

code_score_demo = gr.Interface(
    fn=create_code_score,
    inputs=gr.Textbox(label="Enter Code Here", lines=20),
    outputs=gr.JSON(label="Code Score"),
    description="Generate a basic code score.",
)

# Create tabbed interface
demo = gr.TabbedInterface(
    [analysis_report_demo, code_score_demo],
    ["Code Analysis Report", "Code Score"],
    title="Code Analysis Server",
)

if __name__ == "__main__":
    # Launch the Gradio interface
    demo.launch(share=False, mcp_server=True, debug=True)
