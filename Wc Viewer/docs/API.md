# API Documentation

## Core Modules

### ChatAIAnalyzer

The main AI analysis engine for processing WhatsApp chats.

#### Methods

##### `__init__()`
Initialize the AI analyzer with default models.

##### `analyze_chat(chat_data: List[Dict]) -> Dict`
Perform comprehensive AI analysis on chat data.

**Parameters:**
- `chat_data`: List of message dictionaries

**Returns:**
- Dictionary containing analysis results

##### `analyze_sentiment(messages: List[str]) -> List[Dict]`
Analyze sentiment of messages using TextBlob.

##### `extract_topics(messages: List[str], n_topics: int = 5) -> List[Dict]`
Extract main topics using TF-IDF and K-means clustering.

##### `ask_question(question: str, chat_data: List[Dict]) -> str`
Answer questions about the chat using semantic similarity.

### ChatParser

Robust parser for WhatsApp chat export files.

#### Methods

##### `parse_chat_file(file_path: str) -> List[Dict]`
Parse a WhatsApp chat export file.

**Parameters:**
- `file_path`: Path to the chat export file

**Returns:**
- List of parsed message dictionaries

##### `validate_chat_data() -> Dict`
Validate the parsed chat data.

**Returns:**
- Validation result dictionary

### WhatsAppChatViewer

Main GUI application class.

#### Methods

##### `run()`
Start the application main loop.

## Data Structures

### Message Dictionary
```python
{
    "timestamp": datetime,
    "sender": str,
    "message": str
}
```

### Analysis Results
```python
{
    "sentiments": List[Dict],
    "topics": List[Dict],
    "patterns": Dict,
    "user_behavior": Dict
}
```
