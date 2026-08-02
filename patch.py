import sys

with open('clip_analyzer.py', 'r') as f:
    content = f.read()

old_str = """        The segment must not exceed 60 seconds (end_time - start_time <= 60).
        It must be a complete thought that makes sense as a standalone short-form video.

        Output ONLY valid JSON matching this exact structure:
        {
           "start_time": 12.0,
           "end_time": 72.0,
           "reason": "This is highly engaging because...",
           "instagram_caption": "This is the caption for the reel! #viral"
        }"""

new_str = """        The segment must not exceed 60 seconds (end_time - start_time <= 60).
        It must be a complete thought that makes sense as a standalone short-form video.
        
        CRITICAL: For the "instagram_caption" field, you MUST write a highly detailed, engaging, and relevant caption based EXACTLY on what was said in the selected 60-second clip. 
        - Summarize the core lesson or point being made in the clip.
        - Include an engaging hook/question for the audience.
        - Add 5-8 relevant hashtags.
        - Use appropriate line breaks and emojis.

        Output ONLY valid JSON matching this exact structure:
        {
           "start_time": 12.0,
           "end_time": 72.0,
           "reason": "This is highly engaging because...",
           "instagram_caption": "Your highly detailed, content-specific caption here..."
        }"""

new_content = content.replace(old_str, new_str)
with open('clip_analyzer.py', 'w') as f:
    f.write(new_content)
