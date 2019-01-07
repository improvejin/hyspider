
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.getLogger('scrapy.core.scraper').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
logging.getLogger('fontTools.ttLib.ttFont').setLevel(logging.INFO)

