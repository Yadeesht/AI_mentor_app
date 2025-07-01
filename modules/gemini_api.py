import google.generativeai as genai

def generate_gemini_response(context_chunks: list, query: str, subject: str):
    genai.configure(api_key='AIzaSyAkve1auCv57naXqkihuSypKNhHXkZRr3M')

    # Build context from chunks
    if context_chunks and any(chunk.strip() for chunk in context_chunks if chunk):
        context = "\n---\n".join(context_chunks)
        prompt = f"""
You are a knowledgeable and friendly AI tutor helping a student understand a topic in **{subject}**.

📄 Subject Content (from uploaded files):
{context}

🎓 Student's Question:
{query}

🧠 Answer Instructions:
- Use ONLY the subject content above.
- Be clear, concise, and technically accurate.
- Write like you're speaking to a student — friendly, but not oversimplified.
- Give 2–4 short sentences that an avatar can read aloud clearly.
- If the content includes definitions, features, problems, or examples — mention them.
"""
    else:
        prompt = f"""
You are a knowledgeable and friendly AI tutor helping a student understand a topic in **{subject}**.

🎓 Student's Question:
{query}

🧠 Answer Instructions:
- Use ONLY your knowledge of the subject to answer the question.
- ❗ DO NOT make assumptions. If the question is unrelated to the subject, respond with: "Sorry, this topic is not included in the subject."
- Be clear, concise, and technically accurate.
- Write in 2–4 sentences for an avatar to speak aloud.
- If there is no related student content provided like this "📄 Subject Content (from uploaded files):" you may end with: "This topic was not found in the provided material."
"""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Error] An error occurred with the Gemini model: {e}"
