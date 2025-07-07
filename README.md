# MCP Intelligent Router System

An intelligent AI model routing system based on the Model Context Protocol (MCP), capable of automatically selecting the most suitable AI model for processing based on task characteristics.

## 🌟 Key Features

- **Intelligent Routing**: Automatically selects the most appropriate AI model based on the task type.
- **Multi-modality Support**: Supports various task types including text, mathematical reasoning, and visual understanding.
- **High Reliability**: Comprehensive error handling and retry mechanisms.
- **Extensibility**: Easy to add new AI tools based on the MCP protocol.
- **Configurability**: Supports flexible configuration management.
- **Detailed Logging**: Complete operational log recording.

## 🏗️ Project Structure

```
MCP_Project/
├── src/
│   ├── server/           # MCP Server Module
│   │   ├── mcp_server.py # Main server file
│   │   └── ai_models.py  # AI model manager
│   ├── client/           # MCP Client Module
│   │   └── mcp_client.py # Main client file
│   └── common/           # Common Modules
│       ├── logger.py     # Logging management
│       ├── exceptions.py # Exception definitions
│       ├── utils.py      # Utility functions
│       └── prompts.py    # Prompt management
├── config/
│   └── settings.py       # Configuration management
├── logs/                 # Log file directory
├── tests/                # Test file directory
├── .env                  # Environment variable file
└── README.md             # Project description
```

## 🚀 Quick Start

### 1. Environment Setup

Ensure you have Python 3.8+ and the required dependencies installed:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file by copying `.env.example`:

```env
# API Configuration
BASE_URL=https://api.example.com/v1
API_KEY=your_api_key_here
MODEL=gpt-4o

# Model Configuration
MATH_MODEL=claude-3-5-sonnet-20240620
VISION_MODEL=gpt-4o
LIGHT_MODEL=gpt-4o

# Other Configurations
LOG_LEVEL=INFO
API_TIMEOUT=30
MAX_TOKENS=4000
TEMPERATURE=0.7
```

### 3. Start the System

```bash
# Start the client (which will automatically start the server)
python run.py
```

## 🎯 Supported Task Types

### Math and Code Reasoning (math_code)
- Mathematical proofs and complex calculations
- Code debugging and algorithm optimization
- Logical reasoning and strategic analysis

**Example Use Cases**:
- "Prove the Pythagorean theorem"
- "Optimize the time complexity of this sorting algorithm"

### Vision Understanding (VL_mode)
- Image analysis and description
- Handling of mixed text and image content
- Visual question answering

**Example Use Cases**:
- "Analyze the content of this image"
- "Answer questions based on the picture"

### Lightweight Processing (light_mode)
- Text polishing and editing
- Basic translation and conversion
- Information extraction and summarization

**Example Use Cases**:
- "Polish this text for clarity"
- "Translate this sentence from English to French"

## 🤝 Contribution Guide

1.  Fork the project.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
