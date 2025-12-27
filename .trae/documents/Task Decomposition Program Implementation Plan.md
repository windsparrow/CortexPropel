# Task Decomposition Program Implementation Plan (Revised)

## 1. Core Design Principle
Leverage the LLM's strong comprehension and long-context capabilities to manage the entire task tree. The LLM will receive both the full existing task tree and new user input, then generate an updated complete task tree in structured JSON format.

## 2. Project Structure
```
cortexpropel/
├── src/
│   ├── __init__.py
│   ├── config.py            # Load existing configuration and model settings
│   ├── task_model.py        # Task tree data models and validation
│   ├── llm_client.py        # LLM integration for task processing
│   ├── task_manager.py      # Task tree file operations
│   └── cli.py               # Command-line interface for testing
├── data/
│   └── task_tree.json       # Task tree storage (complete JSON structure)
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (API keys, model config)
```

## 3. Implementation Steps

### 3.1 Setup and Configuration
1. **Initialize Python environment**
   - Create `requirements.txt` with LangChain, JSON, and other dependencies
   - Set up `.env` file for API keys and model configuration
   - Install required packages

2. **Load existing configuration**
   - Implement `config.py` to load model settings (ByteDance model details)
   - Support environment variables and configuration files
   - Provide default values for development

### 3.2 Task Tree JSON Schema
1. **Define JSON structure**
   ```json
   {
     "id": "root",
     "title": "Root Task",
     "description": "Main project task",
     "status": "pending",
     "created_at": "2025-12-27T10:00:00Z",
     "updated_at": "2025-12-27T10:00:00Z",
     "subtasks": [
       {
         "id": "task-1",
         "title": "Subtask 1",
         "description": "First subtask",
         "status": "pending",
         "created_at": "2025-12-27T10:00:00Z",
         "updated_at": "2025-12-27T10:00:00Z",
         "subtasks": []
       }
     ]
   }
   ```

2. **Implement data validation**
   - Use Pydantic models to validate task tree structure
   - Ensure proper nesting of subtasks
   - Validate required fields and data types

### 3.3 LLM Integration
1. **Configure LangChain with ByteDance model**
   - Set up LangChain with appropriate model parameters
   - Configure API connection to ByteDance model
   - Test basic model connectivity

2. **Create prompt engineering**
   - Design prompts that instruct LLM to:
     - Understand the existing task tree structure
     - Interpret user's new task input
     - Decide where to insert/update tasks in the tree
     - Generate complete updated task tree in JSON format
     - Maintain proper JSON syntax and structure
   - Include examples to guide the LLM's response

3. **Implement response parsing**
   - Extract JSON from LLM response
   - Validate generated JSON structure
   - Handle potential parsing errors gracefully

### 3.4 Task Management Functions
1. **File I/O operations**
   - `load_task_tree()`: Read complete task tree from JSON file
   - `save_task_tree()`: Write updated task tree to JSON file
   - Support initial creation if file doesn't exist

2. **Task processing workflow**
   - `process_task_input()`: Core function that:
     1. Loads existing task tree
     2. Combines with user input to create LLM prompt
     3. Sends prompt to LLM
     4. Parses and validates LLM response
     5. Saves updated task tree

### 3.5 CLI Interface
1. **Simple command-line interaction**
   - Support command: `cortexpropel "Your task description here"`
   - Show success message and summary of changes
   - Support optional `--show` flag to display updated task tree
   - Support `--reset` flag to clear and restart task tree

### 3.6 Testing and Validation
1. **Test scenarios**
   - Initial task tree creation
   - Adding new tasks to appropriate locations
   - Updating existing tasks
   - Adding nested subtasks
   - Handling complex task relationships

2. **Validation checks**
   - Verify JSON structure integrity after each update
   - Ensure all required fields are present
   - Test with various user input formats

## 4. Key Features

### 4.1 Full LLM-Driven Task Management
- No rule-based task assignment logic
- LLM decides task hierarchy and relationships based on context
- Leverages LLM's strong comprehension for natural language processing

### 4.2 Structured JSON Output
- Complete task tree in well-defined JSON format
- Ready for visualization and further processing
- Validated structure ensures consistency

### 4.3 Simple User Interaction
- Natural language input for all operations
- No complex commands or syntax
- Clear feedback on task updates

## 5. Technology Stack
- **Language**: Python
- **Agent Framework**: LangChain
- **LLM**: ByteDance model (using existing configuration)
- **Data Storage**: JSON files
- **Interface**: Command-line
- **Validation**: Pydantic
- **Configuration**: Environment variables

This revised plan focuses on maximizing the LLM's capabilities by providing it with the complete task context, allowing it to make intelligent decisions about task decomposition and organization while maintaining a structured JSON output format.