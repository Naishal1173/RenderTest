#!/usr/bin/env python3
"""
Robust PDF-based Chatbot
Handles API rate limits gracefully with fallback responses
Works with any PDF data processed through AnythingLLM
"""

import json
import requests
import numpy as np
import re
import time
from pathlib import Path
from typing import List, Dict, Tuple

class RobustChatbot:
    """Robust chatbot with rate limit handling and fallback responses"""
    
    def __init__(self):
        self.gemini_api_key = "AIzaSyBjRzi23AIhZF5BSXczgFY3jDXRkXfINCw"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={self.gemini_api_key}"
        self.chunks = []
        self.last_api_call = 0
        self.api_delay = 2  # 2 seconds between API calls
        self.load_data()
    
    def load_data(self):
        """Load text chunks from JSON files"""
        print("Loading PDF document data...")
        
        json_files = list(Path(".").glob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list) and len(data) > 0:
                    chunks_list = data[0] if isinstance(data[0], list) else data
                    
                    for item in chunks_list:
                        if 'metadata' in item and 'text' in item['metadata']:
                            text = item['metadata']['text']
                            
                            # Clean text
                            if '<document_metadata>' in text:
                                text = text.split('</document_metadata>')[-1]
                            text = text.replace('passage:', '').strip()
                            text = re.sub(r'\s+', ' ', text)
                            
                            if len(text) > 20:
                                self.chunks.append({
                                    'text': text,
                                    'source': item['metadata'].get('sourceDocument', json_file.name)
                                })
            
            except Exception as e:
                print(f"Warning: Could not load {json_file}: {e}")
                continue
        
        print(f"✅ Loaded {len(self.chunks)} document chunks")
    
    def smart_search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Enhanced smart search with improved pattern matching"""
        query_lower = query.lower()
        scored_chunks = []
        
        # Extract key terms from query
        query_words = [w.strip('.,!?;:') for w in query_lower.split() if len(w) > 2]
        important_words = [w for w in query_words if len(w) > 4]
        
        for chunk in self.chunks:
            text_lower = chunk['text'].lower()
            score = 0
            
            # 1. Exact phrase matching (highest priority)
            if query_lower in text_lower:
                score += 500
            
            # 2. Important word matching
            for word in important_words:
                if word in text_lower:
                    score += 80
                    # Bonus for word at start of sentences
                    if f". {word}" in text_lower or f"• {word}" in text_lower:
                        score += 20
            
            # 3. Regular word matching
            word_matches = sum(1 for word in query_words if word in text_lower)
            score += word_matches * 25
            
            # 4. Document structure elements (tables, sections, etc.)
            structure_terms = {
                'table': 150, 'section': 120, 'chapter': 120, 'clause': 100,
                'paragraph': 80, 'article': 100, 'rule': 120, 'regulation': 120
            }
            
            for term, bonus in structure_terms.items():
                if term in query_lower and term in text_lower:
                    score += bonus
            
            # 5. Numbers and references matching
            import re
            query_numbers = re.findall(r'\d+\.?\d*', query)
            text_numbers = re.findall(r'\d+\.?\d*', chunk['text'])
            
            for qnum in query_numbers:
                if qnum in text_numbers:
                    score += 100
            
            # 6. Question type bonuses
            question_patterns = {
                'what is': 50, 'how to': 50, 'where': 40, 'when': 40,
                'why': 40, 'which': 40, 'define': 60, 'explain': 60,
                'requirement': 80, 'specification': 80, 'standard': 80
            }
            
            for pattern, bonus in question_patterns.items():
                if pattern in query_lower:
                    score += bonus
            
            # 7. Length penalty for very short chunks
            if len(chunk['text']) < 50:
                score *= 0.5
            
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Sort by score and return top results
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]
    
    def get_smart_answer(self, query: str, chunks: List[Tuple[Dict, float]]) -> str:
        """Get smart answers with professional formatting when API is unavailable"""
        if not chunks:
            return "❌ **No Relevant Information Found**\n\nI couldn't find information related to your question in the loaded documents. Please try:\n\n• Rephrasing your question\n• Using different keywords\n• Asking about topics covered in the uploaded documents"
        
        # Use the best matching chunk for fallback response
        best_chunk = chunks[0][0]
        preview = best_chunk['text'][:800]
        
        # Determine if it's a short or detailed question
        query_words = len(query.split())
        
        if query_words <= 5:  # Short question
            return f"""**Answer from Document:**\n\n{preview}...\n\n---\n*Source: {best_chunk['source']}*\n\n💡 **Note:** This response is extracted directly from your document. For more details, please ask a more specific question."""
        else:  # Detailed question
            return f"""## 📋 **Document Analysis Results**\n\n### **Relevant Information Found:**\n\n{preview}...\n\n### **Key Points:**\n• Information extracted from loaded documents\n• No external knowledge used\n• Based on document content analysis\n\n---\n\n### **📄 Source Reference:**\n*{best_chunk['source']}*\n\n💡 **For More Details:** Ask specific questions about particular sections, tables, or requirements mentioned in your documents."""
    
    def try_gemini_api(self, query: str, context: str) -> str:
        """Try Gemini API with enhanced prompt for document-only responses"""
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_api_call < self.api_delay:
                time.sleep(self.api_delay - (current_time - self.last_api_call))
            
            # Enhanced prompt for document-only responses with professional formatting
            prompt = f"""You are a professional document analysis assistant. Your ONLY job is to answer questions using EXCLUSIVELY the provided document context. You must NEVER use external knowledge or make assumptions.

CRITICAL INSTRUCTIONS:
🚫 NEVER use information not present in the context below
🚫 NEVER make assumptions or add external knowledge
🚫 NEVER hallucinate or create information
✅ ONLY use facts directly stated in the provided context
✅ If information is not in context, clearly state "This information is not available in the provided documents"
✅ Format responses professionally like ChatGPT with clear structure

RESPONSE FORMATTING GUIDELINES:
• For SHORT questions: Provide direct, concise answers (2-3 sentences)
• For DETAILED questions: Use structured format with headings, bullet points, and numbered lists
• Always include specific references (Table X, Section Y, Page Z) when mentioned in context
• Use markdown formatting for better readability
• Start with the most important information first

DOCUMENT CONTEXT:
{context[:1500]}

USER QUESTION: {query}

RESPONSE (based ONLY on the above context):"""
            
            response = requests.post(
                self.gemini_url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 800,
                        "topP": 0.8,
                        "topK": 10
                    }
                },
                timeout=15
            )
            
            self.last_api_call = time.time()
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    answer = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    if len(answer) > 20:
                        return answer
            
            elif response.status_code == 429:
                print("⚠️  API rate limit reached, using fallback response...")
                return None
            
        except Exception as e:
            print(f"⚠️  API error: {e}, using fallback response...")
        
        return None
    
    def ask(self, question: str) -> Dict:
        """Main method to ask questions with enhanced processing"""
        if not question.strip():
            return {
                'answer': "👋 **Welcome!** Please ask a question about your uploaded documents.\n\n**Examples:**\n• What are the requirements for...?\n• Explain the process of...\n• What does Table X say about...?",
                'sources': []
            }
        
        print(f"🔍 Processing question: {question}")
        
        # Enhanced search for relevant documents
        relevant_chunks = self.smart_search(question, top_k=5)
        
        if not relevant_chunks:
            return {
                'answer': "❌ **No Relevant Information Found**\n\nI couldn't find information related to your question in the loaded documents.\n\n**Suggestions:**\n• Try different keywords\n• Check if your question relates to the uploaded documents\n• Rephrase your question more specifically",
                'sources': []
            }
        
        print(f"✅ Found {len(relevant_chunks)} relevant sections (best match score: {relevant_chunks[0][1]:.1f})")
        
        # Prepare enhanced context with multiple chunks
        context_parts = []
        for i, (chunk, score) in enumerate(relevant_chunks[:3]):
            context_parts.append(f"[Context {i+1}] {chunk['text'][:400]}")
        
        context = "\n\n".join(context_parts)
        
        # Try Gemini API first with enhanced context
        gemini_answer = self.try_gemini_api(question, context)
        
        # Use appropriate response method
        if gemini_answer and len(gemini_answer.strip()) > 20:
            answer = gemini_answer
            print("🤖 Using AI-enhanced response")
        else:
            answer = self.get_smart_answer(question, relevant_chunks)
            print("📋 Using document-based fallback response")
        
        # Prepare sources (but don't include in response as per user request)
        sources = []
        for chunk, score in relevant_chunks[:3]:
            sources.append({
                'source': chunk['source'],
                'score': round(score, 1),
                'preview': chunk['text'][:120] + "..."
            })
        
        return {
            'answer': answer,
            'sources': sources  # Available but not displayed in UI
        }