# 🧠 NEUROS: Neural Enhanced Universal Reasoning and Organizational System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/Version-1.0.0-green)](https://github.com/yourusername/neuros)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**NEUROS** is a **local-first AI memory and reasoning system** that provides persistent memory and enhanced reasoning capabilities for personal AI interactions. Think of it as "Your AI's permanent brain" that remembers everything and reasons like you do.

<p align="center">
  <img src="docs/images/neuros_logo.png" alt="NEUROS Logo" width="200"/>
</p>

## 🌟 Key Features

- **Persistent Memory**: Never forget a conversation or context again
- **Local-First Design**: Your data stays on your device by default
- **Multi-Modal Storage**: Store text, code, images, audio, and more
- **Semantic Search**: Find memories based on meaning, not just keywords
- **Hybrid Reasoning**: Neural + symbolic reasoning for accurate answers
- **Adaptive Learning**: Learns from your feedback and preferences
- **Secure & Private**: End-to-end encryption and privacy-first design
- **Multi-Platform**: Desktop apps for Windows, macOS, Linux + Browser Extensions

## 🚀 Quick Start

### Installation

```bash
# Option 1: Install via pip
pip install neuros-personal

# Option 2: Install desktop application
# Download from https://neuros.ai/download

# Option 3: Clone and build from source
git clone https://github.com/yourusername/neuros.git
cd neuros
pip install -e .
```

### Basic Usage

```bash
# CLI interface
neuros remember "Important meeting notes about project X"
neuros recall "project X meeting"
neuros reason "What decisions were made about project X?"

# Python API
from neuros.personal import NEUROSPersonal

# Initialize with default settings
neuros = NEUROSPersonal()

# Store a memory
neuros.remember("Meeting notes: Project X timeline extended to Q2", 
                context={"source": "work", "project": "X"})

# Retrieve relevant memories
memories = neuros.recall("Project X timeline")

# Reason over memories
answer = neuros.reason("When is Project X scheduled to complete?")
```

## 💻 System Requirements

### Minimum Requirements
- **CPU**: 8-core (M2/Ryzen 7)
- **RAM**: 16GB
- **GPU**: Optional (8GB VRAM for acceleration)
- **Storage**: 50GB SSD
- **OS**: Windows 11/macOS 13/Ubuntu 22.04

### Recommended Requirements
- **CPU**: 16-core (M3 Max/Ryzen 9)
- **RAM**: 32GB
- **GPU**: RTX 4070/M3 Max
- **Storage**: 500GB NVMe SSD

## 🏗️ Architecture

NEUROS uses a modular, layered architecture designed for both performance and extensibility:

```
┌───────────────────────────────────────────┐
│               User Interfaces             │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐   │
│  │  CLI    │  │ Desktop │  │ Browser  │   │
│  │         │  │   App   │  │Extension │   │
│  └─────────┘  └─────────┘  └──────────┘   │
└───────────────────────────────────────────┘
               │
┌───────────────────────────────────────────┐
│               Core System                 │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐   │
│  │ Memory  │  │Reasoning│  │ Learning │   │
│  │ System  │  │ Engine  │  │ System   │   │
│  └─────────┘  └─────────┘  └──────────┘   │
└───────────────────────────────────────────┘
               │
┌───────────────────────────────────────────┐
│               Storage Layer               │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐   │
│  │ SQLite  │  │ChromaDB │  │ DuckDB   │   │
│  │(Struct) │  │(Vectors)│  │(Analytics)│   │
│  └─────────┘  └─────────┘  └──────────┘   │
└───────────────────────────────────────────┘
```

## 🔧 Core Components

### Memory System
The memory system manages storage, retrieval, and organization of information:

- **SQLite**: Structured data and metadata
- **ChromaDB**: Vector search and semantic retrieval
- **DuckDB**: Analytical queries and data mining
- **Local Embedding**: Privacy-preserving encoding

### Reasoning Engine
The reasoning engine combines neural and symbolic approaches:

- **Local LLM**: Runs on device for privacy and speed
- **Symbolic Logic**: PyDatalog for rule-based reasoning
- **Multi-Step Reasoning**: Chain-of-thought and verification
- **Memory Integration**: Contextually relevant recall

### Learning System
The learning system adapts to user preferences:

- **Feedback Loop**: Learns from user interactions
- **Pattern Recognition**: Identifies recurring themes
- **Strategy Adaptation**: Evolves reasoning strategies
- **Preference Modeling**: Personalizes responses

## 📦 Deployment Options

### Desktop Application
- **Framework**: Electron + React frontend, FastAPI backend
- **Features**: System tray, global hotkeys, native notifications
- **Packaging**: NSIS (Windows), DMG (macOS), AppImage/Snap (Linux)

### Browser Extension
- **Compatibility**: Chrome, Firefox, Edge
- **Features**: Contextual memory capture, in-page reasoning, keyboard shortcuts
- **Backend**: Communicates with local server

### CLI Tool
- **Interface**: Command-line for power users
- **Integration**: Pipe support, shell aliases
- **Automation**: Scriptable for workflows

## 🔒 Privacy & Security

NEUROS is built with security and privacy as core principles:

- **Local-First**: All data stays on your device by default
- **Encryption**: AES-256 encryption for data at rest
- **No Telemetry**: No usage data collected without consent
- **Data Ownership**: Export or delete your data anytime
- **Access Control**: Optional biometric protection

## 🧩 Extensibility

NEUROS is designed to be extended and customized:

```python
# Example: Custom memory source plugin
from neuros.plugins import MemorySourcePlugin

class GitHubIssuesSource(MemorySourcePlugin):
    """Import GitHub issues as memories"""
    
    def __init__(self, repo_url, api_token=None):
        self.repo_url = repo_url
        self.api_token = api_token
    
    def fetch_memories(self):
        """Fetch issues and convert to memories"""
        # Implementation to fetch GitHub issues
        issues = self._get_github_issues()
        
        # Convert to NEUROS memory format
        memories = []
        for issue in issues:
            memories.append({
                'content': f"Issue #{issue['number']}: {issue['title']}\n{issue['body']}",
                'context': {
                    'source': 'github',
                    'repo': self.repo_url,
                    'issue_id': issue['number'],
                    'labels': issue['labels'],
                    'timestamp': issue['created_at']
                }
            })
            
        return memories
```

## 📊 Analytics

NEUROS includes personal analytics to help you understand your knowledge:

- **Memory Statistics**: Total memories, daily averages, top categories
- **Reasoning Patterns**: Most queried topics, reasoning accuracy
- **Learning Insights**: Personalization level, prediction accuracy

## 🤝 Contributing

Contributions are welcome! Please check out our [Contributing Guide](CONTRIBUTING.md) to get started. Here are some ways to contribute:

- 🐛 **Bug Reports**: File detailed issues
- 💡 **Feature Requests**: Share your ideas
- 🔧 **Pull Requests**: Code contributions
- 📚 **Documentation**: Help improve docs
- 🧪 **Testing**: Help with test coverage

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💰 Pricing

### Personal Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | 1,000 memories/month<br>Basic reasoning (depth: 3)<br>Local storage only<br>Community support |
| **Pro** | $9/month | Unlimited memories<br>Advanced reasoning (depth: 10)<br>Encrypted cloud backup<br>Priority support<br>Custom models |
| **Lifetime** | $299 (one-time) | Everything in Pro<br>Early access to features<br>Source code access<br>Commercial use license |

## 🏢 Enterprise Edition

For organizations needing team collaboration, advanced security, and scale, check out [NEUROS Enterprise Edition](https://neuros.ai/enterprise).

- **Multi-Tenant Architecture**
- **Team Collaboration Features**
- **Enterprise-Grade Security**
- **Advanced Analytics & Insights**
- **Full Integration Ecosystem**

## 📞 Support

- **Documentation**: [https://docs.neuros.ai](https://docs.neuros.ai)
- **Community Forum**: [https://community.neuros.ai](https://community.neuros.ai)
- **Email Support**: support@neuros.ai
- **GitHub Issues**: For bug reports and feature requests

## 🚧 Roadmap

See our [public roadmap](ROADMAP.md) for upcoming features and development plans.

## 📄 Citation

If you use NEUROS in your research, please cite:

```bibtex
@software{neuros2025,
  author = {NEUROS Team},
  title = {NEUROS: Neural Enhanced Universal Reasoning and Organizational System},
  url = {https://github.com/yourusername/neuros},
  version = {1.0.0},
  year = {2025},
}
```

---

<p align="center">
  Built with ❤️ by the NEUROS team
</p>
