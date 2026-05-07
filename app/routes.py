import base64
import json
import io
import time
from flask import request, jsonify
from PIL import Image
from app import app, client
from .auth import require_api_key

@app.route('/analyze', methods=['POST'])
def analyze_food():
    try:
        data = request.get_json()
        if 'image_data' not in data:
            return jsonify({"error": "No image data found"}), 400

        base64_string = data['image_data']
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_bytes))

        prompt = """
    You are an expert nutritionist AI analyzing a meal.
    You must respond ONLY with a raw, valid JSON object. 
    Do NOT include Markdown formatting like ```json or any conversational text.
    
    You must calculate the portion size in grams or milliliters.
    
    Your JSON must contain exactly these four keys:
    1. "food_name": The name of the dish and portion size (e.g., "Grilled Salmon (approx. 200g)").
    2. "estimated_calories": An integer representing total kcal.
    3. "macro_breakdown": A string summarizing macros (e.g., "40g Protein | 0g Carbs | 15g Fat").
    
    EDGE CASE: If the image clearly does not contain food or drinks, you must return:
    {"food_name": "Error: No food detected", "estimated_calories": 0, "macro_breakdown": "N/A"}
    """

        print("Sending to AI for analysis...")
        start_time = time.time()
        
        
        max_retries = 3
        response = None
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[image, prompt]
                )
                break 
                
            except Exception as api_error:
                error_string = str(api_error)
                
                # Catch BOTH 503 (Busy) and 429 (Rate Limit)
                if ("503" in error_string or "429" in error_string) and attempt < max_retries - 1:
                    print(f"Rate limit or server busy. Retrying in 5 seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(5) # Wait 5 seconds to clear the Google timeout
                else:
                    # If we are out of retries, or it's a completely different error, crash
                    raise api_error
        # ------------------------------------------------
        
        elapsed = time.time() - start_time
        print(f"Gemini finished in {elapsed:.2f} seconds.")
        
        response_text = response.text.strip()
        
        # Fixed the line break right here!
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
            
        result_json = json.loads(response_text)
        
        print(f"Success! Found: {result_json.get('food_name')}")
        return jsonify(result_json), 200

    except Exception as e:
        print(f"CRASH REPORT: {str(e)}")
        return jsonify({"error": str(e)}), 500