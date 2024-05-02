# Create a new provider in the directory by name "provider_{provider_name}.py"
# Add to the beginning: from .provider import Provider
# Define the class "Provider{provider_name}" and inherit from Provider
# Implement: 1. __call__; 2. get_avail_chat_model_list; 3.update_api_key
# Add arguments for the provider in meta.json: ai_config


import os, re, importlib

# A provider name is by default the capitalize of
special_names = {
    "openai": "OpenAI",
}

dir_path = os.path.dirname(os.path.realpath(__file__))
files = [f for f in os.listdir(dir_path) if f.endswith('.py')]
providers = [re.match(r'provider_(\w+)\.py', f)[1] for f in files if re.match(r'provider_(\w+)\.py', f)]

for i, provider_name in enumerate(providers):
    module = importlib.import_module(f".provider_{provider_name}", package=__name__)
    if provider_name in special_names:
        provider_name = special_names[provider_name]
    else:
        provider_name = provider_name.capitalize()
    providers[i] = provider_name
    globals()[provider_name] = getattr(module, f"Provider{provider_name}")
