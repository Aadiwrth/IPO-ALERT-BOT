import httpx
from config import ONGOING_URL, logger


def fetch_ipo_data():
    """Fetch IPO data from API"""
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(ONGOING_URL)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Successfully fetched IPO data - {len(data.get('response', []))} IPOs found")
            return data.get("response", [])
    except httpx.TimeoutException:
        logger.error("Timeout while fetching IPO data")
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while fetching IPO data: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while fetching IPO data: {e}")
        return []


def test_api_connection():
    """Test API connectivity"""
    try:
        ipo_data = fetch_ipo_data()
        if ipo_data:
            logger.info(f"✓ API connection successful - {len(ipo_data)} IPOs found")
            return True
        else:
            logger.warning("✗ API connection failed or no data")
            return False
    except Exception as e:
        logger.error(f"✗ API test failed: {e}")
        return False