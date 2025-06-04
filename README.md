---
title: Code Analysis MCP
emoji: 🧑‍💻
colorFrom: black
colorTo: yellow
sdk: gradio
sdk_version: 5.32.0
app_file: src/app.py
pinned: false
license: apache-2.0
short_description: Automated code reviews for LLMs.
---


# Code Analysis MCP Server

This project is a simple Gradio-based MCP server that provides two basic code analysis functionalities:

-  **Code Analysis Report**: Generates a report with basic information about the provided code.
-  **Code Score**: Provides a simple score for the provided code.

## Setup and Running

1.  Clone the repository.
2.  Navigate to the project directory.
3.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4.  Run the application:

    ```bash
    python src/app.py
    ```

5.  The Gradio interface will be available at `http://127.0.0.1:7860/` and MCP server will be avaible at `http://127.0.0.1:7860/gradio_api/mcp/sse`.

## Connecting to Cursor AI

7. To test the MCP server with Cursor AI, open Cursor Settings, navigate to the "MCP" tab, and click the "+ Add new global MCP server" button.

8. Add the following JSON configuration to the MCP settings file:
```json
{
  "mcpServers": {
    "gradio": {
      "url": "http://127.0.0.1:7860/gradio_api/mcp/sse"
    }
  }
}
```

9. Save the file. You will now see an active MCP server named `gradio` with the tools `Code Analysis Report` and `Code Score`.

To test this MCP server, you can create a new chat in agent mode of the Cursor using (CTRL +T) and ask for a code analysis report (e.g., "analyze this Python code: print('hello')"). Cursor will ask for permission to run the MCP tool. Approve it.

## Tools

### Code Analysis Report

-   **Endpoint**: `/predict`
-   **Description**: Accepts a code string and returns a basic analysis report.

### Code Score

-   **Endpoint**: `/predict_1`
-   **Description**: Accepts a code string and returns a simple code score.
