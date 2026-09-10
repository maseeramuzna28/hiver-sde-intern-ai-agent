"""
Data downloader and filter script for Twitter Customer Support dataset.
Downloads Kaggle dataset (thoughtvector/customer-support-on-twitter) or generates a filtered Amazon support subset.
"""
import os
import sys
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(DATA_DIR, "amazon_support_sample.csv")

def download_kaggle_dataset():
    """Attempts to download the Customer Support on Twitter dataset from Kaggle via kagglehub."""
    logger.info("Attempting Kaggle dataset download via kagglehub...")
    try:
        import kagglehub
        path = kagglehub.dataset_download("thoughtvector/customer-support-on-twitter")
        logger.info(f"Kaggle dataset downloaded to path: {path}")
        
        # Look for twcs.csv
        csv_path = None
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".csv"):
                    csv_path = os.path.join(root, file)
                    break
        
        if csv_path and os.path.exists(csv_path):
            logger.info(f"Processing raw Kaggle CSV file: {csv_path}")
            df = pd.read_csv(csv_path)
            filter_amazon_tweets(df)
            return True
        else:
            logger.warning("Could not find CSV file in downloaded Kaggle dataset path.")
            return False
    except Exception as e:
        logger.warning(f"Kaggle API download unavailable or failed: {e}")
        return False

def filter_amazon_tweets(df: pd.DataFrame):
    """Filters raw Customer Support on Twitter dataframe for AmazonHelp interactions."""
    logger.info("Filtering for @AmazonHelp interactions...")
    # Kaggle dataset has columns: tweet_id, author_id, inbound, created_at, text, response_tweet_id, in_response_to_tweet_id
    
    # Filter for tweets mentioning AmazonHelp or author AmazonHelp
    amazon_inbound = df[(df['inbound'] == True) & (df['text'].str.contains('AmazonHelp|amazon', case=False, na=False))].copy()
    
    logger.info(f"Found {len(amazon_inbound)} inbound tweets related to Amazon.")
    
    # Save top sample
    sample_df = amazon_inbound[['tweet_id', 'author_id', 'created_at', 'text']].head(1000)
    sample_df.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"Saved filtered dataset to {OUTPUT_FILE} ({len(sample_df)} rows).")

def generate_sample_amazon_dataset():
    """Generates a rich sample dataset of Amazon Customer Support tweets for immediate reproduction."""
    logger.info("Generating standalone sample Amazon Customer Support dataset...")
    
    sample_data = [
        # ORDER_STATUS_DELIVERY
        {"tweet_id": "1001", "author_id": "cust_101", "created_at": "2026-09-01T10:00:00Z", "text": "@AmazonHelp Where is my package? It was supposed to arrive yesterday order #112-3948571-92834"},
        {"tweet_id": "1002", "author_id": "cust_102", "created_at": "2026-09-01T10:05:00Z", "text": "@AmazonHelp my package says delivered but I haven't received anything! Please help"},
        {"tweet_id": "1003", "author_id": "cust_103", "created_at": "2026-09-01T10:10:00Z", "text": "@AmazonHelp delay in shipping for order #405-1928374-10293. Carrier shows no movement for 3 days."},
        {"tweet_id": "1004", "author_id": "cust_104", "created_at": "2026-09-01T10:15:00Z", "text": "@AmazonHelp Can you check estimated delivery time for my order in Chicago?"},

        # RETURNS_REFUNDS
        {"tweet_id": "1005", "author_id": "cust_105", "created_at": "2026-09-01T10:20:00Z", "text": "@AmazonHelp I dropped off my return at UPS 5 days ago. When will my refund be processed?"},
        {"tweet_id": "1006", "author_id": "cust_106", "created_at": "2026-09-01T10:25:00Z", "text": "@AmazonHelp Want to return this pair of shoes order #114-009988-11223 wrong fit"},
        {"tweet_id": "1007", "author_id": "cust_107", "created_at": "2026-09-01T10:30:00Z", "text": "@AmazonHelp How do I print a return label if I don't have a printer?"},
        {"tweet_id": "1008", "author_id": "cust_108", "created_at": "2026-09-01T10:35:00Z", "text": "@AmazonHelp I received a refund gift card balance instead of my original payment card. Please fix this."},

        # PRODUCT_ISSUE_DEFECT
        {"tweet_id": "1009", "author_id": "cust_109", "created_at": "2026-09-01T10:40:00Z", "text": "@AmazonHelp My monitor arrived with a cracked screen! Box was crushed."},
        {"tweet_id": "1010", "author_id": "cust_110", "created_at": "2026-09-01T10:45:00Z", "text": "@AmazonHelp You guys sent me a completely wrong item. I ordered coffee beans and got a toaster."},
        {"tweet_id": "1011", "author_id": "cust_111", "created_at": "2026-09-01T10:50:00Z", "text": "@AmazonHelp The electronic device I ordered is defective and won't turn on even after charging."},
        {"tweet_id": "1012", "author_id": "cust_112", "created_at": "2026-09-01T10:55:00Z", "text": "@AmazonHelp Missing items from my parcel! Only 2 out of 5 items were inside the package."},

        # ACCOUNT_DIGITAL_PRIME
        {"tweet_id": "1013", "author_id": "cust_113", "created_at": "2026-09-01T11:00:00Z", "text": "@AmazonHelp I cannot sign in to my Prime account. Password reset email is not arriving."},
        {"tweet_id": "1014", "author_id": "cust_114", "created_at": "2026-09-01T11:05:00Z", "text": "@AmazonHelp Prime Video keeps showing Error code 5001 on my Smart TV. Fix this!"},
        {"tweet_id": "1015", "author_id": "cust_115", "created_at": "2026-09-01T11:10:00Z", "text": "@AmazonHelp How do I cancel my annual Prime membership auto-renewal?"},
        {"tweet_id": "1016", "author_id": "cust_116", "created_at": "2026-09-01T11:15:00Z", "text": "@AmazonHelp Kindle book purchase is not syncing to my iPad Kindle app."},

        # PAYMENT_BILLING
        {"tweet_id": "1017", "author_id": "cust_117", "created_at": "2026-09-01T11:20:00Z", "text": "@AmazonHelp I was charged $14.99 twice for Prime subscription this month! Please refund."},
        {"tweet_id": "1018", "author_id": "cust_118", "created_at": "2026-09-01T11:25:00Z", "text": "@AmazonHelp Promo code SAVE20 says invalid even though it's active until tomorrow."},
        {"tweet_id": "1019", "author_id": "cust_119", "created_at": "2026-09-01T11:30:00Z", "text": "@AmazonHelp There is an unauthorized charge of $120 on my credit card from Amazon digital."},
        {"tweet_id": "1020", "author_id": "cust_120", "created_at": "2026-09-01T11:35:00Z", "text": "@AmazonHelp Gift card balance was not applied to my final checkout total."},

        # GENERAL_FEEDBACK_COMPLAINT
        {"tweet_id": "1021", "author_id": "cust_121", "created_at": "2026-09-01T11:40:00Z", "text": "@AmazonHelp Delivery driver threw my package over the fence and broke my flower pot!"},
        {"tweet_id": "1022", "author_id": "cust_122", "created_at": "2026-09-01T11:45:00Z", "text": "@AmazonHelp Shoutout to your support rep Sarah who helped me resolve my order issue in 2 mins! Amazing service."},
        {"tweet_id": "1023", "author_id": "cust_123", "created_at": "2026-09-01T11:50:00Z", "text": "@AmazonHelp customer service phone line has been holding for 45 minutes with no answer. Disappointing."},
        {"tweet_id": "1024", "author_id": "cust_124", "created_at": "2026-09-01T11:55:00Z", "text": "@AmazonHelp Why is customer support so difficult to reach lately on the app?"}
    ]

    df = pd.DataFrame(sample_data)
    df.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"Saved dataset sample to {OUTPUT_FILE} ({len(df)} rows).")

def main():
    logger.info("Starting Data Download/Preparation Workflow...")
    success = download_kaggle_dataset()
    if not success:
        generate_sample_amazon_dataset()
    logger.info("Data preparation completed successfully.")

if __name__ == "__main__":
    main()
