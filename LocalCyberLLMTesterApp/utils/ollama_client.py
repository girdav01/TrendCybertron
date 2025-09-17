"""
Ollama Client for Trend Cybertron App
Handles communication with Ollama API
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        """Initialize the Ollama client"""
        self.base_url = "http://localhost:11434"
        self.timeout = 300  # Increased timeout to 5 minutes for longer responses
    
    def set_base_url(self, host: str, port: str):
        """Set the base URL for Ollama API"""
        self.base_url = f"http://{host}:{port}"
    
    def test_connection(self, host: str = "localhost", port: str = "11434") -> bool:
        """Test connection to Ollama API"""
        try:
            url = f"http://{host}:{port}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def test_lmstudio_connection(self, host: str = "localhost", port: str = "1234") -> bool:
        """Test connection to LM Studio API"""
        try:
            url = f"http://{host}:{port}/v1/models"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"LM Studio connection test failed: {e}")
            return False
    
    def list_models(self, host: str = "localhost", port: str = "11434") -> List[Dict[str, Any]]:
        """List available models in Ollama"""
        try:
            url = f"http://{host}:{port}/api/tags"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('models', [])
            else:
                logger.error(f"Failed to list models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def list_lmstudio_models(self, host: str = "localhost", port: str = "1234") -> List[Dict[str, Any]]:
        """List available models in LM Studio"""
        try:
            url = f"http://{host}:{port}/v1/models"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Failed to list LM Studio models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing LM Studio models: {e}")
            return []
    
    def generate_response(self, 
                         prompt: str, 
                         system_prompt: str = None,
                         model: str = "llama-trendcybertron-primus-merged",
                         host: str = "localhost",
                         port: str = "11434",
                         temperature: float = 0.7,
                         max_tokens: int = 2000,
                         stream: bool = False,
                         max_retries: int = 3,
                         provider: str = "Ollama") -> str:
        """Generate a response using Ollama or LM Studio API with retry logic"""
        
        for attempt in range(max_retries):
            try:
                if provider == "Ollama":
                    # Ollama API format
                    url = f"http://{host}:{port}/api/generate"
                    
                    # Prepare the full prompt
                    full_prompt = prompt
                    if system_prompt:
                        full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
                    
                    payload = {
                        "model": model,
                        "prompt": full_prompt,
                        "stream": stream,
                        "options": {
                            "temperature": temperature,
                            "top_p": 0.9,
                            "top_k": 40,
                            "repeat_penalty": 1.1,
                            "num_predict": max_tokens,
                            "num_ctx": 8192
                        }
                    }
                else:  # LM Studio
                    # LM Studio uses OpenAI-compatible API format
                    url = f"http://{host}:{port}/v1/chat/completions"
                    
                    # Prepare messages array
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})
                    
                    payload = {
                        "model": model,
                        "messages": messages,
                        "stream": stream,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "top_p": 0.9,
                        "top_k": 40,
                        "repeat_penalty": 1.1
                    }
                
                logger.info(f"Generating response with {provider} model: {model} (attempt {attempt + 1}/{max_retries})")
                logger.info(f"Prompt length: {len(prompt)} characters")
                
                response = requests.post(
                    url, 
                    json=payload, 
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if provider == "Ollama":
                        response_text = data.get('response', 'No response generated')
                        # Extract token information if available
                        eval_count = data.get('eval_count', 0)
                        prompt_eval_count = data.get('prompt_eval_count', 0)
                        total_tokens = eval_count + prompt_eval_count
                    else:  # LM Studio
                        response_text = data.get('choices', [{}])[0].get('message', {}).get('content', 'No response generated')
                        # Extract token information if available
                        usage = data.get('usage', {})
                        total_tokens = usage.get('total_tokens', 0)
                    
                    logger.info(f"Response generated successfully (length: {len(response_text)} characters)")
                    return {
                        'response': response_text,
                        'tokens': total_tokens,
                        'eval_count': eval_count if provider == "Ollama" else usage.get('completion_tokens', 0),
                        'prompt_tokens': prompt_eval_count if provider == "Ollama" else usage.get('prompt_tokens', 0)
                    }
                else:
                    error_msg = f"API request failed with status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(2)
                        continue
                    return {
                        'response': f"Error: {error_msg}",
                        'tokens': 0,
                        'eval_count': 0,
                        'prompt_tokens': 0
                    }
                    
            except requests.exceptions.Timeout:
                error_msg = f"Request timed out (attempt {attempt + 1}/{max_retries}). The model might be taking too long to respond."
                logger.error(error_msg)
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in 3 seconds...")
                    time.sleep(3)
                    continue
                return {
                    'response': f"Error: {error_msg}",
                    'tokens': 0,
                    'eval_count': 0,
                    'prompt_tokens': 0
                }
            except requests.exceptions.ConnectionError:
                provider_name = "Ollama" if provider == "Ollama" else "LM Studio"
                error_msg = f"Connection error (attempt {attempt + 1}/{max_retries}). Please check if {provider_name} is running."
                logger.error(error_msg)
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                return {
                    'response': f"Error: {error_msg}",
                    'tokens': 0,
                    'eval_count': 0,
                    'prompt_tokens': 0
                }
            except Exception as e:
                error_msg = f"Unexpected error (attempt {attempt + 1}/{max_retries}): {str(e)}"
                logger.error(error_msg)
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                return {
                    'response': f"Error: {error_msg}",
                    'tokens': 0,
                    'eval_count': 0,
                    'prompt_tokens': 0
                }
        
            return {
                'response': "Error: All retry attempts failed",
                'tokens': 0,
                'eval_count': 0,
                'prompt_tokens': 0
            }
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: str = "llama-trendcybertron-primus-merged",
                       host: str = "localhost",
                       port: str = "11434",
                       temperature: float = 0.7,
                       max_tokens: int = 1000) -> str:
        """Generate a response using chat completion format"""
        try:
            url = f"http://{host}:{port}/api/chat"
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "num_predict": max_tokens,
                    "num_ctx": 2048
                }
            }
            
            logger.info(f"Chat completion with model: {model}")
            logger.info(f"Messages count: {len(messages)}")
            
            response = requests.post(
                url, 
                json=payload, 
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', 'No response generated')
            else:
                error_msg = f"Chat API request failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {
                    'response': f"Error: {error_msg}",
                    'tokens': 0,
                    'eval_count': 0,
                    'prompt_tokens': 0
                }
                
        except Exception as e:
            error_msg = f"Chat completion error: {str(e)}"
            logger.error(error_msg)
            return {
                'response': f"Error: {error_msg}",
                'tokens': 0,
                'eval_count': 0,
                'prompt_tokens': 0,
                'inference_time': 0
            }
    
    def pull_model(self, model_name: str, host: str = "localhost", port: str = "11434") -> bool:
        """Pull a model from Ollama registry"""
        try:
            url = f"http://{host}:{port}/api/pull"
            
            payload = {
                "name": model_name,
                "stream": False
            }
            
            logger.info(f"Pulling model: {model_name}")
            
            response = requests.post(
                url, 
                json=payload, 
                timeout=300,  # 5 minutes timeout for model pulling
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {model_name}")
                return True
            else:
                logger.error(f"Failed to pull model: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    def get_model_info(self, model_name: str, host: str = "localhost", port: str = "11434") -> Dict[str, Any]:
        """Get information about a specific model"""
        try:
            models = self.list_models(host, port)
            for model in models:
                if model['name'] == model_name:
                    return model
            return {}
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {}
    
    def check_model_availability(self, model_name: str, host: str = "localhost", port: str = "11434") -> bool:
        """Check if a model is available"""
        try:
            models = self.list_models(host, port)
            return any(model['name'] == model_name for model in models)
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    def get_health_status(self, host: str = "localhost", port: str = "11434") -> Dict[str, Any]:
        """Get Ollama health status"""
        try:
            url = f"http://{host}:{port}/api/tags"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                return {
                    'status': 'healthy',
                    'models_count': len(models),
                    'models': [model['name'] for model in models],
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f"HTTP {response.status_code}",
                    'response_time': response.elapsed.total_seconds()
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': None
            }
    
    def stream_response(self, 
                       prompt: str, 
                       system_prompt: str = None,
                       model: str = "llama-trendcybertron-primus-merged",
                       host: str = "localhost",
                       port: str = "11434",
                       temperature: float = 0.7,
                       max_tokens: int = 1000):
        """Stream response from Ollama API"""
        try:
            url = f"http://{host}:{port}/api/generate"
            
            # Prepare the full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "num_predict": max_tokens,
                    "num_ctx": 2048
                }
            }
            
            response = requests.post(
                url, 
                json=payload, 
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'},
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'response' in data:
                                yield data['response']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"Error: HTTP {response.status_code} - {response.text}"
                
        except Exception as e:
            yield f"Error: {str(e)}"
