import os
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LeadService")

LEADS_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "leads.json"
)

def save_lead(lead_data: dict) -> bool:
    """
    Saves lead details to simulated MongoDB, Google Sheets, CRM and 
    persists them in a local JSON database.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    record = {
        "timestamp": timestamp,
        **lead_data
    }

    # 1. Simulate MongoDB Insert
    logger.info("=== SIMULATING MONGODB INSERT ===")
    logger.info(f"MongoDB Collection: leads | Document: {json.dumps(record, indent=2)}")

    # 2. Simulate Google Sheets Append
    logger.info("=== SIMULATING GOOGLE SHEETS APPEND ===")
    logger.info(f"Google Sheet: Lead Database | Row Added: {[record.get('name'), record.get('mobile'), record.get('email'), record.get('intent')]}")

    # 3. Simulate CRM Lead Capture
    logger.info("=== SIMULATING CRM LEAD CAPTURE ===")
    logger.info(f"CRM URL: https://api.crm.asb.in/leads | Payload: {json.dumps(record)}")

    # 4. Save to Local JSON File (Database Fallback)
    try:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(LEADS_FILE_PATH), exist_ok=True)

        leads = []
        if os.path.exists(LEADS_FILE_PATH):
            with open(LEADS_FILE_PATH, "r", encoding="utf-8") as f:
                try:
                    leads = json.load(f)
                    if not isinstance(leads, list):
                        leads = []
                except json.JSONDecodeError:
                    leads = []

        leads.append(record)

        with open(LEADS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=4, ensure_ascii=False)

        logger.info(f"Lead successfully saved locally to {LEADS_FILE_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to save lead locally: {str(e)}")
        return False
