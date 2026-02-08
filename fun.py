"""
Token counting utility for Groq API
"""

import tiktoken

def count_tokens(messages):
    """
    Count tokens in messages using tiktoken
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        
    Returns:
        int: Estimated token count
    """
    try:
        # Use cl100k_base encoding (used by GPT-3.5/GPT-4)
        encoding = tiktoken.get_encoding("cl100k_base")
        
        num_tokens = 0
        for message in messages:
            # Every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4
            
            for key, value in message.items():
                num_tokens += len(encoding.encode(str(value)))
                
        num_tokens += 2  # Every reply is primed with <im_start>assistant
        
        return num_tokens
        
    except Exception as e:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        total_chars = 0
        for msg in messages:
            total_chars += len(str(msg.get('content', '')))
            total_chars += len(str(msg.get('role', '')))
        
        return total_chars // 4


def count_tokens_simple(text):
    """
    Count tokens for a simple text string
    
    Args:
        text: String to count tokens for
        
    Returns:
        int: Estimated token count
    """
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception as e:
        # Fallback: rough estimate
        return len(text) // 4
