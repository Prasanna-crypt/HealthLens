import json
import re
from openai import OpenAI
from sqlalchemy.orm import Session
from ..config import settings

# ── Health Disclaimer & Detection ───────────────────────────────────────────
HEALTH_DISCLAIMER = (
    "\n\n---\n*Disclaimer: HealthLens is for educational purposes only. "
    "It is not a medical diagnosis. Always consult a qualified healthcare professional.*"
)

# Common medical terms, lab tests, and symptoms to detect health-related questions
HEALTH_KEYWORDS = {
    # Lab tests & biomarkers
    "hemoglobin", "hb", "cholesterol", "ldl", "hdl", "vldl", "triglyceride",
    "glucose", "sugar", "diabetes", "creatinine", "urea", "bun", "platelet",
    "platelets", "wbc", "rbc", "bilirubin", "sgpt", "sgot", "alt", "ast",
    "tsh", "thyroid", "calcium", "sodium", "potassium", "chloride", "iron",
    "ferritin", "vitamin", "b12", "d3", "albumin", "globulin", "uric", "lipid",
    "cbc", "lft", "kft", "hba1c",
    # Medical, anatomy & symptom terms
    "blood", "pressure", "bp", "pulse", "heart", "kidney", "liver", "lung",
    "urine", "stool", "fever", "pain", "headache", "cough", "infection",
    "inflammation", "fatigue", "tired", "weakness", "dizziness", "nausea",
    "symptom", "symptoms", "disease", "condition", "illness", "syndrome",
    "doctor", "hospital", "clinic", "physician", "medicine", "medication",
    "pill", "drug", "tablet", "dosage", "dose", "treatment", "cure", "remedy",
    "remedies", "therapy", "diet", "nutrition", "exercise", "lifestyle",
    "health", "healthy", "test", "tests", "report", "reports", "result",
    "results", "range", "ranges", "normal", "abnormal", "high", "low",
    "elevated", "deficiency", "level", "levels", "value", "values", "count",
    "diagnose", "diagnosis"
}

# Instant Local Responses for standard casual queries (0ms latency, zero API trip)
FAST_CASUAL_RESPONSES = {
    "hi": "Hey! 👋 How can I help you today? You can ask me about your recent lab tests, normal ranges, or natural lifestyle tips!",
    "hello": "Hello! 👋 I'm here to help explain your lab results or health questions. What would you like to know?",
    "hey": "Hey! 👋 How's it going? Ask me anything about your medical reports or health biomarkers.",
    "good morning": "Good morning! ☀️ How can I assist you with your health reports today?",
    "good afternoon": "Good afternoon! 👋 How can I help you review your health records today?",
    "good evening": "Good evening! 🌙 What would you like to check in your health reports?",
    "thanks": "You're very welcome! 😊 Let me know if you need help with anything else.",
    "thank you": "Glad I could help! 😊 Feel free to ask if you have more questions about your reports.",
    "who are you": "I'm HealthLens Assistant! 🩺 I help you understand your lab reports, track biomarker changes, and suggest natural lifestyle tips.",
    "what can you do": "I can help you:\n• Understand your lab numbers (e.g. Hemoglobin, Sugar, Cholesterol)\n• Compare results across your uploaded reports\n• Provide natural diet & lifestyle suggestions\n• Answer common health questions!"
}

def is_health_question(text: str) -> bool:
    """
    Backend feature: detects whether the user's question is health/medical related.
    Returns True for test results, symptoms, medical queries.
    Returns False for casual greetings, small talk, and thank yous.
    """
    if not text:
        return False

    clean = text.lower().strip()

    # If it's a known short casual phrase
    stripped = clean.rstrip("!.?, ")
    if stripped in FAST_CASUAL_RESPONSES:
        return False

    # Check for keyword matches
    words = set(re.findall(r'\b[a-z0-9]+\b', clean))
    if words.intersection(HEALTH_KEYWORDS):
        return True

    # Check for substring matches for compound terms
    for kw in HEALTH_KEYWORDS:
        if kw in clean:
            return True

    return False

# ── AI Safety Rules ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a knowledgeable and supportive health assistant for the HealthLens app.

CONVERSATION RULES:
- When answering a health question or inquiry about medical reports, ANSWER DIRECTLY without generic greeting intros like "Hey! 👋 How can I help you today?". Jump straight into the explanation or answer.
- Only use greetings (like "Hey! 👋 How can I help you?") if the user specifically just said hello or greeted you.
- Be clear, conversational, and direct.

HEALTH & SAFETY RULES (apply when the user asks a health-related question):
1. Never diagnose any disease or medical condition.
2. Never recommend any prescription or OTC medication.
3. Use cautious language ("may indicate" or "could suggest").
4. Suggest only natural remedies, dietary improvements, and lifestyle adjustments for abnormal results.
5. End health-related answers with: "Always check with your doctor to be sure! 😊"

NOTE: Do NOT write formal disclaimer footers yourself — the backend automatically appends the official disclaimer.
"""

def get_ai_client():
    """Returns an OpenAI client. Prefers OpenAI key, falls back to NVIDIA."""
    if settings.OPENAI_API_KEY:
        return OpenAI(api_key=settings.OPENAI_API_KEY, timeout=45.0)
    if settings.NVIDIA_API_KEY:
        return OpenAI(api_key=settings.NVIDIA_API_KEY, base_url=settings.NVIDIA_BASE_URL, timeout=45.0)
    return None

def get_model_name():
    """Returns which AI model name to use based on which API key is set."""
    if settings.OPENAI_API_KEY:
        return settings.OPENAI_MODEL
    return settings.NVIDIA_MODEL

def call_ai(prompt: str, max_tokens: int = 1024, is_health: bool = False) -> str:
    """
    Sends a prompt to the AI and returns its response as a string.
    This is the single shared function all other functions use.
    Returns an error message string if the AI call fails.
    """
    client = get_ai_client()
    if not client:
        return "AI is unavailable. Please check your API key in the .env file."

    try:
        response = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.3,   # Low = more factual, less creative
            max_tokens=max_tokens,
        )
        answer = response.choices[0].message.content
        if is_health:
            return answer + HEALTH_DISCLAIMER
        return answer

    except Exception as error:
        print(f"[HealthLens] AI call failed: {error}")
        return "AI is temporarily unavailable."


# ── Natural Remedies Knowledge Base ───────────────────────────────────────────
# Medically accurate, lifestyle & nutrition-only guidance (Strictly NO medications)
NATURAL_REMEDIES = {
    "hemoglobin": {
        "what": "measures the iron-rich protein in red blood cells that carries oxygen throughout your body.",
        "low_insight": "A lower reading may suggest reduced iron stores, fatigue, or low red blood cell production.",
        "low_remedies": [
            "Enjoy iron-rich whole foods like spinach, lentils, beets, black raisins, and pumpkin seeds.",
            "Pair iron-rich meals with Vitamin C (citrus fruits, amla, lemon) to boost natural iron absorption.",
            "Maintain steady daily hydration and 7-8 hours of restful sleep for cellular renewal."
        ],
        "high_insight": "A higher reading is often related to dehydration, high altitude, or temporary hemoconcentration.",
        "high_remedies": [
            "Drink plenty of water (2.5 to 3 liters daily) to maintain optimal blood plasma volume.",
            "Avoid tobacco smoke and secondhand smoke, which can artificially trigger elevated hemoglobin.",
            "Engage in regular moderate aerobic exercise such as brisk walking, cycling, or swimming."
        ]
    },
    "platelets": {
        "what": "measures cell fragments essential for normal blood clotting and tissue repair.",
        "low_insight": "Low platelets may occur during or after viral recovery or temporary immune stress.",
        "low_remedies": [
            "Incorporate nutrient-dense foods like fresh papaya, kiwi, pomegranate, and dark leafy greens.",
            "Stay well hydrated with fresh coconut water and warm broths to support circulation.",
            "Prioritize physical rest, avoid strenuous contact sports, and ensure deep restorative sleep."
        ],
        "high_insight": "Elevated platelets frequently reflect a natural, temporary inflammatory or healing response.",
        "high_remedies": [
            "Consume natural anti-inflammatory foods rich in omega-3s, turmeric with black pepper, and ginger.",
            "Stay well-hydrated throughout the day to support smooth blood viscosity.",
            "Engage in gentle daily walks and restorative stretching to promote healthy circulation."
        ]
    },
    "wbc": {
        "what": "measures white blood cells, the core defenders of your immune system.",
        "low_insight": "A lower count can indicate recent viral recovery or lowered immune defense reserves.",
        "low_remedies": [
            "Support immunity with zinc- and vitamin C-rich foods (citrus fruits, sunflower seeds, garlic).",
            "Prioritize consistent 7-8 hours of sleep to allow immune cell generation.",
            "Practice stress-relief techniques like gentle breathing exercises or mindful walking."
        ],
        "high_insight": "A higher count typically means your body is actively fighting off mild infection or inflammation.",
        "high_remedies": [
            "Allow your body adequate rest and recovery time; avoid strenuous overexertion.",
            "Drink plenty of warm herbal fluids, ginger tea, and clear vegetable broths.",
            "Eat light, easily digestible, antioxidant-rich meals with fresh fruits and steamed vegetables."
        ]
    },
    "glucose": {
        "what": "measures circulating blood sugar, the primary fuel source for your body's cells.",
        "low_insight": "Lower blood sugar may be caused by delayed meals, intense exertion, or low carbohydrate intake.",
        "low_remedies": [
            "Consume balanced, evenly spaced meals featuring complex carbohydrates and lean proteins.",
            "Carry wholesome snacks like a handful of almonds, roasted chickpeas, or fresh fruit.",
            "Avoid long fasting windows and maintain consistent meal schedules."
        ],
        "high_insight": "Higher blood sugar levels suggest insulin resistance or excess dietary refined carbohydrates.",
        "high_remedies": [
            "Switch to low-glycemic, fiber-rich whole grains (oats, quinoa, brown rice, chia seeds).",
            "Take a brisk 10 to 15-minute walk immediately following your main meals.",
            "Incorporate cinnamon into warm water or soaked fenugreek seeds in the morning, and minimize refined sugars."
        ]
    },
    "cholesterol": {
        "what": "evaluates circulating lipids essential for hormone synthesis and cell membrane integrity.",
        "low_insight": "Very low total cholesterol is uncommon and can reflect nutritional deficiencies or rapid metabolism.",
        "low_remedies": [
            "Include nutrient-dense healthy fats like avocados, walnuts, extra virgin olive oil, and sesame seeds.",
            "Ensure adequate overall caloric intake with well-balanced whole meals."
        ],
        "high_insight": "Elevated cholesterol or LDL may contribute to plaque buildup in arterial walls over time.",
        "high_remedies": [
            "Boost soluble fiber daily with oatmeal, flaxseeds, psyllium husk, and beans.",
            "Replace saturated and trans fats with heart-healthy monounsaturated fats (extra virgin olive oil, nuts).",
            "Aim for at least 30 minutes of brisk cardiovascular activity 5 days a week."
        ]
    },
    "triglycerides": {
        "what": "measures the most common type of fat in your bloodstream, derived from unused dietary calories.",
        "low_insight": "Low triglycerides are generally healthy and indicate efficient metabolic fat clearance.",
        "low_remedies": [
            "Maintain your balanced whole-foods nutrition and healthy active lifestyle."
        ],
        "high_insight": "Elevated triglycerides are often connected to refined sugar intake, refined flours, or sedentary habits.",
        "high_remedies": [
            "Significantly cut back on sugary drinks, sodas, fruit juices, and bakery sweets.",
            "Incorporate omega-3 fatty acids through chia seeds, flaxseeds, and walnuts.",
            "Engage in regular aerobic exercise such as jogging or brisk walking to burn circulating fats."
        ]
    },
    "creatinine": {
        "what": "measures a metabolic waste product filtered out of the blood by healthy kidneys.",
        "low_insight": "Low creatinine is usually benign and can reflect low muscle mass or a light vegetarian diet.",
        "low_remedies": [
            "Include adequate quality dietary protein (legumes, lentils, Greek yogurt, tofu) and gentle resistance exercise."
        ],
        "high_insight": "Elevated creatinine can indicate reduced kidney filtration efficiency, dehydration, or heavy muscle breakdown.",
        "high_remedies": [
            "Increase pure water intake (2.5 to 3 liters daily) to aid kidney filtration.",
            "Avoid excessive red meat, excessive synthetic creatine powders, and high-dose protein supplements.",
            "Avoid extreme exhaustive workouts immediately prior to blood testing."
        ]
    },
    "urea": {
        "what": "measures nitrogen waste from protein breakdown cleared by the liver and kidneys.",
        "low_insight": "Low urea can result from a low-protein diet, overhydration, or high fluid intake.",
        "low_remedies": [
            "Maintain a balanced intake of whole proteins across your daily meals."
        ],
        "high_insight": "High urea levels often signal mild dehydration, a very high-protein intake, or decreased kidney clearance.",
        "high_remedies": [
            "Prioritize consistent hydration with clean water, herbal teas, and coconut water.",
            "Balance your daily protein portions and focus on plant-based legumes and lentils.",
            "Limit high-sodium processed foods that strain fluid balance."
        ]
    },
    "uric_acid": {
        "what": "measures the byproduct formed when your body breaks down natural purines found in foods.",
        "low_insight": "Low uric acid is uncommon and generally harmless.",
        "low_remedies": [
            "Continue eating a diverse, balanced whole-foods diet."
        ],
        "high_insight": "High uric acid can crystallize in joints (gout) or form kidney stones if unmanaged.",
        "high_remedies": [
            "Drink 2.5 to 3 liters of water daily to help flush excess uric acid through the kidneys.",
            "Enjoy fresh tart cherries or unsweetened tart cherry juice, which naturally supports uric acid excretion.",
            "Reduce purine-rich foods (red meats, shellfish, yeast-rich items) and avoid high-fructose corn syrup."
        ]
    },
    "bilirubin": {
        "what": "measures the yellow pigment formed during the normal natural breakdown of red blood cells.",
        "low_insight": "Low bilirubin is generally a benign finding with no clinical concern.",
        "low_remedies": [
            "Maintain your healthy daily diet and balanced fluid intake."
        ],
        "high_insight": "Elevated bilirubin indicates that liver processing or bile duct drainage may be sluggish or stressed.",
        "high_remedies": [
            "Support liver detox with fresh cruciferous vegetables (broccoli, cabbage, radish) and beetroot.",
            "Drink warm lemon water and herbal teas (like dandelion or green tea) to encourage bile flow.",
            "Avoid oily, deep-fried street foods and stay strictly hydrated."
        ]
    },
    "alt": {
        "what": "measures an enzyme predominantly found in liver cells that spills into blood during liver strain.",
        "low_insight": "Low ALT is normal and indicates healthy liver tissue integrity.",
        "low_remedies": [
            "Keep up your current nutritious diet and active lifestyle."
        ],
        "high_insight": "Elevated ALT suggests acute or ongoing liver cellular stress or fatty liver changes.",
        "high_remedies": [
            "Reduce refined carbohydrates, deep-fried items, and eliminate alcohol to protect liver cells.",
            "Incorporate liver-cleansing foods like garlic, turmeric, grapefruit, and leafy greens.",
            "Aim for 150 minutes of moderate exercise per week to reduce visceral and hepatic fat."
        ]
    },
    "ast": {
        "what": "measures an enzyme present in the liver, heart, and muscle tissue.",
        "low_insight": "Low AST is standard and indicates normal cellular stability.",
        "low_remedies": [
            "Continue your regular healthy wellness routine."
        ],
        "high_insight": "Elevated AST can reflect liver strain, vigorous heavy exercise, or muscle tissue soreness.",
        "high_remedies": [
            "Ensure adequate muscle recovery days between intense workouts.",
            "Consume antioxidant-rich berries, green tea, and cruciferous vegetables.",
            "Maintain optimal daily hydration to help flush metabolic cellular byproducts."
        ]
    },
    "tsh": {
        "what": "measures the master pituitary hormone that signals your thyroid to regulate metabolism.",
        "low_insight": "Low TSH suggests an overactive thyroid (hyperthyroid state) with accelerated metabolism.",
        "low_remedies": [
            "Avoid excessive caffeine, energy drinks, and intense stimulants.",
            "Practice cooling and calming relaxation exercises like deep diaphragmatic breathing and gentle yoga.",
            "Consume cruciferous vegetables (broccoli, cauliflower) which naturally help modulate thyroid activity."
        ],
        "high_insight": "High TSH indicates a sluggish thyroid (hypothyroid state) needing extra encouragement.",
        "high_remedies": [
            "Ensure adequate dietary selenium by eating 1 to 2 Brazil nuts daily.",
            "Consume zinc-rich pumpkin seeds and lentils to support thyroid hormone conversion.",
            "Manage chronic daily stress and prioritize 8 hours of restful sleep."
        ]
    },
    "vitamin_d": {
        "what": "evaluates 25-hydroxy vitamin D, essential for bone mineralization, calcium uptake, and immunity.",
        "low_insight": "Low Vitamin D is very common and can cause low energy, bone aches, and sluggish immunity.",
        "low_remedies": [
            "Get 15 to 20 minutes of direct morning sunlight exposure on arms and legs several times weekly.",
            "Include fortified dairy or plant milks, egg yolks, and sun-exposed mushrooms in your diet.",
            "Discuss with your doctor if an over-the-counter vitamin D3 supplement is appropriate for your baseline."
        ],
        "high_insight": "Elevated Vitamin D is rare and typically occurs only from excessive high-dose supplementation.",
        "high_remedies": [
            "Pause any external high-dose vitamin D supplements and recheck after a few weeks.",
            "Drink plenty of water to support normal renal calcium clearance."
        ]
    },
    "vitamin_b12": {
        "what": "measures a vital nutrient needed for nerve function, brain health, and red blood cell creation.",
        "low_insight": "Low B12 can lead to fatigue, tingling in fingers/toes, brain fog, and anemia.",
        "low_remedies": [
            "Incorporate fortified nutritional yeast, fortified cereals, and fermented yogurts/paneer into meals.",
            "Improve digestive gut absorption by chewing thoroughly and eating probiotic foods (kefir, curd).",
            "Consult your healthcare provider to evaluate if an active B12 supplement is recommended."
        ],
        "high_insight": "High B12 is usually benign, often caused by recent multivitamin intake.",
        "high_remedies": [
            "Check multivitamin ingredients to avoid unnecessary megadoses.",
            "Maintain consistent daily water intake."
        ]
    },
    "calcium": {
        "what": "measures the essential mineral responsible for bone structure, muscle contraction, and nerve signals.",
        "low_insight": "Low calcium can lead to muscle cramps, brittle nails, and bone density loss.",
        "low_remedies": [
            "Incorporate calcium-rich sesame seeds, chia seeds, almonds, dark leafy greens, and dairy.",
            "Pair calcium intake with adequate morning sunlight for natural Vitamin D synergy."
        ],
        "high_insight": "Elevated calcium may relate to dehydration, thyroid/parathyroid activity, or over-supplementation.",
        "high_remedies": [
            "Stay thoroughly hydrated with 2.5 to 3 liters of water to help kidneys excrete excess calcium.",
            "Pause any calcium-fortified pills and review dietary sources with your doctor."
        ]
    }
}

# Aliases mapping test names to canonical remedy keys
REMEDY_ALIASES = {
    "hb": "hemoglobin", "hemoglobin": "hemoglobin", "haemoglobin": "hemoglobin", "rbc": "hemoglobin", "hematocrit": "hemoglobin", "pcv": "hemoglobin",
    "plt": "platelets", "platelet": "platelets", "platelets": "platelets", "platelet count": "platelets",
    "wbc": "wbc", "tlc": "wbc", "leukocyte": "wbc", "leukocytes": "wbc", "neutrophil": "wbc", "lymphocyte": "wbc",
    "glucose": "glucose", "blood sugar": "glucose", "fasting blood sugar": "glucose", "fbs": "glucose", "ppbs": "glucose", "post prandial": "glucose", "hba1c": "glucose",
    "cholesterol": "cholesterol", "total cholesterol": "cholesterol", "ldl": "cholesterol", "ldl cholesterol": "cholesterol", "vldl": "cholesterol",
    "triglyceride": "triglycerides", "triglycerides": "triglycerides",
    "creatinine": "creatinine", "serum creatinine": "creatinine", "egfr": "creatinine",
    "urea": "urea", "blood urea": "urea", "bun": "urea", "blood urea nitrogen": "urea",
    "uric acid": "uric_acid", "serum uric acid": "uric_acid", "urate": "uric_acid",
    "bilirubin": "bilirubin", "total bilirubin": "bilirubin", "direct bilirubin": "bilirubin", "indirect bilirubin": "bilirubin",
    "sgpt": "alt", "alt": "alt", "alanine aminotransferase": "alt", "alanine transaminase": "alt",
    "sgot": "ast", "ast": "ast", "aspartate aminotransferase": "ast", "aspartate transaminase": "ast",
    "tsh": "tsh", "thyroid stimulating hormone": "tsh", "t3": "tsh", "t4": "tsh", "free t3": "tsh", "free t4": "tsh",
    "vitamin d": "vitamin_d", "vitamin d3": "vitamin_d", "25-hydroxy vitamin d": "vitamin_d", "vit d": "vitamin_d",
    "vitamin b12": "vitamin_b12", "b12": "vitamin_b12", "vit b12": "vitamin_b12", "cyanocobalamin": "vitamin_b12",
    "calcium": "calcium", "serum calcium": "calcium"
}

def find_remedy_entry(test_name: str) -> dict | None:
    """Finds natural remedy guidelines for a given lab test name."""
    clean = re.sub(r'[^a-z0-9 ]+', ' ', str(test_name).lower()).strip()
    
    # 1. Exact alias match
    if clean in REMEDY_ALIASES:
        return NATURAL_REMEDIES.get(REMEDY_ALIASES[clean])
        
    # 2. Substring matching in aliases
    for alias, canonical in REMEDY_ALIASES.items():
        if alias in clean or clean in alias:
            return NATURAL_REMEDIES.get(canonical)
            
    # 3. Direct key search
    for key in NATURAL_REMEDIES:
        if key in clean:
            return NATURAL_REMEDIES.get(key)
            
    return None

def get_natural_tips_for_test(test_name: str, status: str) -> list[str]:
    """Returns a list of 2-3 natural lifestyle tips for a test based on its status."""
    entry = find_remedy_entry(test_name)
    if not entry:
        if status == 'LOW':
            return [
                f"Nourish your body with wholesome, nutrient-dense whole foods to gently support {test_name}.",
                "Ensure steady hydration and 7-8 hours of restful sleep daily.",
                "Review with your healthcare professional to investigate potential root factors."
            ]
        elif status == 'HIGH':
            return [
                "Drink 2.5 to 3 liters of water daily to support natural metabolic clearance.",
                "Focus on fiber-rich fresh vegetables and eliminate ultra-processed or sugary snacks.",
                "Engage in 20-30 minutes of gentle daily walking to promote circulation."
            ]
        return ["Maintain your wholesome diet, daily hydration, and active lifestyle routine."]
        
    if status == 'LOW':
        return entry.get("low_remedies", [])
    elif status == 'HIGH':
        return entry.get("high_remedies", [])
    return ["Maintain your wholesome diet, daily hydration, and active lifestyle routine."]

def generate_fast_test_explanation(test_name: str, value: float, unit: str,
                                   ref_low: float | None, ref_high: float | None,
                                   status: str) -> str:
    """
    Instantly (<0.1ms) generates a clear, medically grounded, natural-only explanation
    for any lab test result without blocking or calling external APIs.
    """
    u = f" {unit}".strip() if unit else ""
    if ref_low is not None and ref_high is not None:
        ref_text = f"{ref_low} – {ref_high}{u}"
    else:
        ref_text = "Standard clinical range"

    # 1. Normal Test Result
    if status == 'NORMAL':
        return (
            f"{test_name} is at {value}{u}, which is well within your healthy normal range ({ref_text}). "
            f"Your body is maintaining balanced regulation for this biomarker. "
            f"Keep up your consistent hydration, wholesome meals, and active routine!"
        )

    # 2. Abnormal Result (LOW or HIGH)
    entry = find_remedy_entry(test_name)
    status_label = "lower than" if status == 'LOW' else "elevated above"

    if entry:
        what_str = entry.get("what", "is an important health biomarker.")
        insight = entry.get("low_insight" if status == 'LOW' else "high_insight", "")
        remedies = entry.get("low_remedies" if status == 'LOW' else "high_remedies", [])
        
        tips_formatted = "\n".join([f"• {tip}" for tip in remedies])
        return (
            f"{test_name} is at {value}{u}, which is {status_label} the standard reference range ({ref_text}). "
            f"This test {what_str} {insight}\n\n"
            f"Natural Lifestyle & Nutrition Tips:\n{tips_formatted}\n\n"
            f"*Always discuss this result with your doctor for clinical confirmation.*"
        )

    # 3. Fallback for uncatalogued biomarkers
    tips = get_natural_tips_for_test(test_name, status)
    tips_formatted = "\n".join([f"• {tip}" for tip in tips])
    return (
        f"{test_name} measured at {value}{u}, which is {status_label} the reference range ({ref_text}).\n\n"
        f"General Natural Wellness Steps:\n{tips_formatted}\n\n"
        f"*Please consult your healthcare provider for evaluation against your personal medical history.*"
    )

def generate_structured_report_summary(test_results: list[dict]) -> str:
    """
    Instantly (<0.5ms) creates a rich, structured markdown summary of the entire
    report, highlighting optimal markers, flagged values, and customized natural remedies.
    """
    total = len(test_results)
    if total == 0:
        return "No lab biomarkers were detected in this report."

    normal_tests = [r for r in test_results if r.get('status') == 'NORMAL']
    low_tests = [r for r in test_results if r.get('status') == 'LOW']
    high_tests = [r for r in test_results if r.get('status') == 'HIGH']
    flagged = low_tests + high_tests

    # Overall Status Assessment
    if not flagged:
        status_line = "✅ **Overall Status: Optimal** — All analyzed biomarkers fall comfortably within standard reference limits."
    elif len(flagged) <= 2:
        status_line = f"⚠️ **Overall Status: Good with Mild Variations** — {len(normal_tests)} of {total} biomarkers are normal, with {len(flagged)} area(s) to monitor naturally."
    else:
        status_line = f"🔍 **Overall Status: Attention Recommended** — {len(flagged)} biomarkers are outside standard reference ranges and warrant lifestyle adjustments and medical review."

    lines = [
        "### 📋 HealthLens Report Summary",
        f"{status_line}",
        "",
        f"- **Total Tests Evaluated:** {total}",
        f"- **Optimal Biomarkers:** {len(normal_tests)}",
        f"- **Biomarkers Outside Range:** {len(flagged)}",
        ""
    ]

    if flagged:
        lines.append("#### 🔬 Key Biomarkers Requiring Attention")
        for r in flagged:
            ref = "N/A"
            if r.get("reference_low") is not None and r.get("reference_high") is not None:
                ref = f"{r['reference_low']} – {r['reference_high']} {r.get('unit', '')}".strip()
            badge = "🔻 LOW" if r.get('status') == 'LOW' else "🔺 HIGH"
            lines.append(f"- **{r.get('test_name', 'Test')}**: **{r.get('value')} {r.get('unit', '')}** ({badge} | Reference: {ref})")
        lines.append("")

        # Aggregate natural remedies from flagged tests
        lines.append("#### 🌿 Recommended Natural Lifestyle & Nutritional Steps")
        tips_collected = []
        for r in flagged:
            remedies = get_natural_tips_for_test(r.get('test_name', ''), r.get('status', ''))
            for tip in remedies:
                if tip not in tips_collected:
                    tips_collected.append(tip)

        if not tips_collected:
            tips_collected = [
                "Prioritize consistent hydration with 2 to 2.5 liters of clean water daily.",
                "Focus on a colorful, fiber-rich whole-foods diet with minimal refined sugars and processed fats.",
                "Incorporate 20-30 minutes of daily moderate movement such as walking or light jogging.",
                "Aim for 7-8 hours of uninterrupted, restorative sleep to support natural metabolic recovery."
            ]

        for tip in tips_collected[:5]:  # Top 5 most relevant unique tips
            lines.append(f"• {tip}")
        lines.append("")
    else:
        lines.append("#### 🌟 Health & Wellness Maintenance")
        lines.append("• Maintain your balanced whole-foods nutrition rich in fiber, greens, and lean proteins.")
        lines.append("• Keep up regular hydration and daily physical activity (at least 30 minutes of moderate exercise).")
        lines.append("• Preserve healthy sleep hygiene and stress management to maintain consistent biomarker vitality.")
        lines.append("")

    lines.append("---")
    lines.append("*Disclaimer: HealthLens is for educational purposes only. It is not a medical diagnosis. Always consult a qualified healthcare professional regarding any abnormal test results or before making significant dietary changes.*")

    return "\n".join(lines)


# ── Public Functions ─────────────────────────────────────────────────────────

def generate_report_summary(test_results: list[dict]) -> str:
    """
    Generates a structured, plain-English summary of all test results in <1ms.
    Eliminates multi-minute remote AI network latencies.
    """
    return generate_structured_report_summary(test_results)


def generate_test_explanation(test_name: str, value: float, unit: str,
                               ref_low: float | None, ref_high: float | None,
                               status: str) -> str:
    """
    Instantly explains an individual test result with natural lifestyle tips.
    Eliminates multi-minute remote AI network latencies.
    """
    return generate_fast_test_explanation(test_name, value, unit, ref_low, ref_high, status)


def stream_ai_assistant(user_question: str, user_id: int, db: Session):
    """
    Streaming version of the AI chat assistant.
    Yields text chunks as the AI generates them — words appear on screen instantly
    instead of waiting for the full response to finish.
    """
    from ..models.report import Report

    client = get_ai_client()
    if not client:
        yield "AI is unavailable. Please check your API key in the .env file."
        return

    # 0ms Instant Response for common greetings and short phrases
    clean_q = user_question.lower().strip().rstrip("!.?, ")
    if clean_q in FAST_CASUAL_RESPONSES:
        yield FAST_CASUAL_RESPONSES[clean_q]
        return

    is_health = is_health_question(user_question)

    # Load only the most recent report to keep the prompt short
    recent_reports = (
        db.query(Report)
        .filter(Report.user_id == user_id)
        .order_by(Report.report_date.desc())
        .limit(1)
        .all()
    )

    if recent_reports:
        context = "USER'S LATEST TEST RESULTS:\n"
        for report in recent_reports:
            context += f"Report date: {report.report_date}\n"
            for test in report.test_results:
                context += f"  - {test.test_name}: {test.value} {test.unit} ({test.status})\n"
    else:
        context = "No medical reports uploaded yet.\n"

    if is_health:
        prompt = (
            f"User's health data:\n{context}\n\n"
            f"User question: {user_question}\n\n"
            f"Instructions:\n"
            f"- Jump directly into answering the question. DO NOT start with 'Hey! How can I help you today?' or repetitive greetings.\n"
            f"- Answer concisely in 2-3 short paragraphs or clean bullet points.\n"
            f"- Reference their exact numbers if available in their data.\n"
            f"- Suggest natural lifestyle/diet tips if discussing an abnormal level."
        )
    else:
        prompt = (
            f"User said: \"{user_question}\"\n"
            f"Reply warmly and helpfully in 1-2 friendly sentences."
        )

    try:
        # stream=True makes OpenAI send chunks as they are generated
        stream = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.3,
            max_tokens=250,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta  # Send each word/piece as it arrives

        # Feature: If the user asked a health-related question, attach the medical disclaimer
        if is_health_question(user_question):
            yield HEALTH_DISCLAIMER

    except Exception as error:
        print(f"[HealthLens] AI streaming failed: {error}")
        yield "AI is temporarily unavailable."


def ai_enhance_test_metadata(test_results: list[dict]) -> list[dict]:
    """
    Asks AI to fill in missing units and reference ranges for extracted tests.
    For example, if OCR found 'Hemoglobin = 14.5' but no unit, AI will say 'g/dL'.
    """
    client = get_ai_client()
    if not client or not test_results:
        return test_results  # Nothing to do — skip

    # Build a simple list to send to the AI
    test_inputs = []
    for r in test_results:
        test_inputs.append({
            "test_name":      r.get("test_name", ""),
            "value":          r.get("value"),
            "current_unit":   r.get("unit") or "",
            "ref_low":        r.get("report_ref_low") or r.get("reference_low"),
            "ref_high":       r.get("report_ref_high") or r.get("reference_high"),
        })

    prompt = (
        "You are a medical lab parser.\n"
        "For each test below, fill in the correct standard medical unit "
        "and standard adult reference range if they are missing.\n\n"
        "Input tests:\n" + json.dumps(test_inputs, indent=2) + "\n\n"
        "Respond ONLY with a JSON array. Each item must have: "
        "test_name, unit, reference_low, reference_high.\n"
        "No explanation. No markdown. Just the raw JSON array."
    )

    try:
        response = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": "You output strict JSON only. No prose."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
            max_tokens=300,
        )

        # Strip markdown code fences if the AI added them
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        ai_list = json.loads(raw)

        # Build a lookup table: lowercase test name → AI's metadata
        ai_lookup = {
            str(item.get("test_name", "")).lower(): item
            for item in ai_list
            if isinstance(item, dict)
        }

        # Apply AI's suggestions to each test result
        for r in test_results:
            name_key = str(r.get("test_name", "")).lower()

            # Try exact match first, then partial match
            ai_meta = ai_lookup.get(name_key)
            if not ai_meta:
                for key, meta in ai_lookup.items():
                    if key in name_key or name_key in key:
                        ai_meta = meta
                        break

            if not ai_meta:
                continue  # AI didn't return data for this test

            # Fill unit if currently missing
            if ai_meta.get("unit") and not r.get("unit"):
                r["unit"] = str(ai_meta["unit"])

            # Fill reference low if currently missing
            if r.get("report_ref_low") is None and ai_meta.get("reference_low") is not None:
                r["report_ref_low"] = float(ai_meta["reference_low"])
                r["reference_low"]  = float(ai_meta["reference_low"])

            # Fill reference high if currently missing
            if r.get("report_ref_high") is None and ai_meta.get("reference_high") is not None:
                r["report_ref_high"] = float(ai_meta["reference_high"])
                r["reference_high"]  = float(ai_meta["reference_high"])

    except Exception as error:
        print(f"[HealthLens] AI metadata fill failed: {error}")

    return test_results
