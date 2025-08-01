# Dual AI Assistant

## Overview

This repository contains a command-line AI assistant application that implements a **pipeline architecture**: User → ChatGPT → Gemini. The system now includes **file management capabilities** allowing it to read, create, and modify local project files for code generation. ChatGPT processes and analyzes user requests (including file context), then Gemini provides detailed code implementation and technical analysis. The application is built in Python and features a rich terminal interface with both conversation and code generation modes.

## User Preferences

- Preferred communication style: Simple, everyday language
- Language: Korean (한국어) - User prefers Korean language interactions
- Focus: Building powerful AI assistant combining ChatGPT and Gemini

## System Architecture

The application follows a modular Python architecture with clear separation of concerns:

- **Core Logic**: `ai_assistant.py` contains the main `DualAIAssistant` class that handles API interactions
- **Configuration Management**: `config.py` manages environment variables and application settings
- **CLI Interface**: `main.py` provides the command-line interface using Click framework
- **Rich Terminal UI**: Utilizes the Rich library for enhanced terminal output and formatting

The architecture is designed for simplicity and maintainability, with asynchronous processing capabilities for parallel API calls.

## Key Components

### DualAIAssistant Class
- **Purpose**: Core class that manages interactions with both OpenAI and Gemini APIs
- **Functionality**: Handles client initialization, API key management, and parallel query execution
- **Design Choice**: Single class approach for simplicity, with clear separation of API client setup

### Configuration System
- **Purpose**: Centralized configuration management using environment variables
- **Features**: Default values, type conversion, and configuration validation
- **Benefits**: Easy deployment configuration without code changes

### CLI Interface
- **Framework**: Click for robust command-line argument parsing
- **Features**: Interactive mode, verbose logging, single query mode
- **UI Enhancement**: Rich library for beautiful terminal output with panels and columns

### Logging System
- **Implementation**: Python's built-in logging module
- **Output**: Both file logging (`ai_assistant.log`) and console output
- **Configuration**: Configurable log levels and verbose mode support

## Data Flow (Pipeline Architecture)

1. **Input Processing**: User provides query via command line arguments or interactive mode
2. **Client Initialization**: Both OpenAI and Gemini clients are set up with API keys from environment
3. **Stage 1 - ChatGPT Processing**: ChatGPT analyzes user request and provides comprehensive response
4. **Stage 2 - Gemini Enhancement**: Gemini receives ChatGPT's analysis and provides additional detailed insights
5. **Output Display**: Sequential display showing ChatGPT's processing (1단계) and Gemini's response (2단계)
6. **Logging**: All operations and errors are logged for debugging purposes

## External Dependencies

### Core Dependencies
- **openai**: Official OpenAI Python client for ChatGPT API integration
- **google-genai**: Google's Generative AI client for Gemini API access
- **click**: Command-line interface framework for argument parsing and commands
- **rich**: Terminal styling and formatting library for enhanced UI
- **python-dotenv**: Environment variable management (implied for .env file support)

### API Services
- **OpenAI ChatGPT API**: Primary AI model (GPT-4o) requiring OPENAI_API_KEY
- **Google Gemini API**: Secondary AI model (Gemini 2.5-Flash) requiring GEMINI_API_KEY

### Configuration Requirements
- Environment variables for API authentication
- Configurable model parameters (temperature, max tokens, timeout)
- Optional logging configuration

## Deployment Strategy

### Environment Setup
- **API Keys**: Requires both OpenAI and Gemini API keys as environment variables
- **Dependencies**: Standard pip installation of Python packages
- **Python Version**: Compatible with Python 3.7+ (based on async/await usage)

### Configuration Management
- Environment-based configuration for different deployment environments
- Default values provided for non-critical settings
- Validation system to ensure required API keys are present

### Execution Modes
- **Single Query**: Direct command-line usage for one-off queries
- **Interactive Mode**: Continuous conversation mode for extended sessions
- **Batch Processing**: Potential for future enhancement with file input

### Logging and Monitoring
- File-based logging for persistent debugging information
- Console output for real-time feedback
- Configurable log levels for different deployment scenarios

The application is designed for easy deployment across different environments, with minimal setup requirements beyond API key configuration.