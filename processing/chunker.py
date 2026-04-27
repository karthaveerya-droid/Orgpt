def chunk_texts(texts, chunk_size=300, min_chunk_size=150):
    """
    Chunk texts into smaller pieces for embedding.
    
    Args:
        texts: List of text documents
        chunk_size: Maximum words per chunk
        min_chunk_size: Minimum words to trigger chunking (if doc is smaller, keep whole)
    
    Returns:
        List of text chunks
    """
    chunks = []
    for text in texts:
        words = text.split()
        word_count = len(words)
        
        # If document is small enough, don't chunk it
        if word_count <= chunk_size:
            chunks.append(text)
        else:
            # Chunk larger documents
            for i in range(0, word_count, chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                chunks.append(chunk)
    
    return chunks
