# SHAKTI SHIELD - The drawn of Autonomous defense

## 🎯 Overview

SHAKTI SHIELD is an advanced AI-powered safety assistant designed specifically for women's protection. It leverages a sophisticated multi-agent system to detect threats, manipulation, and dangerous situations in real-time.

## ✨ Key Features

### 🔍 **Intelligent Analysis**
- **Threat Detection**: Identifies harassment, stalking, violence, and blackmail with severity scoring (1-5)
- **Manipulation Detection**: Recognizes love bombing, gaslighting, guilt-tripping, and emotional manipulation
- **Red Flag Analysis**: Detects grooming patterns, sexual coercion, and predatory behavior
- **Reality Check**: Generates "bait" messages to test someone's true intentions

### 🚨 **Emergency Response**
- **Panic Button**: One-touch emergency activation
- **Auto-Recording**: Silent audio/video capture
- **Location Sharing**: Real-time GPS tracking to emergency contacts
- **Evidence Collection**: Automatic timestamped documentation

### ⚖️ **Legal Support**
- Country-specific laws and regulations
- Step-by-step complaint filing guidance
- Police contact information
- Victim rights information

### 🌍 **Multilingual Support**
- Language detection and translation
- Support for Hindi, Spanish, and more
- Speech command recognition

## 🚀 Installation

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
\`\`\`

## 🎨 UI Features

Built with Gradio + TailwindCSS for a modern, responsive interface:

- **Message Analysis Tab**: Analyze text conversations
- **Media Analysis Tab**: Upload images, videos, audio for AI analysis
- **Emergency Tab**: Panic button with emergency protocols
- **Reality Check Tab**: Generate test messages
- **Legal Support Tab**: Get legal guidance by country
- **System Dashboard**: View metrics and observability data

## 🏗️ Architecture

### Multi-Agent System
- **ThreatDetectionAgent**: Analyzes dangerous intent
- **ManipulationDetectionAgent**: Identifies psychological manipulation
- **RedFlagDetectionAgent**: Detects grooming and sexual coercion
- **EvidenceCollectorAgent**: Documents and timestamps evidence
- **LegalSupportAgent**: Provides legal information
- **PanicResponseAgent**: Handles emergency situations
- **MultilingualAgent**: Translates and processes multiple languages
- **RealityCheckAgent**: Generates intention-revealing messages

### Data Flow
1. Input → Language Detection
2. Panic Check (high priority)
3. Parallel Analysis (Threat, Manipulation, Red Flag)
4. Evidence Collection
5. Legal Support Lookup
6. Reality Check Generation (if not emergency)

## 📊 System Monitoring

- Request tracking
- Latency monitoring
- Threat heatmap
- Agent performance metrics

## 🔒 Privacy & Security

- All data encrypted
- SQLite-based persistent storage
- Session-based memory management
- No external data sharing

## 🎓 Built For

This project was created for the Kaggle Capstone Project competition, designed to be in the top 1% of submissions by combining:
- Advanced AI capabilities
- Real-world impact
- Production-ready architecture
- Beautiful, accessible UI

## 💜 Mission

Every woman deserves to feel safe. SHAKTI SHIELD empowers women with AI-driven insights to recognize danger, collect evidence, and take legal action.

## 📝 License

Built with care for women's safety worldwide. 🌍💜
