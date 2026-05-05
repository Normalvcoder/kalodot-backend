import base64
import json
import io
import time
from flask import request, jsonify
from PIL import Image
from app import app, client

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
        Analyze the attached image of food. Identify the primary food items and estimate the total 
        calories based on a standard, average portion size in grams (metric system). 
        Return ONLY a valid JSON object with no markdown formatting or code blocks. 
        The JSON must have exactly these three keys: 
        'food_name' (string), 
        'estimated_calories' (integer), 
        'macro_breakdown' (string, e.g., 'Protein: 20g, Carbs: 30g, Fat: 10g').
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