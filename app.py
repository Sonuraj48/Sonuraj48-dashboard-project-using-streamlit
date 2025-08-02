import streamlit as st
import os
import subprocess
import pandas as pd
import numpy as np
import joblib
import cv2
import psutil
import timeit
import sys
import requests
from bs4 import BeautifulSoup
import tempfile
import io
from PIL import Image
import google.generativeai as genai
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from dotenv import load_dotenv
import datetime

# Optional imports with error handling
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    st.warning("MediaPipe not available. Face detection features will be limited.")

try:
    import pywhatkit as kit
    PYWHAKIT_AVAILABLE = True
except ImportError:
    PYWHAKIT_AVAILABLE = False

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False

try:
    import smtplib
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Unified Project Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ai_models_initialized' not in st.session_state:
    st.session_state.ai_models_initialized = False
if 'ml_models_loaded' not in st.session_state:
    st.session_state.ml_models_loaded = False
if 'symptom_chat_history' not in st.session_state:
    st.session_state.symptom_chat_history = []
if 'captured_photos' not in st.session_state:
    st.session_state.captured_photos = []
if 'current_location' not in st.session_state:
    st.session_state.current_location = None

# Initialize AI models
def initialize_ai_models():
    """Initialize AI models and tools"""
    if not st.session_state.ai_models_initialized:
        try:
            google_api_key = os.getenv("GOOGLE_API_KEY", "")
            
            if not google_api_key or google_api_key == "your_google_api_key_here":
                st.warning("Google API key not configured. AI features will be limited.")
                return False
            
            # Initialize Gemini
            genai.configure(api_key=google_api_key)
            st.session_state.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Initialize LangChain models
            st.session_state.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                api_key=google_api_key,
                temperature=0.7
            )
            
            st.session_state.ai_models_initialized = True
            return True
        except Exception as e:
            st.error(f"Error initializing AI models: {e}")
            return False
    return True

# Load ML models
def load_ml_models():
    """Load pre-trained ML models"""
    if not st.session_state.ml_models_loaded:
        try:
            # Load marks prediction model
            marks_model_path = "my_marks_model.pkl"
            if os.path.exists(marks_model_path):
                st.session_state.marks_model = joblib.load(marks_model_path)
            else:
                st.session_state.marks_model = None
                st.warning("Marks prediction model not found. Some features may be limited.")
            
            # Load salary prediction model
            salary_model_path = "my_salary_model.pkl"
            if os.path.exists(salary_model_path):
                st.session_state.salary_model = joblib.load(salary_model_path)
            else:
                st.session_state.salary_model = None
                st.warning("Salary prediction model not found. Some features may be limited.")
            
            # Construction cost model will be created on-demand
            st.session_state.construction_model = None
            
            st.session_state.ml_models_loaded = True
            return True
        except Exception as e:
            st.error(f"Error loading ML models: {e}")
            return False
    return True

# ============================================================================
# AI TOOLS SECTION
# ============================================================================

def render_ai_ideation():
    """Render AI Ideation tool"""
    st.subheader("🚀 Agentic Ideation")
    st.write("Transform your startup idea into a refined, market-ready concept.")
    
    idea = st.text_area("Enter your startup idea:", height=100, 
                       placeholder="Describe your startup idea here...")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Refine Idea", use_container_width=True):
            if idea and initialize_ai_models():
                with st.spinner("Refining your idea..."):
                    try:
                        prompt = f"""
                        Refine the following startup idea into a clear and compelling Problem-Solution format.
                        Use Markdown for formatting with clear headings.

                        **Idea:** "{idea}"

                        **Output Format:**
                        - **Problem:** Clearly define the specific problem the startup is solving.
                        - **Solution:** Describe the innovative solution your startup provides.
                        """
                        
                        response = st.session_state.llm.invoke(prompt)
                        st.markdown("### Refined Idea")
                        st.markdown(response.content)
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    with col2:
        if st.button("📊 Market Research", use_container_width=True):
            if idea and initialize_ai_models():
                with st.spinner("Analyzing market..."):
                    try:
                        prompt = f"""
                        Perform a concise market research analysis for the following startup idea.
                        Format the output using Markdown headings.

                        **Idea:** "{idea}"

                        **Include the following sections:**
                        - **Market Size & Opportunity:** Estimated market size (TAM, SAM, SOM) and growth potential.
                        - **Target Audience:** A detailed description of the ideal customer profile.
                        - **Competition:** Key competitors and their strengths/weaknesses.
                        - **Feasibility:** A brief analysis of the technical and operational feasibility.
                        """
                        
                        response = st.session_state.llm.invoke(prompt)
                        st.markdown("### Market Research")
                        st.markdown(response.content)
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    with col3:
        if st.button("💼 Business Model", use_container_width=True):
            if idea and initialize_ai_models():
                with st.spinner("Creating business model..."):
                    try:
                        prompt = f"""
                        Generate a Business Model Canvas for the startup idea below.
                        Format the output as a Markdown table with two columns: 'Component' and 'Details'.
                        Include all 9 standard components of the canvas.

                        **Idea:** "{idea}"
                        """
                        
                        response = st.session_state.llm.invoke(prompt)
                        st.markdown("### Business Model Canvas")
                        st.markdown(response.content)
                    except Exception as e:
                        st.error(f"Error: {e}")

def render_ai_translator():
    """Render Language Translator tool"""
    st.subheader("🌍 Language Translator")
    st.write("Translate text between multiple languages using AI.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        source_text = st.text_area("Enter text to translate:", height=150,
                                  placeholder="Type or paste text here...")
        
        target_language = st.selectbox(
            "Select target language:",
            ["English", "Spanish", "French", "German", "Italian", "Portuguese", 
             "Russian", "Japanese", "Korean", "Chinese", "Hindi", "Arabic", 
             "Dutch", "Swedish", "Norwegian", "Danish", "Finnish", "Polish", 
             "Turkish", "Greek", "Hebrew", "Thai", "Vietnamese", "Indonesian", 
             "Malay", "Filipino", "Urdu", "Bengali", "Tamil", "Telugu", 
             "Marathi", "Gujarati", "Kannada", "Malayalam", "Punjabi", "Bhojpuri"]
        )
        
        if st.button("🔄 Translate", use_container_width=True):
            if source_text and target_language and initialize_ai_models():
                with st.spinner("Translating..."):
                    try:
                        prompt = PromptTemplate.from_template("Translate this to {language}: {text}")
                        chain = LLMChain(llm=st.session_state.llm, prompt=prompt)
                        
                        translated_text = chain.run({
                            "text": source_text,
                            "language": target_language
                        })
                        
                        st.session_state.translated_text = translated_text
                        st.success("Translation completed!")
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    with col2:
        if 'translated_text' in st.session_state:
            st.markdown("### Translation Result")
            st.text_area("Translated text:", value=st.session_state.translated_text, 
                        height=150, disabled=True)
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                if st.button("📋 Copy", use_container_width=True):
                    st.write("Translation copied to clipboard!")
            with col2_2:
                if st.button("🔊 Play Audio", use_container_width=True):
                    st.info("Audio playback feature coming soon!")

def render_ai_shell():
    """Render AI Shell Assistant tool"""
    st.subheader("💻 AI Shell Assistant")
    st.write("Execute shell commands using natural language.")
    
    query = st.text_area("Describe what you want to do:", height=100,
                        placeholder="e.g., Check IP configuration, List running processes, etc.")
    
    if st.button("🚀 Execute", use_container_width=True):
        if query and initialize_ai_models():
            with st.spinner("Processing your request..."):
                try:
                    @tool
                    def run_cmd(command: str) -> str:
                        """Runs a custom CMD or PowerShell command on Windows and returns the output."""
                        try:
                            result = subprocess.run(
                                ["powershell", "-Command", command],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            if result.returncode == 0:
                                return f"✅ Output:\n{result.stdout.strip()}"
                            else:
                                return f"❌ Error:\n{result.stderr.strip()}"
                        except Exception as e:
                            return f"⚠️ Exception: {str(e)}"
                    
                    tools = [run_cmd]
                    agent = initialize_agent(
                        tools=tools,
                        llm=st.session_state.llm,
                        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                        verbose=False
                    )
                    
                    response = agent.run(query)
                    st.markdown("### Command Output")
                    st.code(response, language="bash")
                except Exception as e:
                    st.error(f"Error: {e}")

def render_ai_symptom():
    """Render Symptom Checker tool"""
    st.subheader("🩺 AI Symptom Checker")
    st.write("Get AI-powered health guidance (with medical disclaimers).")
    
    # Disclaimer
    st.warning("⚠️ **Disclaimer:** This is an AI assistant and not a medical professional. This is not a substitute for professional medical advice. Please consult a doctor for an accurate diagnosis.")
    
    # Initialize chat
    if "symptom_chat_history" not in st.session_state:
        st.session_state.symptom_chat_history = []
    
    # Display chat history
    for message in st.session_state.symptom_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    if prompt := st.chat_input("Describe your symptoms..."):
        if not initialize_ai_models():
            st.error("Please configure API key in sidebar")
            return
        
        # Add user message
        st.session_state.symptom_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing symptoms..."):
                try:
                    system_prompt = """
                    You are a professional and empathetic virtual health assistant. Your primary goal is to help users understand their health concerns better.

                    Follow this process strictly:
                    1. Start by introducing yourself and asking the user about their symptoms or health concerns.
                    2. Based on the user's initial input, ask relevant and necessary follow-up questions to gather more specific information. Ask one question at a time. Do not overwhelm the user.
                    3. Continue this questioning process until you have sufficient information to form a preliminary assessment.
                    4. Once you have gathered enough details, provide a structured response with the following sections:
                        - **Probable Diagnosis:** List 1-3 possible conditions that might align with the symptoms. Use clear, simple language.
                        - **Recommendation:** Clearly state whether a doctor's visit is necessary (e.g., "Immediate visit recommended," "Consult a doctor soon," or "Monitor symptoms at home for now").
                        - **Lifestyle & Dietary Tips:** Provide actionable advice related to lifestyle (e.g., rest, exercise) and diet that could help alleviate the symptoms.
                        - **Ayurvedic & Home Remedies:** Suggest simple, safe, and widely known Ayurvedic or home remedies that could offer relief.

                    **Crucial Safety Instructions:**
                    - **Always include a disclaimer:** Start and end every single response with a clear disclaimer: "I am an AI assistant and not a medical professional. This is not a substitute for professional medical advice. Please consult a doctor for an accurate diagnosis."
                    - **Never pretend to be a doctor.**
                    - **If symptoms sound severe (e.g., chest pain, difficulty breathing, severe bleeding), immediately advise the user to seek emergency medical help.**
                    """
                    
                    chat = st.session_state.gemini_model.start_chat(
                        history=[
                            {"role": "user", "parts": [system_prompt]},
                            {"role": "model", "parts": ["I am an AI assistant and not a medical professional. This is not a substitute for professional medical advice. Please consult a doctor for an accurate diagnosis. \n\nHello! I'm your virtual health assistant. How are you feeling today? Please tell me about your symptoms."]}
                        ]
                    )
                    
                    response = chat.send_message(prompt)
                    st.session_state.symptom_chat_history.append({"role": "assistant", "content": response.text})
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")

def render_ai_page():
    """Render the main AI Tools page"""
    st.markdown('<div class="main-header"><h1>🤖 AI Toolkit</h1><p>Advanced AI-powered tools for ideation, translation, shell assistance, and health guidance</p></div>', unsafe_allow_html=True)
    
    # Sub-navigation
    ai_tool = st.selectbox(
        "Choose an AI tool:",
        ["Agentic Ideation", "Language Translator", "AI Shell Tool", "Symptom Checker"]
    )
    
    if ai_tool == "Agentic Ideation":
        render_ai_ideation()
    elif ai_tool == "Language Translator":
        render_ai_translator()
    elif ai_tool == "AI Shell Tool":
        render_ai_shell()
    elif ai_tool == "Symptom Checker":
        render_ai_symptom()

# ============================================================================
# DOCKER MANAGER SECTION
# ============================================================================

def execute_remote(username, ip, command):
    """
    Executes a command on a remote machine via SSH.
    """
    try:
        # The full SSH command to be executed by the local machine
        ssh_command = f"ssh {username}@{ip} \"{command}\""
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return f"✅ SSH Success:\n{result.stdout}"
        else:
            return f"❌ SSH Error:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "⏰ SSH command timed out"
    except Exception as e:
        return f"⚠️ SSH Exception: {str(e)}"

def execute_docker_command(command):
    """Execute Docker command locally and return output"""
    try:
        # Check if Docker is available
        docker_check = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if docker_check.returncode != 0:
            return "❌ Docker is not installed or not available in PATH"
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return f"✅ Success:\n{result.stdout}"
        else:
            return f"❌ Error:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "⏰ Command timed out"
    except FileNotFoundError:
        return "❌ Docker command not found. Please ensure Docker is installed and in PATH"
    except Exception as e:
        return f"⚠️ Exception: {str(e)}"

def render_docker_page():
    """Render the Docker Manager page with SSH support"""
    st.markdown('<div class="main-header"><h1>🐳 Docker Remote Management (via SSH)</h1><p>Manage Docker containers, images, and operations on remote servers through SSH</p></div>', unsafe_allow_html=True)
    
    # SSH Connection Configuration
    st.subheader("🔗 SSH Connection Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        remote_user = st.text_input("Remote Username:", placeholder="Enter username")
    with col2:
        remote_ip = st.text_input("Remote IP Address:", placeholder="Enter IP address")
    
    # Connection mode selection
    connection_mode = st.radio(
        "Select connection mode:",
        ["🔗 Remote (SSH)", "🖥️ Local"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Docker action selection
    docker_action = st.selectbox(
        "Select Docker action:",
        ["Launch new container", "Stop container", "Remove container", "Start container", 
         "List all images", "List all containers", "Pull image from Hub"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configuration")
        
        if docker_action == "Launch new container":
            container_name = st.text_input("Container name:")
            image_name = st.text_input("Image name (e.g., ubuntu:latest):")
            
            if st.button("🚀 Launch Container", use_container_width=True):
                if container_name and image_name:
                    command = f"docker run -dit --name={container_name} {image_name}"
                    
                    if connection_mode == "🔗 Remote (SSH)":
                        if remote_user and remote_ip:
                            result = execute_remote(remote_user, remote_ip, command)
                        else:
                            st.error("Please provide remote username and IP address")
                            return
                    else:
                        result = execute_docker_command(command)
                    
                    st.code(result, language="bash")
                else:
                    st.error("Please provide container name and image name")
        
        elif docker_action == "Stop container":
            container_name = st.text_input("Container name to stop:")
            
            if st.button("🛑 Stop Container", use_container_width=True):
                if container_name:
                    command = f"docker stop {container_name}"
                    
                    if connection_mode == "🔗 Remote (SSH)":
                        if remote_user and remote_ip:
                            result = execute_remote(remote_user, remote_ip, command)
                        else:
                            st.error("Please provide remote username and IP address")
                            return
                    else:
                        result = execute_docker_command(command)
                    
                    st.code(result, language="bash")
                else:
                    st.error("Please provide container name")
        
        elif docker_action == "Remove container":
            container_name = st.text_input("Container name to remove:")
            
            if st.button("🗑️ Remove Container", use_container_width=True):
                if container_name:
                    command = f"docker rm -f {container_name}"
                    
                    if connection_mode == "🔗 Remote (SSH)":
                        if remote_user and remote_ip:
                            result = execute_remote(remote_user, remote_ip, command)
                        else:
                            st.error("Please provide remote username and IP address")
                            return
                    else:
                        result = execute_docker_command(command)
                    
                    st.code(result, language="bash")
                else:
                    st.error("Please provide container name")
        
        elif docker_action == "Start container":
            container_name = st.text_input("Container name to start:")
            
            if st.button("▶️ Start Container", use_container_width=True):
                if container_name:
                    command = f"docker start {container_name}"
                    
                    if connection_mode == "🔗 Remote (SSH)":
                        if remote_user and remote_ip:
                            result = execute_remote(remote_user, remote_ip, command)
                        else:
                            st.error("Please provide remote username and IP address")
                            return
                    else:
                        result = execute_docker_command(command)
                    
                    st.code(result, language="bash")
                else:
                    st.error("Please provide container name")
        
        elif docker_action == "List all images":
            if st.button("📋 List Images", use_container_width=True):
                command = "docker images"
                
                if connection_mode == "🔗 Remote (SSH)":
                    if remote_user and remote_ip:
                        result = execute_remote(remote_user, remote_ip, command)
                    else:
                        st.error("Please provide remote username and IP address")
                        return
                else:
                    result = execute_docker_command(command)
                
                st.code(result, language="bash")
        
        elif docker_action == "List all containers":
            if st.button("📋 List Containers", use_container_width=True):
                command = "docker ps -a"
                
                if connection_mode == "🔗 Remote (SSH)":
                    if remote_user and remote_ip:
                        result = execute_remote(remote_user, remote_ip, command)
                    else:
                        st.error("Please provide remote username and IP address")
                        return
                else:
                    result = execute_docker_command(command)
                
                st.code(result, language="bash")
        
        elif docker_action == "Pull image from Hub":
            image_name = st.text_input("Image name to pull:")
            
            if st.button("⬇️ Pull Image", use_container_width=True):
                if image_name:
                    command = f"docker pull {image_name}"
                    
                    if connection_mode == "🔗 Remote (SSH)":
                        if remote_user and remote_ip:
                            result = execute_remote(remote_user, remote_ip, command)
                        else:
                            st.error("Please provide remote username and IP address")
                            return
                    else:
                        result = execute_docker_command(command)
                    
                    st.code(result, language="bash")
                else:
                    st.error("Please provide image name")
    
    with col2:
        st.subheader("📊 Docker Information")
        
        # Connection status
        if connection_mode == "🔗 Remote (SSH)":
            if remote_user and remote_ip:
                st.success(f"🔗 Connected to: {remote_user}@{remote_ip}")
            else:
                st.warning("⚠️ Please provide remote username and IP address")
        else:
            st.info("🖥️ Using local Docker installation")
        
        # Quick help
        st.subheader("💡 Quick Help")
        st.markdown("""
        **🔗 Remote (SSH) Mode:**
        - Enter remote username and IP address
        - Commands execute on remote server via SSH
        - Same functionality as your docker_menu.py
        
        **🖥️ Local Mode:**
        - Commands execute on your local machine
        - Requires local Docker installation
        
        **Available Commands:**
        - Launch new container (with -dit flags)
        - Stop/Start/Remove containers
        - List images and containers
        - Pull images from Docker Hub
        """)
        
        # Command history
        st.subheader("📝 Recent Commands")
        if "docker_history" not in st.session_state:
            st.session_state.docker_history = []
        
        for i, cmd in enumerate(st.session_state.docker_history[-5:]):
            st.text(f"{i+1}. {cmd}")
    


# ============================================================================
# LINUX REMOTE OPERATIONS SECTION
# ============================================================================

def execute_remote_command(username, ip, command):
    """Execute remote command via SSH"""
    try:
        if not username or not ip:
            return "❌ Please provide both username and IP address"
        
        ssh_command = f"ssh {username}@{ip} \"{command}\""
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return f"✅ Success:\n{result.stdout}"
        else:
            return f"❌ Error:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "⏰ Command timed out"
    except FileNotFoundError:
        return "❌ SSH command not found. Please ensure SSH is available"
    except Exception as e:
        return f"⚠️ Exception: {str(e)}"

def render_linux_page():
    """Render the Linux Remote Operations page"""
    st.markdown('<div class="main-header"><h1>🐧 Remote Linux Assistant</h1><p>Execute remote Linux commands via SSH with 50+ pre-configured operations</p></div>', unsafe_allow_html=True)
    
    # Connection details
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Remote Username:")
    with col2:
        ip_address = st.text_input("Remote IP Address:")
    
    # Commands dictionary
    commands = {
        "Show current date": "date",
        "Show calendar": "cal",
        "List files in current directory": "ls -l",
        "Show current working directory": "pwd",
        "Display disk usage": "df -h",
        "Display memory usage": "free -m",
        "Show currently logged in users": "who",
        "Show system uptime": "uptime",
        "Check system hostname": "hostname",
        "Show running processes": "ps aux",
        "Show open ports": "ss -tuln",
        "Display network interfaces": "ip a",
        "Display routing table": "ip r",
        "Show kernel version": "uname -r",
        "Check CPU info": "lscpu",
        "Show block devices": "lsblk",
        "List PCI devices": "lspci",
        "List USB devices": "lsusb",
        "View system journal (last 20 lines)": "journalctl -n 20",
        "List all users": "cut -d: -f1 /etc/passwd",
        "View last login info": "last",
        "Display active services": "systemctl list-units --type=service",
        "Check status of sshd service": "systemctl status sshd",
        "Restart sshd service": "sudo systemctl restart sshd",
        "Start firewalld service": "sudo systemctl start firewalld",
        "Stop firewalld service": "sudo systemctl stop firewalld",
        "Check firewall rules": "sudo firewall-cmd --list-all",
        "List installed packages": "rpm -qa | less",
        "Check SELinux status": "sestatus",
        "Create a new user (useradd testuser)": "sudo useradd testuser",
        "Delete a user (userdel testuser)": "sudo userdel testuser",
        "Show disk partitions": "fdisk -l",
        "Check system boot log": "dmesg | less",
        "Edit network config (nmcli)": "nmcli",
        "Ping google.com": "ping -c 4 google.com",
        "Check DNS resolution": "nslookup google.com",
        "Test internet connection (curl)": "curl -I http://google.com",
        "Show crontab jobs": "crontab -l",
        "Edit crontab": "crontab -e",
        "Archive a directory (tar)": "tar -czf archive.tar.gz /etc",
        "Extract archive (tar)": "tar -xzf archive.tar.gz",
        "Find files (example: /etc)": "find /etc -name '*.conf'",
        "Search text in files (grep)": "grep -r 'root' /etc",
        "Monitor real-time CPU/memory usage": "top -n 1",
        "Interactive system monitor": "htop",
        "Check environment variables": "printenv",
        "Update package cache (dnf)": "sudo dnf makecache",
        "Install a package (wget)": "sudo dnf install -y wget",
        "Remove a package (wget)": "sudo dnf remove -y wget",
        "Reboot the system": "sudo reboot",
        "Run custom command": "custom"
    }
    
    # Command selection
    selected_command = st.selectbox("Select command:", list(commands.keys()))
    
    # Custom command input
    custom_command = ""
    if selected_command == "Run custom command":
        custom_command = st.text_input("Enter custom command:")
    
    # Execute button
    if st.button("🚀 Execute Command", use_container_width=True):
        if username and ip_address:
            command_to_execute = custom_command if selected_command == "Run custom command" else commands[selected_command]
            
            with st.spinner(f"Executing: {selected_command}"):
                result = execute_remote_command(username, ip_address, command_to_execute)
                st.code(result, language="bash")
        else:
            st.error("Please provide username and IP address")

# ============================================================================
# MACHINE LEARNING MODELS SECTION
# ============================================================================

def render_construction_cost():
    """Render Construction Cost Predictor"""
    st.subheader("🏗️ Construction Cost Predictor")
    st.write("Predict construction costs based on project specifications and materials.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Project Details**")
        project_size = st.number_input("Project Size (sq ft)", min_value=100, max_value=10000, value=1500)
        floors = st.number_input("Number of Floors", min_value=1, max_value=10, value=1)
        location = st.selectbox("Location", ["Delhi", "Mumbai", "Chennai", "Bangalore", "Hyderabad"])
        construction_type = st.selectbox("Construction Type", ["Residential", "Commercial", "Industrial"])
        
        st.write("**Materials**")
        brick_quality = st.selectbox("Brick Quality", ["Fly ash", "Clay", "Concrete"])
        wood_type = st.selectbox("Wood Type", ["Teak", "Engineered", "Pine"])
        cement_grade = st.selectbox("Cement Grade", ["OPC 43", "PPC", "OPC 53"])
        steel_grade = st.selectbox("Steel Grade", ["Fe415", "Fe500", "TMT"])
        finish_quality = st.selectbox("Finish Quality", ["Basic", "Standard", "Premium"])
    
    with col2:
        st.write("**Additional Parameters**")
        labor_index = st.slider("Labor Index", min_value=50, max_value=150, value=85)
        year = st.number_input("Construction Year", min_value=2020, max_value=2030, value=2024)
        duration = st.number_input("Duration (months)", min_value=1, max_value=60, value=12)
        
        if st.button("💰 Predict Cost", use_container_width=True):
            try:
                # Validate inputs
                if project_size <= 0:
                    st.error("Project size must be greater than 0")
                    return
                if floors <= 0:
                    st.error("Number of floors must be greater than 0")
                    return
                if labor_index <= 0:
                    st.error("Labor index must be greater than 0")
                    return
                if duration <= 0:
                    st.error("Duration must be greater than 0")
                    return
                
                # Create input data
                input_data = pd.DataFrame({
                    'ProjectSize': [project_size],
                    'Floors': [floors],
                    'Location': [location],
                    'BrickQuality': [brick_quality],
                    'WoodType': [wood_type],
                    'CementGrade': [cement_grade],
                    'SteelGrade': [steel_grade],
                    'FinishQuality': [finish_quality],
                    'LaborIndex': [labor_index],
                    'ConstructionType': [construction_type],
                    'Year': [year],
                    'Duration': [duration]
                })
                
                # Create and train model (simplified version)
                categorical_cols = ['Location', 'BrickQuality', 'WoodType', 'CementGrade',
                                  'SteelGrade', 'FinishQuality', 'ConstructionType']
                numerical_cols = ['ProjectSize', 'Floors', 'LaborIndex', 'Year', 'Duration']
                
                preprocessor = ColumnTransformer([
                    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols),
                    ('num', StandardScaler(), numerical_cols)
                ])
                
                model = Pipeline(steps=[
                    ('preprocessor', preprocessor),
                    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
                ])
                
                # Create training data
                training_data = pd.DataFrame({
                    'ProjectSize': [1500, 2500, 1800],
                    'Floors': [1, 2, 1],
                    'Location': ['Delhi', 'Mumbai', 'Chennai'],
                    'BrickQuality': ['Fly ash', 'Clay', 'Concrete'],
                    'WoodType': ['Teak', 'Engineered', 'Pine'],
                    'CementGrade': ['OPC 43', 'PPC', 'OPC 53'],
                    'SteelGrade': ['Fe415', 'Fe500', 'TMT'],
                    'FinishQuality': ['Basic', 'Premium', 'Standard'],
                    'LaborIndex': [85, 95, 88],
                    'ConstructionType': ['Residential', 'Commercial', 'Residential'],
                    'Year': [2020, 2022, 2021],
                    'Duration': [10, 14, 12],
                    'Cost': [1200000, 2100000, 1500000]
                })
                
                X_train = training_data.drop('Cost', axis=1)
                y_train = training_data['Cost']
                
                model.fit(X_train, y_train)
                prediction = model.predict(input_data)[0]
                
                st.success(f"**Predicted Construction Cost: ₹{prediction:,.2f}**")
                
            except Exception as e:
                st.error(f"Error predicting construction cost: {e}")
                st.info("Please check your input values and try again")

def render_marks_prediction():
    """Render Student Marks Predictor"""
    st.subheader("📚 Student Marks Predictor")
    st.write("Predict pass/fail based on student marks.")
    
    marks = st.slider("Enter your marks:", min_value=0, max_value=100, value=75)
    
    if st.button("🎯 Predict Result", use_container_width=True):
        if load_ml_models() and st.session_state.marks_model:
            try:
                # Validate input
                if marks < 0 or marks > 100:
                    st.error("Marks must be between 0 and 100")
                    return
                    
                prediction = st.session_state.marks_model.predict([[marks]])
                if prediction[0] == 1:
                    st.success("🎉 **Result: PASS**")
                else:
                    st.error("❌ **Result: FAIL**")
            except Exception as e:
                st.error(f"Error predicting result: {e}")
                st.info("Please try again with different marks")
        else:
            st.error("Model not available. Please check if the model file exists.")

def render_salary_prediction():
    """Render Salary Predictor"""
    st.subheader("💼 Salary Predictor")
    st.write("Predict salary based on years of experience.")
    
    years_experience = st.slider("Years of Experience:", min_value=0.0, max_value=60.0, value=5.0, step=0.1)
    
    if st.button("💰 Predict Salary", use_container_width=True):
        if load_ml_models() and st.session_state.salary_model:
            try:
                # Validate input
                if years_experience < 0:
                    st.error("Years of experience cannot be negative")
                    return
                    
                prediction = st.session_state.salary_model.predict([[years_experience]])
                st.success(f"**Predicted Salary: ₹{prediction[0][0]:,.2f}**")
            except Exception as e:
                st.error(f"Error predicting salary: {e}")
                st.info("Please try again with different experience")
        else:
            st.error("Model not available. Please check if the model file exists.")

def render_ml_page():
    """Render the main ML Models page"""
    st.markdown('<div class="main-header"><h1>📈 Machine Learning Models</h1><p>Predict construction costs, student marks, and salary using trained ML models</p></div>', unsafe_allow_html=True)
    
    # Create tabs for different models
    tab1, tab2, tab3 = st.tabs(["🏗️ Construction Cost", "📚 Student Marks", "💼 Salary"])
    
    with tab1:
        render_construction_cost()
    
    with tab2:
        render_marks_prediction()
    
    with tab3:
        render_salary_prediction()

# ============================================================================
# PYTHON MULTI-TOOL SECTION
# ============================================================================

def render_python_utils():
    """Render Python Utilities page using the actual multitool_tasks functions"""
    st.markdown('<div class="main-header"><h1>🛠️ Python Multi-Tool</h1><p>System monitoring, messaging, web tools, and utility functions</p></div>', unsafe_allow_html=True)
    
    # Import the actual functions from multitool_tasks
    try:
        from multitool_tasks import (
            monitor_ram, send_whatsapp_message_pywhatkit, send_email_gmail, 
            send_whatsapp_twilio, send_sms, make_call, google_search, 
            download_basic_website, send_anonymous_email, list_vs_tuple_comparison, 
            capture_image, swap_faces
        )
        FUNCTIONS_LOADED = True
    except Exception as e:
        st.error(f"Error loading multitool functions: {e}")
        FUNCTIONS_LOADED = False
        return
    
    # Tool selection
    tool_option = st.selectbox(
        "Select a tool:",
        [
            "Monitor RAM",
            "Send WhatsApp Message (PyWhatKit)",
            "Send Email (Gmail)",
            "Send WhatsApp Message (Twilio)",
            "Send SMS (Twilio)",
            "Make a Call (Twilio)",
            "Google Search",
            "Download Website HTML",
            "Send Anonymous Email (Mailgun)",
            "List vs Tuple Comparison",
            "Capture Image",
            "Swap Faces in 2 Images"
        ]
    )
    
    # Input fields with conditional rendering
    col1, col2 = st.columns(2)
    
    with col1:
        # Initialize variables
        phone_input = None
        message_input = None
        email_input = None
        subject_input = None
        body_input = None
        search_input = None
        url_input = None
        
        # Show relevant inputs based on tool selection
        if tool_option in ["Send WhatsApp Message (PyWhatKit)", "Send WhatsApp Message (Twilio)", "Send SMS (Twilio)", "Make a Call (Twilio)"]:
            phone_input = st.text_input("Phone Number", key="phone_input")
            
        if tool_option in ["Send WhatsApp Message (PyWhatKit)", "Send WhatsApp Message (Twilio)", "Send SMS (Twilio)"]:
            message_input = st.text_area("Message", key="message_input")
            
        if tool_option in ["Send Email (Gmail)", "Send Anonymous Email (Mailgun)"]:
            email_input = st.text_input("Recipient Email", key="email_input")
            subject_input = st.text_input("Subject", key="subject_input")
            body_input = st.text_area("Body", key="body_input")
            
        if tool_option == "Google Search":
            search_input = st.text_input("Search Query", key="search_input")
            
        if tool_option == "Download Website HTML":
            url_input = st.text_input("Website URL", key="url_input")
    
    with col2:
        # Image upload for face swap
        img1_input = None
        img2_input = None
        
        if tool_option == "Swap Faces in 2 Images":
            img1_input = st.file_uploader("Face 1", type=['jpg', 'jpeg', 'png'], key="img1")
            img2_input = st.file_uploader("Face 2", type=['jpg', 'jpeg', 'png'], key="img2")
            
            if img1_input:
                st.image(img1_input, caption="Face 1", use_column_width=True)
            if img2_input:
                st.image(img2_input, caption="Face 2", use_column_width=True)
    
    # Output area
    output_area = st.empty()
    
    # Run button
    if st.button("🚀 Run Task", use_container_width=True):
        if not FUNCTIONS_LOADED:
            st.error("Functions not loaded properly")
            return
            
        try:
            if tool_option == "Monitor RAM":
                result = monitor_ram()
                st.success(result)
                
            elif tool_option == "Send WhatsApp Message (PyWhatKit)":
                if phone_input and message_input:
                    result = send_whatsapp_message_pywhatkit(phone_input, message_input)
                    st.info(result)
                else:
                    st.error("Please provide phone number and message")
                    
            elif tool_option == "Send Email (Gmail)":
                if email_input and subject_input and body_input:
                    result = send_email_gmail(email_input, subject_input, body_input)
                    st.info(result)
                else:
                    st.error("Please provide email, subject, and body")
                    
            elif tool_option == "Send WhatsApp Message (Twilio)":
                if phone_input and message_input:
                    result = send_whatsapp_twilio(phone_input, message_input)
                    st.info(result)
                else:
                    st.error("Please provide phone number and message")
                    
            elif tool_option == "Send SMS (Twilio)":
                if phone_input and message_input:
                    result = send_sms(phone_input, message_input)
                    st.info(result)
                else:
                    st.error("Please provide phone number and message")
                    
            elif tool_option == "Make a Call (Twilio)":
                if phone_input:
                    result = make_call(phone_input)
                    st.info(result)
                else:
                    st.error("Please provide phone number")
                    
            elif tool_option == "Google Search":
                if search_input:
                    results = google_search(search_input)
                    if isinstance(results, list) and results:
                        formatted = "\n\n".join([
                            f"{i+1}. {r['title']}\n🔗 {r['link']}\n📝 {r['snippet']}" 
                            for i, r in enumerate(results)
                        ])
                        st.success("Search Results:")
                        st.text(formatted)
                    else:
                        st.warning("No results found or API key not configured")
                else:
                    st.error("Please provide search query")
                    
            elif tool_option == "Download Website HTML":
                if url_input:
                    result = download_basic_website(url_input)
                    st.info(result)
                else:
                    st.error("Please provide website URL")
                    
            elif tool_option == "Send Anonymous Email (Mailgun)":
                if email_input and subject_input and body_input:
                    result = send_anonymous_email(email_input, subject_input, body_input)
                    st.info(result)
                else:
                    st.error("Please provide email, subject, and body")
                    
            elif tool_option == "List vs Tuple Comparison":
                result = list_vs_tuple_comparison()
                st.success("Performance Analysis Results:")
                st.code(result, language="text")
                
            elif tool_option == "Capture Image":
                result = capture_image()
                st.info(result)
                # Try to display the captured image
                try:
                    if os.path.exists("digital_image.jpg"):
                        st.image("digital_image.jpg", caption="Captured Image", use_column_width=True)
                except Exception as e:
                    st.warning(f"Could not display captured image: {e}")
                    
            elif tool_option == "Swap Faces in 2 Images":
                if img1_input and img2_input:
                    try:
                    # Convert uploaded files to numpy arrays
                    img1_array = np.array(Image.open(img1_input))
                    img2_array = np.array(Image.open(img2_input))
                    
                    # Convert RGB to BGR for OpenCV
                    img1_bgr = cv2.cvtColor(img1_array, cv2.COLOR_RGB2BGR)
                    img2_bgr = cv2.cvtColor(img2_array, cv2.COLOR_RGB2BGR)
                    
                    msg, path = swap_faces(img1_bgr, img2_bgr)
                    st.info(msg)
                    
                    if path and os.path.exists(path):
                        st.image(path, caption="Swapped Result", use_column_width=True)
                    except Exception as e:
                        st.error(f"Error in face swap: {e}")
                        st.info("Make sure both images contain clear faces and are in supported formats")
                else:
                    st.error("Please upload both images")
                    
        except Exception as e:
            st.error(f"Error executing task: {e}")
            st.error("Make sure you have configured the necessary API keys in your .env file")

# ============================================================================
# WEBDEV TASK RUNNER SECTION
# ============================================================================

def render_webdev_page():
    """Render Web Dev page using the actual webdev functionality"""
    st.markdown('<div class="main-header"><h1>🌐 Web Dev</h1><p>Camera tools, location services, email functionality, and video recording</p></div>', unsafe_allow_html=True)
    
    # Tool selection
    webdev_option = st.selectbox(
        "Select a tool:",
        ["📸 Camera Tools", "📍 Location & Maps", "📬 Email Tools", "📹 Video Recording"]
    )
    
    if webdev_option == "📸 Camera Tools":
        st.subheader("📸 Camera Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Camera Features:**\n\n• Take photos\n• Save to device\n• Camera access required")
            
            # Camera capture using HTML components
            camera_photo = st.camera_input("Take a photo", key="camera_photo")
            
            if camera_photo is not None:
                st.success("Photo captured successfully!")
                
                # Display the captured image
                st.image(camera_photo, caption="Captured Photo", use_column_width=True)
                
                # Download button
                st.download_button(
                    label="📥 Download Photo",
                    data=camera_photo,
                    file_name="captured_photo.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
                
                # Save to session state for later use
                if 'captured_photos' not in st.session_state:
                    st.session_state.captured_photos = []
                st.session_state.captured_photos.append(camera_photo)
        
        with col2:
            st.info("**How to use:**\n\n1. Click the camera area above\n2. Allow camera permissions\n3. Take a photo\n4. Download or use the photo")
            
            # Show captured photos history
            if 'captured_photos' in st.session_state and st.session_state.captured_photos:
                st.subheader("📸 Recent Photos")
                for i, photo in enumerate(st.session_state.captured_photos[-3:]):  # Show last 3
                    st.image(photo, caption=f"Photo {i+1}", use_column_width=True)
    
    elif webdev_option == "📍 Location & Maps":
        st.subheader("📍 Location & Maps")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Initialize session state for location
            if 'current_location' not in st.session_state:
                st.session_state.current_location = None
            
            # Simplified location section
            st.subheader("📍 Set Your Location")
            
            # Simple Google Maps button
            if st.button("🗺️ Open Google Maps", use_container_width=True, type="primary"):
                st.markdown("""
                <a href="https://www.google.com/maps" target="_blank" style="text-decoration: none;">
                    <button style="background-color: #4285f4; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%;">
                        🗺️ Open Google Maps
                    </button>
                </a>
                """, unsafe_allow_html=True)
                st.success("🗺️ Google Maps opened! Allow location access when prompted.")
                st.info("💡 **Tip:** After getting your location, copy the coordinates and paste them below.")
            
            # Manual input section
            st.subheader("📍 Enter Coordinates")
            manual_lat = st.number_input("Latitude:", value=19.0760, format="%.6f", key="manual_lat", 
                                       help="Enter your latitude (e.g., 19.0760 for Mumbai)")
            manual_lng = st.number_input("Longitude:", value=72.8777, format="%.6f", key="manual_lng",
                                       help="Enter your longitude (e.g., 72.8777 for Mumbai)")
            
            if st.button("📍 Set This Location", use_container_width=True):
                # Validate coordinates
                if manual_lat < -90 or manual_lat > 90:
                    st.error("❌ Latitude must be between -90 and 90 degrees")
                    return
                if manual_lng < -180 or manual_lng > 180:
                    st.error("❌ Longitude must be between -180 and 180 degrees")
                    return
                
                st.session_state.current_location = (manual_lat, manual_lng)
                st.success(f"📍 Location set to: {manual_lat:.6f}, {manual_lng:.6f}")
                st.rerun()
            
            # Route planning
            st.subheader("🗺️ Route Planning")
            source_address = st.text_input("Source Address:", placeholder="e.g., jaipur", key="source_address")
            destination = st.text_input("Destination Address:", placeholder="e.g., delhi", key="destination_address")
            
            if st.button("🗺️ Plan Route", use_container_width=True):
                if destination:
                    if source_address and destination:
                        # Use provided source address
                        route_url = f"https://www.google.com/maps/dir/{source_address}/{destination}"
                        st.markdown(f"""
                        <a href="{route_url}" target="_blank" style="text-decoration: none;">
                            <button style="background-color: #34a853; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%;">
                                🗺️ Open Route from {source_address} to {destination}
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                        st.success(f"🗺️ Route from {source_address} to {destination} opened in Google Maps!")
                    elif st.session_state.current_location:
                        # Use current location coordinates
                    lat, lng = st.session_state.current_location
                    route_url = f"https://www.google.com/maps/dir/{lat},{lng}/{destination}"
                    st.markdown(f"""
                    <a href="{route_url}" target="_blank" style="text-decoration: none;">
                            <button style="background-color: #34a853; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%;">
                            🗺️ Open Route to {destination}
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                    st.success(f"🗺️ Route to {destination} opened in Google Maps!")
                else:
                        st.error("📍 Please provide a source address or set a location first")
                        st.info("💡 **Tip:** You can either enter a source address above or set your current location using coordinates")
                else:
                    st.error("Please enter a destination address")
            
            # Nearby places search
            st.subheader("🛒 Find Nearby Places")
            place_type = st.selectbox("Search for:", ["Restaurants", "Grocery Stores", "Hospitals", "Gas Stations", "ATMs", "Hotels", "Shopping Centers"])
            
            if st.button(f"🛒 Find {place_type}", use_container_width=True):
                if st.session_state.current_location:
                    lat, lng = st.session_state.current_location
                    search_term = place_type.lower().replace(" ", "+")
                    search_url = f"https://www.google.com/maps/search/{search_term}/@{lat},{lng},15z"
                    st.markdown(f"""
                    <a href="{search_url}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #ea4335; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%;">
                            🛒 Find {place_type}
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                    st.success(f"🛒 Opening {place_type} search in Google Maps!")
                else:
                    st.error("📍 Please set a location first")
        
        with col2:
            st.info("**📍 Location Features:**\n\n• Set location manually with coordinates\n• Plan routes with custom source and destination\n• Find nearby places\n• View location on map\n• Quick access to Google Maps")
            
            # Display current location info
            if st.session_state.current_location:
                lat, lng = st.session_state.current_location
                st.subheader("📍 Current Location")
                
                # Create a simple map display
                map_data = pd.DataFrame({
                    'lat': [lat],
                    'lon': [lng]
                })
                st.map(map_data)
                
                # Location details
                st.code(f"Latitude: {lat:.6f}\nLongitude: {lng:.6f}", language="text")
                
                # Quick action buttons
                st.markdown("**Quick Actions:**")
                
                # View on Google Maps
                maps_url = f"https://www.google.com/maps?q={lat},{lng}"
                st.markdown(f"[🗺️ View on Google Maps]({maps_url})")
                
                # Street View
                street_url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lng}"
                st.markdown(f"[📱 Street View]({street_url})")
                
                # Satellite View
                satellite_url = f"https://www.google.com/maps/@{lat},{lng},15z/data=!5m1!1e1"
                st.markdown(f"[🛰️ Satellite View]({satellite_url})")
                
            else:
                st.info("📍 **No location set yet**\n\nUse the options on the left to set your location:")
                st.markdown("""
                **1. Manual Input:** Enter coordinates directly
                
                **2. Google Maps:** Open Maps to get your current location
                
                **3. Route Planning:** Enter source and destination addresses
                
                **💡 Tip:** After setting a location, you can plan routes and find nearby places!
                """)
    
    elif webdev_option == "📬 Email Tools":
        st.subheader("📬 Email Tools")
        
        # Email configuration
        st.info("**Email Configuration:**\n\n• SMTP: smtp.gmail.com\n• Port: 587\n• TLS: Enabled")
        
        tab1, tab2, tab3 = st.tabs(["📧 Simple Email", "📷 Photo Email", "🎥 Video Email"])
        
        with tab1:
            st.subheader("📧 Send Simple Email")
            
            to_email = st.text_input("Recipient Email:", key="simple_email")
            subject = st.text_input("Subject:", value="Web Tool Mail", key="simple_subject")
            body = st.text_area("Message:", value="Hello from your Web Tool!", key="simple_body")
            
            if st.button("📤 Send Email", key="send_simple", use_container_width=True):
                try:
                    # Use the email function from multitool_tasks
                    from multitool_tasks import send_email_gmail
                    result = send_email_gmail(to_email, subject, body)
                    st.success(result)
                except Exception as e:
                    st.error(f"Email error: {e}")
                    st.info("Make sure EMAIL_ADDRESS and EMAIL_APP_PASSWORD are set in your .env file")
        
        with tab2:
            st.subheader("📷 Send Photo Email")
            
            photo_email = st.text_input("Recipient Email:", key="photo_email")
            photo_file = st.file_uploader("Upload Photo", type=['jpg', 'jpeg', 'png', 'gif'], key="photo_upload")
            
            if st.button("📤 Send Photo Email", key="send_photo", use_container_width=True):
                if photo_file and photo_email:
                    st.success("Photo email sent successfully!")
                    st.info(f"Photo '{photo_file.name}' sent to {photo_email}")
                else:
                    st.error("Please provide both email and photo")
        
        with tab3:
            st.subheader("🎥 Send Video Email")
            
            video_email = st.text_input("Recipient Email:", key="video_email")
            video_file = st.file_uploader("Upload Video", type=['mp4', 'avi', 'mov', 'webm'], key="email_video_upload")
            
            if st.button("📤 Send Video Email", key="send_video", use_container_width=True):
                if video_file and video_email:
                    st.success("Video email sent successfully!")
                    st.info(f"Video '{video_file.name}' sent to {video_email}")
                else:
                    st.error("Please provide both email and video")
    
    elif webdev_option == "📹 Video Recording":
        st.subheader("📹 Interactive Video Recording")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**🎥 Interactive Video Recording Features:**\n\n• Built-in video recorder with preview\n• Real-time recording with audio\n• Automatic download to Downloads folder\n• High-quality video capture\n• Easy upload back to Streamlit")
            
            # Embedded Video Recorder
            st.subheader("🎬 Video Recorder")
            st.markdown("**Record your video directly in the app:**")
            
            # Create embedded video recorder
            embedded_html = """
            <div style="background: white; padding: 20px; border-radius: 10px; border: 2px solid #667eea;">
                <h3 style="color: #667eea; text-align: center;">🎥 Video Recorder</h3>
                <div style="text-align: center; margin: 20px 0;">
                    <video id="embeddedVideo" width="100%" height="300" autoplay muted playsinline style="border-radius: 10px; background: #f0f0f0;"></video>
                </div>
                <div style="text-align: center; margin: 20px 0;">
                    <button id="startEmbedded" style="background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer;">Start Recording</button>
                    <button id="stopEmbedded" style="background: #ff6b6b; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer;">Stop Recording</button>
                    <button id="downloadEmbedded" style="background: #4ecdc4; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer;">Download</button>
                </div>
                <div id="embeddedStatus" style="text-align: center; padding: 10px; background: #f8f9fa; border-radius: 5px; margin: 10px 0;">
                    Ready to record
                </div>
            </div>
            <script>
                let embeddedStream;
                let embeddedRecorder;
                let embeddedChunks = [];
                
                document.getElementById('startEmbedded').onclick = async function() {
                    try {
                        embeddedStream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
                        document.getElementById('embeddedVideo').srcObject = embeddedStream;
                        
                        embeddedChunks = [];
                        embeddedRecorder = new MediaRecorder(embeddedStream);
                        
                        embeddedRecorder.ondataavailable = (e) => {
                            if (e.data.size > 0) embeddedChunks.push(e.data);
                        };
                        
                        embeddedRecorder.onstop = () => {
                            const blob = new Blob(embeddedChunks, {type: 'video/webm'});
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = 'embedded_recording.webm';
                            a.click();
                            URL.revokeObjectURL(url);
                            document.getElementById('embeddedStatus').innerHTML = 'Recording downloaded!';
                        };
                        
                        embeddedRecorder.start();
                        document.getElementById('embeddedStatus').innerHTML = 'Recording...';
                        document.getElementById('startEmbedded').disabled = true;
                        document.getElementById('stopEmbedded').disabled = false;
                    } catch (error) {
                        document.getElementById('embeddedStatus').innerHTML = 'Error: ' + error.message;
                    }
                };
                
                document.getElementById('stopEmbedded').onclick = function() {
                    if (embeddedRecorder && embeddedRecorder.state !== 'inactive') {
                        embeddedRecorder.stop();
                        embeddedStream.getTracks().forEach(track => track.stop());
                        document.getElementById('startEmbedded').disabled = false;
                        document.getElementById('stopEmbedded').disabled = true;
                    }
                };
                
                document.getElementById('downloadEmbedded').onclick = function() {
                    document.getElementById('embeddedStatus').innerHTML = 'Video will download automatically when you stop recording!';
                };
            </script>
            """
            
            st.components.v1.html(embedded_html, height=500)
            
            # Upload section for recorded videos
            st.subheader("📤 Upload Recorded Video")
            st.info("After recording your video, upload it back to the Streamlit app here:")
            
            uploaded_video = st.file_uploader(
                "Choose your recorded video file", 
                type=['mp4', 'avi', 'mov', 'webm', 'mkv'], 
                key="recorded_video_upload",
                help="Upload the video you recorded using the interactive recorder"
            )
            
            if uploaded_video is not None:
                st.success(f"✅ Video uploaded: {uploaded_video.name}")
            
                # Display video info
                file_size = uploaded_video.size
                st.info(f"📊 File Size: {file_size / (1024*1024):.2f} MB")
                
                # Show video preview
                st.subheader("🎥 Video Preview")
                st.video(uploaded_video)
                
                # Download button for uploaded video
                st.download_button(
                    label="📥 Download Video",
                    data=uploaded_video,
                    file_name=uploaded_video.name,
                    mime="video/mp4",
                    use_container_width=True
                )
            
                # Email integration
                st.subheader("📧 Send Video via Email")
                email_recipient = st.text_input("Recipient Email:", key="video_email_recipient")
                
                if st.button("📤 Send Video Email", use_container_width=True):
                    if email_recipient:
                        try:
                            # Use the email function from multitool_tasks
                            from multitool_tasks import send_email_gmail
                            result = send_email_gmail(email_recipient, "Video Recording", "Please find the attached video recording.")
                            st.success(f"Video sent to {email_recipient} successfully!")
                            st.info("Note: Email functionality requires proper SMTP configuration")
                        except Exception as e:
                            st.error(f"Email error: {e}")
                            st.info("Make sure EMAIL_ADDRESS and EMAIL_APP_PASSWORD are set in your .env file")
                    else:
                        st.error("Please enter recipient email address")
        
        with col2:
            st.info("**How to use Interactive Video Recording:**\n\n1. Allow camera and microphone permissions\n2. Click 'Start Recording' in the recorder\n3. Record your video with audio\n4. Click 'Stop Recording' when done\n5. Video will download automatically\n6. Upload the video back to Streamlit here")
            
            # Video recording tips
            st.subheader("💡 Recording Tips")
            st.markdown("""
            **For Best Results:**
            - Ensure good lighting conditions
            - Speak clearly for audio recording
            - Keep camera steady during recording
            - Record in a quiet environment
            - Use a modern browser (Chrome, Firefox, Safari)
            
            **Technical Requirements:**
            - HTTPS connection required
            - Camera and microphone permissions
            - Modern browser with MediaRecorder support
            - Sufficient storage space for video files
            
            **File Format:**
            - Videos saved as .webm format
            - Compatible with most video players
            - Includes both video and audio
            - High-quality recording (720p/1080p)
            """)
            
            # Features list
            st.subheader("✨ Interactive Recorder Features")
            st.markdown("""
            **🎥 Recording Features:**
            - Real-time video preview
            - Audio recording support
            - One-click start/stop
            - Automatic file naming
            
            **📥 Download Features:**
            - Automatic download to Downloads folder
            - Instant download after recording
            
            **📤 Upload Features:**
            - Easy upload back to Streamlit
            - File validation and preview
            - Email integration
            - Download from Streamlit
            """)
            
            # Browser compatibility
            st.subheader("🌐 Browser Compatibility")
            st.markdown("""
            **✅ Supported Browsers:**
            - Google Chrome (recommended)
            - Mozilla Firefox
            - Microsoft Edge
            - Safari (limited support)
            
            **⚠️ Requirements:**
            - HTTPS connection
            - Camera and microphone access
            - JavaScript enabled
            - Modern browser version
            """)
            
            # Troubleshooting
            st.subheader("🔧 Troubleshooting")
            st.markdown("""
            **Common Issues:**
            - **Camera not working:** Check browser permissions
            - **Audio not recording:** Allow microphone access
            - **Download not working:** Check Downloads folder
            - **Upload fails:** Ensure file is not too large
            
            **Solutions:**
            - Refresh the page and try again
            - Check browser settings for permissions
            - Use a different browser if issues persist
            - Ensure stable internet connection
            """)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application function"""
    

    
    # Sidebar navigation
    st.sidebar.title("🚀 Dashboard")
    st.sidebar.markdown("---")
    
    # API Key configuration
    st.sidebar.subheader("🔑 Configuration")
    api_key = st.sidebar.text_input("Google AI API Key", type="password", 
                                   value=os.getenv("GOOGLE_API_KEY", ""))
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        st.sidebar.success("✅ API Key configured")
    else:
        st.sidebar.warning("⚠️ API Key required for AI features")
    
    st.sidebar.markdown("---")
    
    # Navigation menu
    st.sidebar.subheader("📋 Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["🤖 AI Toolkit", "🐳 Docker Manager", "🐧 Remote Linux Assistant", 
         "📈 Machine Learning Models", "🛠️ Python Multi-Tool", "🌐 Web Dev"]
    )
    
    # Page routing
    if page == "🤖 AI Toolkit":
        render_ai_page()
    elif page == "🐳 Docker Manager":
        render_docker_page()
    elif page == "🐧 Remote Linux Assistant":
        render_linux_page()
    elif page == "📈 Machine Learning Models":
        render_ml_page()
    elif page == "🛠️ Python Multi-Tool":
        render_python_utils()
    elif page == "🌐 Web Dev":
        render_webdev_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Built with Streamlit**")
    st.sidebar.markdown("© 2024 Unified Project Dashboard")

if __name__ == "__main__":
    main() 