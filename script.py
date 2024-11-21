def create_conversation_history(conversation_history_list):
    result = []
    for row in conversation_history_list:
        result.append({
            "role": "user",
            "content": row[0]
        })
        result.append({
        "role": "assistant",
        "content": row[1]
        })        
    return result
