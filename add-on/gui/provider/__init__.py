# Create a new config layout for a provider in the directory by name "ai_config_layout_{provider_name}.py"
# Add to the beginning: from .ai_config_layout import AIConfigLayout
# Define the class "AIConfigLayout{provider_name}" and inherit from PAIConfigLayout
# Implement: advanced() if needed
# Add arguments for the provider in meta.json: ai_config


import os, re, importlib
from ...ai.provider import special_names

dir_path = os.path.dirname(os.path.realpath(__file__))
files = [f for f in os.listdir(dir_path) if f.endswith('.py')]
providers = [re.match(r'ai_config_layout_(\w+)\.py', f)[1] for f in files if re.match(r'ai_config_layout_(\w+)\.py', f)]

for i, provider_name in enumerate(providers):
    module = importlib.import_module(f".ai_config_layout_{provider_name}", package=__name__)
    if provider_name in special_names:
        provider_name = special_names[provider_name]
    else:
        provider_name = provider_name.capitalize()
    providers[i] = provider_name
    globals()["ai_config_layout_" + provider_name] = getattr(module, f"AIConfigLayout{provider_name}")
