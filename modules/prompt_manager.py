import yaml
from string import Template

class PromptTemplateManager:
    def __init__(self, template_path):
        with open(template_path, 'r', encoding='utf-8') as file:
            self.templates = yaml.safe_load(file)
        print("✅ Loaded Templates:")
        for key in self.templates.keys():
            print(f"  • {key} → {list(self.templates[key].keys())}")

    def normalize_pattern_type(self, pattern_type):
        """Normalize pattern keys to match YAML format"""
        return pattern_type.replace("-", "_")

    def get_template(self, thought_type, pattern_type):
        pattern_type = self.normalize_pattern_type(pattern_type)

        print(f" Requested: {thought_type=} | {pattern_type=}")
        print(f" Available thought types: {list(self.templates.keys())}")
        thought_templates = self.templates.get(thought_type)
        if not thought_templates:
            print(f" No templates found for {thought_type}")
            return None

        print(f"📘 Available patterns for {thought_type}: {list(thought_templates.keys())}")
        template = thought_templates.get(pattern_type)
        if not template:
            print(f" Pattern '{pattern_type}' not found under '{thought_type}'")
        return template

    def generate_prompt(self, thought_type, pattern_type, params):
        """Generate prompt by applying parameters to template"""
        normalized_type = self.normalize_pattern_type(pattern_type)
        template = self.get_template(thought_type, normalized_type)

        if not template:
            print(f"⛑ Falling back to default / {normalized_type}")
            template = self.templates.get("default", {}).get(normalized_type)

        if not template:
            raise ValueError(f" Template not found for {thought_type}/{normalized_type}, and no default fallback available.")

        # Combine meta, structure, and content levels
        meta_template = Template(template.get('meta_level', ''))
        structure_template = Template(template.get('structure_level', ''))
        content_template = Template(template.get('content_level', ''))

        meta_text = meta_template.safe_substitute(params)
        structure_text = structure_template.safe_substitute(params)
        content_text = content_template.safe_substitute(params)

        return f"{meta_text}\n\n{structure_text}\n\n{content_text}"
