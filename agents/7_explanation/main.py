import os
import json
import google.generativeai as genai
from fastapi import FastAPI, Request
from dotenv import load_dotenv
load_dotenv()
# --- Configuration ---
# Make sure to set your GOOGLE_API_KEY in your environment
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    generation_config = {
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 4096,
        "response_mime_type": "application/json", # Specify JSON output
    }
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
    )
    print("Gemini model configured successfully.")
    GEMINI_AVAILABLE = True
except KeyError:
    print("Warning: GOOGLE_API_KEY environment variable not set. Gemini will not be available.")
    GEMINI_AVAILABLE = False
except Exception as e:
    print(f"An error occurred during Gemini configuration: {e}")
    GEMINI_AVAILABLE = False


app = FastAPI(title="Explanation Agent")

# --- Default Fallback Logic ---
# Your original function, renamed to be the default/fallback
def explain_default(s: dict) -> dict:
    """The default rule-based explanation logic."""
    parts = []
    f = s.get("features", {}) # Use .get for safer access

    if f.get("origin_storm"):
        parts.append("heavy storm at origin")
    if f.get("origin_rain_mm", 0) > 10:
        parts.append("significant rainfall")
    if f.get("congestion_index", 0) >= 0.5:
        parts.append("peak-hour congestion")
    if f.get("distance_km", 0) > 400:
        parts.append("long route distance")
    if not parts:
        parts.append("minor traffic and weather factors")

    actions = []
    delay_prob = s.get("delay_prob", 0)
    if delay_prob >= 0.6:
        actions = ["Notify customer of possible delay", "Consider alternate route or dispatch offset"]
    elif delay_prob >= 0.3:
        actions = ["Monitor closely", "Pre-position resources for potential delay"]
    else:
        actions = ["No action needed"]

    s["summary"] = f"Order {s.get('shipment_id', 'N/A')} risk {int(delay_prob*100)}% due to " + ", ".join(parts) + "."
    s["actions"] = actions
    return s

# --- Gemini Logic ---
async def explain_with_gemini(s: dict) -> dict:
    """Generates an explanation using the Gemini API."""
    prompt = f"""
    You are a logistics and supply chain analyst. Your task is to analyze shipment data and provide a concise summary and recommended actions.

    Based on the following shipment JSON data, generate a response in a valid JSON format with two keys: "summary" and "actions".

    - The 'summary' should be a single, human-readable sentence explaining the risk.
    - The 'actions' should be a JSON array of strings with specific, actionable recommendations.

    Shipment Data:
    {json.dumps(s, indent=2)}

    Example Output Format:
    {{
      "summary": "Order [shipment_id] has a high risk of delay due to peak-hour congestion and a long route.",
      "actions": ["Notify customer of possible delay", "Monitor traffic conditions closely"]
    }}
    """
    
    try:
        response = await model.generate_content_async(prompt)
        # The API returns a JSON string, so we need to parse it
        gemini_result = json.loads(response.text)
        
        # Merge Gemini's output back into the original shipment dictionary
        s["summary"] = gemini_result.get("summary", "No summary generated.")
        s["actions"] = gemini_result.get("actions", ["No actions generated."])
        s["explained_by"] = "gemini" # Add a field to know who explained it
        return s
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        # Re-raise the exception to be caught by the endpoint's try/except block
        raise

# --- API Endpoints ---
@app.get("/health")
def health():
    return {"status": "alive", "gemini_available": GEMINI_AVAILABLE}

@app.post("/explain")
async def explain_endpoint(request: Request):
    shipment = await request.json()
    # Try to use Gemini first if it's available
    if GEMINI_AVAILABLE:
        try:
            print("Gemini")
            return await explain_with_gemini(shipment)
        except Exception as e:
            print(f"Switching to default explanation due to Gemini failure: {e}")
            # Fallback to default logic if Gemini fails
            response = explain_default(shipment)
            response["explained_by"] = "default_fallback"
            return response
    else:
        # Use default logic if Gemini was never configured
        response = explain_default(shipment)
        response["explained_by"] = "default"
        return response