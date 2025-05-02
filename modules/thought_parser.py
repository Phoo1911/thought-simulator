import re

def parse_thoughts(response):
    """Parse thought steps from LLM response"""
    thoughts = []
    
    # 추가: Step 1:, Step 2: 형태도 인식
    patterns = [
        r'(Step\s*\d+:\s*)(.*?)(?=Step\s*\d+:\s*|$)',  # Step-numbered items
        r'(\d+[\.\)]\s*)(.*?)(?=\d+[\.\)]\s*|$)',       # Numbered items
        r'([*\-]\s*)(.*?)(?=[*\-]\s*|$)',              # Bulleted items
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, response, re.DOTALL)
        for match in matches:
            thought_text = match.group(2).strip()
            if thought_text:
                thoughts.append({
                    'text': thought_text,
                    'type': 'standard'
                })
        if thoughts:
            break

    # If still nothing found, fallback to paragraph split
    if not thoughts:
        paragraphs = response.split('\n\n')
        for para in paragraphs:
            if para.strip():
                thoughts.append({
                    'text': para.strip(),
                    'type': 'paragraph'
                })

    # Classify each thought based on keyword heuristics
    for thought in thoughts:
        text = thought['text'].lower()
        if any(word in text for word in ['analyze', 'consider']):
            thought['type'] = 'analytical'
        elif any(word in text for word in ['alternative', 'creative']):
            thought['type'] = 'creative'
        elif any(word in text for word in ['evaluate', 'assess']):
            thought['type'] = 'evaluative'
        elif any(word in text for word in ['reflect', 'meta']):
            thought['type'] = 'reflective'

    return thoughts
