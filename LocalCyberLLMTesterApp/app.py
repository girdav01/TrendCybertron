"""
Trend Cybertron Streamlit App
A comprehensive cybersecurity AI assistant based on Trend Cybertron Primus 8B model
"""

import streamlit as st
import ollama
import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from database_manager import DatabaseManager
from ollama_client import OllamaClient
from prompt_templates import PromptTemplates

# Page configuration
st.set_page_config(
    page_title="Trend Cybertron AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tab-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e8b57;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .system-message {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .error-message {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        color: #c62828;
    }
    .success-message {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

class TrendCybertronApp:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.ollama_client = OllamaClient()
        self.prompt_templates = PromptTemplates()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'messages' not in st.session_state:
            st.session_state.messages = {}
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = 'Configuration'
        if 'ollama_config' not in st.session_state:
            st.session_state.ollama_config = {
                'host': 'localhost',
                'port': '11434',
                'model': 'llama-trendcybertron-primus-merged',
                'provider': 'Ollama'
            }
        if 'temperature' not in st.session_state:
            st.session_state.temperature = 0.7
        if 'max_tokens' not in st.session_state:
            st.session_state.max_tokens = 2000

    def render_header(self):
        """Render the main header"""
        st.markdown('<div class="main-header">🛡️ Trend Cybertron AI Assistant</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; color: #666; margin-bottom: 2rem;">
            Powered by Trend Cybertron Primus 8B - Specialized Cybersecurity AI Model
        </div>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render the sidebar with configuration options"""
        with st.sidebar:
            st.markdown("## ⚙️ Configuration")
            
            # Provider selection
            provider = st.selectbox(
                "Model Provider",
                ["Ollama", "LM Studio"],
                index=0,
                help="Choose between Ollama (local) or LM Studio (local with web UI)"
            )
            
            if provider == "Ollama":
                st.markdown("### 🔧 Ollama Settings")
                host = st.text_input("Host", value=st.session_state.ollama_config['host'])
                port = st.text_input("Port", value=st.session_state.ollama_config['port'])
                
                # Model selection
                try:
                    models = self.ollama_client.list_models(host, port)
                    if models:
                        model_names = [model['name'] for model in models]
                        # Prefer Trend Cybertron model if available
                        if 'llama-trendcybertron-primus-merged' in model_names:
                            default_index = model_names.index('llama-trendcybertron-primus-merged')
                        else:
                            default_index = 0
                        selected_model = st.selectbox(
                            "Model", 
                            model_names,
                            index=default_index
                        )
                    else:
                        st.warning("⚠️ No models found. Please pull a model first:")
                        st.code("ollama pull llama3.2:3b")
                        selected_model = st.text_input(
                            "Enter model name manually:", 
                            value="llama3.2:3b"
                        )
                except Exception as e:
                    st.error(f"Error loading models: {e}")
                    st.info("Please ensure Ollama is running and try again.")
                    selected_model = st.text_input(
                        "Enter model name manually:", 
                        value="llama3.2:3b"
                    )
            else:  # LM Studio
                st.markdown("### 🎨 LM Studio Settings")
                host = st.text_input("Host", value="localhost")
                port = st.text_input("Port", value="1234")
                
                # Model selection for LM Studio
                try:
                    models = self.ollama_client.list_lmstudio_models(host, port)
                    if models:
                        model_names = [model['id'] for model in models]
                        selected_model = st.selectbox(
                            "Model", 
                            model_names,
                            index=0
                        )
                    else:
                        st.warning("⚠️ No models found. Please load a model in LM Studio first.")
                        selected_model = st.text_input(
                            "Enter model name manually:", 
                            value=""
                        )
                except Exception as e:
                    st.error(f"Error loading models: {e}")
                    st.info("Please ensure LM Studio is running and try again.")
                    selected_model = st.text_input(
                        "Enter model name manually:", 
                        value=""
                    )
            
            # Update session state
            st.session_state.ollama_config = {
                'host': host,
                'port': port,
                'model': selected_model,
                'provider': provider
            }
            
            # Generation parameters
            st.markdown("### 🎛️ Generation Parameters")
            st.session_state.temperature = st.slider(
                "Temperature", 
                min_value=0.0, 
                max_value=1.0, 
                value=st.session_state.temperature, 
                step=0.1,
                help="Controls randomness. Lower values make responses more focused."
            )
            
            st.session_state.max_tokens = st.slider(
                "Max Tokens", 
                min_value=100, 
                max_value=8000, 
                value=st.session_state.max_tokens, 
                step=100,
                help="Maximum number of tokens to generate (up to 8000 for longer responses)."
            )
            
            # Connection test
            st.markdown("### 🔍 Connection Test")
            if st.button("Test Connection"):
                with st.spinner("Testing connection..."):
                    try:
                        if provider == "Ollama":
                            response = self.ollama_client.test_connection(host, port)
                        else:  # LM Studio
                            response = self.ollama_client.test_lmstudio_connection(host, port)
                        
                        if response:
                            st.success("✅ Connection successful!")
                        else:
                            st.error("❌ Connection failed!")
                    except Exception as e:
                        st.error(f"❌ Connection error: {e}")
            
            # Clear conversations
            st.markdown("### 🗑️ Data Management")
            if st.button("Clear All Conversations"):
                self.db_manager.clear_all_conversations()
                st.session_state.messages = {}
                st.success("All conversations cleared!")
            
            # Export conversations
            if st.button("Export Conversations"):
                conversations = self.db_manager.export_conversations()
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(conversations, indent=2),
                    file_name=f"trend_cybertron_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

    def render_configuration_tab(self):
        """Render the configuration tab"""
        st.markdown('<div class="tab-header">⚙️ Configuration & Setup</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚀 Quick Setup")
            
            # Provider selection for setup instructions
            setup_provider = st.selectbox(
                "Choose setup instructions for:",
                ["Ollama", "LM Studio"],
                index=0
            )
            
            if setup_provider == "Ollama":
                st.markdown("""
                **Prerequisites:**
                1. Ollama installed and running
                2. Trend Cybertron Primus 8B model pulled
                3. Python packages installed
                
                **Setup Commands:**
                ```bash
                # Install Ollama (if not installed)
                # Windows: Download from https://ollama.ai/
                # macOS: brew install ollama
                # Linux: curl -fsSL https://ollama.ai/install.sh | sh
                
                # Start Ollama service
                ollama serve
                
                # Pull the model
                ollama pull llama-trendcybertron-primus-merged
                
                # Install Python packages
                pip install streamlit ollama
                ```
                """)
            else:  # LM Studio
                st.markdown("""
                **Prerequisites:**
                1. LM Studio installed and running
                2. Model loaded in LM Studio
                3. Python packages installed
                
                **Setup Commands:**
                ```bash
                # Install LM Studio
                # Download from https://lmstudio.ai/
                
                # Start LM Studio and load a model
                # 1. Open LM Studio
                # 2. Go to "Local Server" tab
                # 3. Load your preferred model
                # 4. Start the server (default port 1234)
                
                # Install Python packages
                pip install streamlit requests
                ```
                """)
            
            if st.button("🚀 Run Setup Script"):
                st.info("Please run the setup commands manually in your terminal.")
        
        with col2:
            st.markdown("### 📊 System Status")
            
            # Check provider status
            provider = st.session_state.ollama_config.get('provider', 'Ollama')
            
            if provider == "Ollama":
                try:
                    models = self.ollama_client.list_models(
                        st.session_state.ollama_config['host'],
                        st.session_state.ollama_config['port']
                    )
                    if models:
                        st.success("✅ Ollama is running")
                        st.info(f"📋 Available models: {len(models)}")
                        for model in models[:5]:  # Show first 5 models
                            st.text(f"  • {model['name']}")
                    else:
                        st.warning("⚠️ No models found")
                except Exception as e:
                    st.error(f"❌ Ollama connection failed: {e}")
            else:  # LM Studio
                try:
                    models = self.ollama_client.list_lmstudio_models(
                        st.session_state.ollama_config['host'],
                        st.session_state.ollama_config['port']
                    )
                    if models:
                        st.success("✅ LM Studio is running")
                        st.info(f"📋 Available models: {len(models)}")
                        for model in models[:5]:  # Show first 5 models
                            st.text(f"  • {model['id']}")
                    else:
                        st.warning("⚠️ No models found")
                except Exception as e:
                    st.error(f"❌ LM Studio connection failed: {e}")
            
            # Database status
            try:
                db_status = self.db_manager.get_database_status()
                st.success("✅ Database is ready")
                st.info(f"📊 Total conversations: {db_status['total_conversations']}")
            except Exception as e:
                st.error(f"❌ Database error: {e}")

    def render_chat_tab(self, tab_name: str, system_prompt: str, test_prompts: List[str]):
        """Render a chat tab with system prompt and test prompts"""
        st.markdown(f'<div class="tab-header">💬 {tab_name}</div>', unsafe_allow_html=True)
        
        # Create two columns for system prompt and test prompts
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🎯 System Prompt")
            st.markdown("This is the specialized prompt that defines the AI's role and expertise:")
            with st.expander("View System Prompt", expanded=False):
                st.code(system_prompt, language="text")
            
            # Copy system prompt button
            if st.button(f"📋 Copy System Prompt", key=f"copy_system_{tab_name}"):
                st.code(system_prompt, language="text")
                st.success("System prompt displayed above! You can copy it manually.")
        
        with col2:
            st.markdown("### 🧪 Test Prompts")
            st.markdown("Click any button below to load a test prompt:")
            
            # Create a unique hash for this tab to ensure all keys are unique
            import hashlib
            tab_hash = hashlib.md5(tab_name.encode()).hexdigest()[:8]
            
            for i, test_prompt in enumerate(test_prompts):
                # Create a unique key using hash
                unique_test_key = f"test_{tab_hash}_{i}"
                if st.button(f"📝 Test {i+1}", key=unique_test_key):
                    # Store the test prompt in session state for the chat input
                    st.session_state[f"test_prompt_{tab_name}"] = test_prompt
                    st.success(f"Test prompt {i+1} loaded! You can copy it from the text area below.")
            
            # Show the selected test prompt in a text area for easy copying (outside the loop)
            if f"test_prompt_{tab_name}" in st.session_state:
                st.markdown("**Selected Test Prompt:**")
                # Create a unique key for the text area using hash to ensure uniqueness
                unique_textarea_key = f"test_prompt_display_{tab_hash}"
                st.text_area(
                    "Copy this prompt to use in the chat:",
                    value=st.session_state[f"test_prompt_{tab_name}"],
                    height=100,
                    key=unique_textarea_key
                )
                
                # Clear button
                unique_clear_key = f"clear_test_{tab_hash}"
                if st.button(f"🗑️ Clear Test Prompt", key=unique_clear_key):
                    del st.session_state[f"test_prompt_{tab_name}"]
                    st.rerun()
        
        # Initialize messages for this tab
        if tab_name not in st.session_state.messages:
            st.session_state.messages[tab_name] = []
        
        # Display chat history
        for message in st.session_state.messages[tab_name]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Multi-model comparison option
        st.markdown("### 🔄 Multi-Model Comparison")
        enable_comparison = st.checkbox(
            "Compare responses from multiple models", 
            key=f"comparison_{tab_name}",
            help="Send the same prompt to up to 3 different models and compare results"
        )
        
        comparison_models = []
        if enable_comparison:
            col1, col2, col3 = st.columns(3)
            with col1:
                model1 = st.selectbox(
                    "Model 1", 
                    self.get_available_models(),
                    key=f"model1_{tab_name}"
                )
                if model1:
                    comparison_models.append(model1)
            with col2:
                model2 = st.selectbox(
                    "Model 2", 
                    [""] + [m for m in self.get_available_models() if m != model1],
                    key=f"model2_{tab_name}"
                )
                if model2:
                    comparison_models.append(model2)
            with col3:
                model3 = st.selectbox(
                    "Model 3", 
                    [""] + [m for m in self.get_available_models() if m not in [model1, model2]],
                    key=f"model3_{tab_name}"
                )
                if model3:
                    comparison_models.append(model3)
        
        # Chat input
        chat_input_key = f"chat_input_{tab_name}"
        
        if prompt := st.chat_input(f"Ask about {tab_name.lower()}...", key=chat_input_key):
            
            # Add user message to chat history
            st.session_state.messages[tab_name].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            if enable_comparison and comparison_models:
                # Multi-model comparison
                self.generate_multi_model_responses(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    models=comparison_models,
                    tab_name=tab_name,
                    temperature=st.session_state.temperature,
                    max_tokens=st.session_state.max_tokens
                )
            else:
                # Single model response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response_data = self.ollama_client.generate_response(
                                prompt=prompt,
                                system_prompt=system_prompt,
                                model=st.session_state.ollama_config['model'],
                                host=st.session_state.ollama_config['host'],
                                port=st.session_state.ollama_config['port'],
                                temperature=st.session_state.temperature,
                                max_tokens=st.session_state.max_tokens,
                                provider=st.session_state.ollama_config.get('provider', 'Ollama')
                            )
                            
                            # Extract response
                            response_text = response_data['response']
                            
                            st.markdown(response_text)
                            
                            # Add assistant response to chat history
                            st.session_state.messages[tab_name].append({"role": "assistant", "content": response_text})
                            
                            # Save to database
                            self.db_manager.save_message(
                                tab_name=tab_name,
                                user_message=prompt,
                                assistant_response=response_text,  # Save original response without formatting
                                system_prompt=system_prompt,
                                model=model_name,
                                temperature=st.session_state.temperature,
                                max_tokens=st.session_state.max_tokens
                            )
                            
                        except Exception as e:
                            error_msg = f"Error generating response: {e}"
                            st.error(error_msg)
                            st.session_state.messages[tab_name].append({"role": "assistant", "content": error_msg})

    def get_available_models(self):
        """Get list of available models from the current provider"""
        try:
            provider = st.session_state.ollama_config.get('provider', 'Ollama')
            host = st.session_state.ollama_config['host']
            port = st.session_state.ollama_config['port']
            
            if provider == "Ollama":
                models = self.ollama_client.list_models(host, port)
                return [model['name'] for model in models] if models else []
            else:  # LM Studio
                models = self.ollama_client.list_lmstudio_models(host, port)
                return [model['id'] for model in models] if models else []
        except Exception as e:
            st.error(f"Error getting models: {e}")
            return []

    def generate_multi_model_responses(self, prompt, system_prompt, models, tab_name, temperature, max_tokens):
        """Generate responses from multiple models and display them side by side"""
        provider = st.session_state.ollama_config.get('provider', 'Ollama')
        host = st.session_state.ollama_config['host']
        port = st.session_state.ollama_config['port']
        
        # Create columns for each model response
        cols = st.columns(len(models))
        responses = []
        
        for i, model in enumerate(models):
            with cols[i]:
                st.markdown(f"### 🤖 {model}")
                with st.spinner(f"Generating response with {model}..."):
                    try:
                        response_data = self.ollama_client.generate_response(
                            prompt=prompt,
                            system_prompt=system_prompt,
                            model=model,
                            host=host,
                            port=port,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            provider=provider
                        )
                        
                        # Extract response
                        response_text = response_data['response']
                        
                        st.markdown(response_text)
                        responses.append({
                            'model': model,
                            'response': response_text
                        })
                        
                    except Exception as e:
                        error_msg = f"❌ Error: {e}"
                        st.error(error_msg)
                        responses.append({
                            'model': model,
                            'response': f"Error: {e}"
                        })
        
        # Add all responses to chat history
        combined_response = "\n\n".join([resp['response'] for resp in responses])
        st.session_state.messages[tab_name].append({"role": "assistant", "content": combined_response})
        
        # Save each response to database
        for resp in responses:
            self.db_manager.save_message(
                tab_name=tab_name,
                user_message=prompt,
                assistant_response=resp['response'],
                system_prompt=system_prompt,
                model=resp['model'],
                temperature=temperature,
                max_tokens=max_tokens
            )

    def run(self):
        """Main application loop"""
        self.initialize_session_state()
        self.render_header()
        self.render_sidebar()
        
        # Define tabs with system prompts and test prompts
        tabs = {
            "Configuration": self.render_configuration_tab,
            "Alert Prioritization": lambda: self.render_chat_tab(
                "Alert Prioritization", 
                self.prompt_templates.get_alert_prioritization_prompt(),
                self.prompt_templates.get_test_prompts("alert_prioritization")
            ),
            "YARA Patterns": lambda: self.render_chat_tab(
                "YARA Patterns", 
                self.prompt_templates.get_yara_patterns_prompt(),
                self.prompt_templates.get_test_prompts("yara_patterns")
            ),
            "OSINT Reporting": lambda: self.render_chat_tab(
                "OSINT Reporting", 
                self.prompt_templates.get_osint_reporting_prompt(),
                self.prompt_templates.get_test_prompts("osint_reporting")
            ),
            "Incident Summarization": lambda: self.render_chat_tab(
                "Incident Summarization", 
                self.prompt_templates.get_incident_summarization_prompt(),
                self.prompt_templates.get_test_prompts("incident_summarization")
            ),
            "Red Team Planning": lambda: self.render_chat_tab(
                "Red Team Planning", 
                self.prompt_templates.get_redteam_planning_prompt(),
                self.prompt_templates.get_test_prompts("redteam_planning")
            ),
            "Exploit Generation": lambda: self.render_chat_tab(
                "Exploit Generation", 
                self.prompt_templates.get_exploit_generation_prompt(),
                self.prompt_templates.get_test_prompts("exploit_generation")
            ),
            "Threat Intelligence": lambda: self.render_chat_tab(
                "Threat Intelligence", 
                self.prompt_templates.get_threat_intelligence_prompt(),
                self.prompt_templates.get_test_prompts("threat_intelligence")
            ),
            "Vulnerability Assessment": lambda: self.render_chat_tab(
                "Vulnerability Assessment", 
                self.prompt_templates.get_vulnerability_assessment_prompt(),
                self.prompt_templates.get_test_prompts("vulnerability_assessment")
            ),
            "Security Policy": lambda: self.render_chat_tab(
                "Security Policy", 
                self.prompt_templates.get_security_policy_prompt(),
                self.prompt_templates.get_test_prompts("security_policy")
            ),
            "CREM Discover": lambda: self.render_chat_tab(
                "CREM Discover", 
                self.prompt_templates.get_crem_discover_prompt(),
                self.prompt_templates.get_test_prompts("crem_discover")
            ),
            "CREM Predict": lambda: self.render_chat_tab(
                "CREM Predict", 
                self.prompt_templates.get_crem_predict_prompt(),
                self.prompt_templates.get_test_prompts("crem_predict")
            ),
            "CREM Prioritize": lambda: self.render_chat_tab(
                "CREM Prioritize", 
                self.prompt_templates.get_crem_prioritize_prompt(),
                self.prompt_templates.get_test_prompts("crem_prioritize")
            ),
            "CREM Comply": lambda: self.render_chat_tab(
                "CREM Comply", 
                self.prompt_templates.get_crem_comply_prompt(),
                self.prompt_templates.get_test_prompts("crem_comply")
            ),
            "CREM Quantify": lambda: self.render_chat_tab(
                "CREM Quantify", 
                self.prompt_templates.get_crem_quantify_prompt(),
                self.prompt_templates.get_test_prompts("crem_quantify")
            ),
            "CREM Mitigate": lambda: self.render_chat_tab(
                "CREM Mitigate", 
                self.prompt_templates.get_crem_mitigate_prompt(),
                self.prompt_templates.get_test_prompts("crem_mitigate")
            )
        }
        
        # Create tabs
        selected_tab = st.selectbox(
            "Select a cybersecurity use case:",
            list(tabs.keys()),
            index=list(tabs.keys()).index(st.session_state.current_tab)
        )
        
        st.session_state.current_tab = selected_tab
        
        # Render selected tab
        tabs[selected_tab]()

def main():
    """Main function"""
    app = TrendCybertronApp()
    app.run()

if __name__ == "__main__":
    main()
