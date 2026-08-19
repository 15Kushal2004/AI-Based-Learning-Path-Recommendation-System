# 🤖 AI Learning Path Generator
An AI-driven, interactive platform designed to construct dynamically personalized curriculum maps, track user milestones, and deliver structured educational pathways. 

## 📂 Project Architecture
The workspace follows a strict modular structure, dividing logic, multi-page routing layouts, and data tracking layers:
```text
AI-Learning-Path/
├── .vscode/               # Workspace-specific development configurations
├── core/                  # Core algorithms and AI orchestration engines
├── data/                  # Static training resources or user tracking models
├── pages/                 # Multi-page web view modules and interfaces
├── scripts/               # Automation scripts and background tasks
├── ui/                    # Shared layouts, CSS variables, and components
├── utils/                 # Extensible helper functions and third-party wrappers
├── app.py                 # Primary entry point for application initialization
├── firebase_config.py     # Authentication & persistent cloud storage config
└── requirements.txt       # Hardcoded package dependencies
```

## ✨ Key Features
- **Adaptive Curricula:** Generates learning roadmaps using semantic prompts or skill inputs.
- **Multi-Page Interface:** Smoothly navigates distinct dashboards, path analytics, and timeline states.
- **Firebase Syncing:** Real-time user session authentication and data persistence storage.
- **System Logging:** Active background logging tracking through persistent state engines (`tea_debug.log`).

## 🛠️ Tech Stack
- **Language Framework:** Python 3.9+
- **Database Ecosystem:** Firebase Realtime DB / Firestore
- **Authentication:** Firebase Auth
- **Frontend/UI:** Multi-page layout modules

## 🚀 Getting Started
Follow these steps to spin up the learning path interface on your local machine.

### Prerequisites
Ensure your local system has Python and pip installed securely:
```bash
python --version
pip --version
```

### Installation
1. Clone the remote repository:
   ```bash
   git clone https://github.com
   ```
2. Change into the project directory:
   ```bash
   cd AI-Learning-Path
   ```
3. Install the dependencies listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration
Create a local configuration block or set up your Firebase application inside `firebase_config.py`:
```python
# Provide your web app's Firebase configuration keys
config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_PROJECT_://firebaseapp.com",
    "databaseURL": "https://YOUR_PROJECT_://firebaseio.com",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_PROJECT_://appspot.com",
}
```

## 💡 Usage
Launch the primary runtime script to activate the application server or window loop:
```bash
python app.py
```
Check the generated runtime logs in `tea_debug.log` to troubleshoot server connections, AI generations, or database authentication requests.

## 🤝 Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create.
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
