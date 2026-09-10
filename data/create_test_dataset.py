"""
Script to construct 150 hand-labeled test dataset for AI Support Agent benchmark.
"""
import json
import os

test_cases = []

# 1. ORDER_STATUS_DELIVERY (25 cases)
delivery_cases = [
    ("Where is my order #111-2223334-4455667? It said out for delivery 2 days ago.", False),
    ("My package tracking hasn't updated since Monday. Carrier is UPS. Please help!", False),
    ("Delivered status shown on app but package is not on my porch or mailbox.", False),
    ("Can I change the shipping address for order #402-9988776 before it ships?", False),
    ("Driver marked package as delivered to resident but nobody was home. Where is it?", False),
    ("Estimated delivery was 10 AM, now it's 8 PM. Is my package coming today?", False),
    ("Order #102-3948571 was supposed to be 1-day Prime delivery. Why is it 4 days late?", False),
    ("Tracking says 'Incorrect Address'. How do I update my delivery instructions?", False),
    ("Is there any way to expedite shipping for an item I ordered an hour ago?", False),
    ("Package was left in the heavy rain and shipping box is soaked. Tracking #992837.", False),
    ("Can you tell me which carrier is delivering order #701-2837491?", False),
    ("Item shipped via USPS but tracking link is not working on the site.", False),
    ("I paid extra for Sunday delivery and it did not arrive. Order #113-445566-77", False),
    ("Driver gave package to neighbor without permission. Can you track who accepted it?", False),
    ("Order status says 'Dispatched' for 5 days. Has it left the warehouse?", False),
    ("My delivery driver left the package on the sidewalk near a busy street.", False),
    ("Where is my package? No update on app for 48 hours.", False),
    ("Why was my order split into 3 separate deliveries?", False),
    ("Can I request delivery to a Locker instead of my home for order #554-112233?", False),
    ("My package is delayed due to weather. How long will it take now?", False),
    ("Order #998-123456-789 says delivered to garage but garage was locked.", False),
    ("Tracking number 1Z9999999999999999 is invalid on carrier website.", False),
    ("I need my medical supplies order #112-998877 delivered urgently today!", False),
    ("Shipment status says returned to sender due to damaged outer packaging.", False),
    ("Will my order arrive before 5 PM today in New York?", False)
]

for idx, (text, esc) in enumerate(delivery_cases, 1):
    test_cases.append({
        "id": idx,
        "text": f"@AmazonHelp {text}",
        "ground_truth_intent": "ORDER_STATUS_DELIVERY",
        "ground_truth_escalation": esc
    })

# 2. RETURNS_REFUNDS (25 cases)
returns_cases = [
    ("How do I return a dress that doesn't fit? Order #112-445566", False),
    ("I returned my item 7 days ago via Kohl's dropoff. When will my refund hit my account?", False),
    ("Can I get a replacement instead of a refund for order #403-112233?", False),
    ("Return policy says 30 days. It has been 32 days, can I still get store credit?", False),
    ("My return QR code expired. How do I generate a new return label?", False),
    ("I dropped off 2 items in 1 return box. Only 1 item shows refunded.", False),
    ("When does the 14-day refund processing window start after UPS pickup?", False),
    ("Is return shipping free for Prime members on clothing items?", False),
    ("How do I exchange a medium shirt for a large size?", False),
    ("I was refunded to gift card balance but I wanted original credit card refund.", False),
    ("Can I return a opened electronic item if it's missing original plastic wrap?", False),
    ("Return status shows processed but money is not in my bank account yet.", False),
    ("I returned a defective blender. Will I get a full refund including shipping fees?", False),
    ("Where do I find my return mailing authorization slip?", False),
    ("UPS driver never showed up to pick up my return parcel.", False),
    ("I want to cancel a return request I submitted by mistake yesterday.", False),
    ("Is it possible to return an item bought from a third-party seller?", False),
    ("Refund amount is $5 short. Why was a restocking fee deducted?", False),
    ("Can I return an item at Whole Foods without a box or label?", False),
    ("I returned my product 2 weeks ago and still no refund. Order #105-887766.", False),
    ("How long does it take for a credit card refund to reflect on my statement?", False),
    ("Do I need to return all accessories that came in the original box?", False),
    ("I received a partial refund for my returned book. Why wasn't it full?", False),
    ("Can I get cash refund at Amazon Fresh store for an online return?", False),
    ("My account shows refund issued on Sept 2nd but my bank sees nothing.", False)
]

for idx, (text, esc) in enumerate(returns_cases, 26):
    test_cases.append({
        "id": idx,
        "text": f"@AmazonHelp {text}",
        "ground_truth_intent": "RETURNS_REFUNDS",
        "ground_truth_escalation": esc
    })

# 3. PRODUCT_ISSUE_DEFECT (25 cases)
defect_cases = [
    ("My laptop screen arrived completely shattered! Box was damaged. Order #114-998877", False),
    ("The headphones I received only play audio in the left ear. Defective out of box.", False),
    ("You sent me a size 8 shoe when I ordered size 10! Order #402-334455", False),
    ("Opened package and the bottle of detergent leaked all over the other items!", False),
    ("The coffee maker I bought stopped heating water after 2 days of use.", False),
    ("My parcel was missing 2 out of the 4 battery packs ordered.", False),
    ("The smartphone box was empty! Seal was broken and no phone inside!", True), # High risk / missing expensive
    ("Received a completely different item: ordered a keyboard, got a dog toy.", False),
    ("The ceramic mug arrived cracked into pieces. Unsafe to touch.", False),
    ("Item missing essential parts listed on the manual. Cannot assemble desk.", False),
    ("The battery charger melted while plugged in! Potential fire hazard!", True), # Safety hazard -> Escalation
    ("Expiration date on the food item delivered today was 3 months ago!", False),
    ("The power bank expanded and swollen! Looks dangerous to use.", True), # Safety hazard -> Escalation
    ("Sent refurbished item when I paid full price for brand new condition.", False),
    ("Hard drive makes clicking sound and fails to connect to PC.", False),
    ("Order #113-556677 arrived without the power cord included.", False),
    ("Product user manual is in a foreign language with no English instructions.", False),
    ("The zipper on the jacket broke on first try. Poor quality.", False),
    ("Garment has a terrible chemical odor even after washing.", False),
    ("Supposed to be a pack of 12 sodas, only received 6 cans in damaged carton.", False),
    ("Watch glass has deep scratches right out of the plastic seal.", False),
    ("The toy arrived with sharp exposed wire inside. Dangerous for kids!", True), # Safety hazard
    ("Smart light bulb won't connect to Alexa or Wi-Fi.", False),
    ("Package box crushed like someone stepped on it. Contents smashed.", False),
    ("Tool set came with missing screwdriver bits.", False)
]

for idx, (text, esc) in enumerate(defect_cases, 51):
    test_cases.append({
        "id": idx,
        "text": f"@AmazonHelp {text}",
        "ground_truth_intent": "PRODUCT_ISSUE_DEFECT",
        "ground_truth_escalation": esc
    })

# 4. ACCOUNT_DIGITAL_PRIME (25 cases)
account_cases = [
    ("Cannot log into my Amazon account. Password reset email is not coming through.", False),
    ("How do I cancel my Amazon Prime membership before auto-renewing?", False),
    ("Prime Video displays Error Code 5001 on my LG TV. How to fix?", False),
    ("My Kindle paperwhite is stuck on tree screen and won't restart.", False),
    ("I paid for Prime but my orders are still showing standard shipping fees.", False),
    ("My Amazon account was locked due to suspicious activity. Need access back!", True), # Account access/security
    ("Someone changed the email address on my Amazon account without my permission!", True), # Account takeover
    ("How do I transfer my Kindle library to a new Amazon account?", False),
    ("Prime Video subscription was charged but movies still ask for rental fee.", False),
    ("Two-factor authentication SMS codes are not reaching my mobile phone.", False),
    ("How do I remove a credit card from my saved Amazon payment methods?", False),
    ("Amazon Music app keeps crashing on iOS 18.", False),
    ("Can I share Prime benefits with my family members in Household?", False),
    ("My Amazon Luna controller disconnects during gameplay.", False),
    ("How do I update my phone number associated with my account?", False),
    ("Prime student verification failed even though I uploaded my university ID.", False),
    ("Audible credit did not show up after monthly billing.", False),
    ("How do I turn off 1-Click ordering on desktop browser?", False),
    ("My Fire TV Stick keeps rebooting in a boot loop.", False),
    ("Account compromised! Someone placed 5 orders on my account in 10 minutes!", True), # Fraud / security
    ("How do I download tax invoice for my Prime digital subscription?", False),
    ("Why is Prime Video content restricted in my current country travel?", False),
    ("Unable to unlink Twitch account from Prime Gaming.", False),
    ("My Amazon Photos cloud storage says full when I only used 2GB.", False),
    ("How to change default address in my account settings?", False)
]

for idx, (text, esc) in enumerate(account_cases, 76):
    test_cases.append({
        "id": idx,
        "text": f"@AmazonHelp {text}",
        "ground_truth_intent": "ACCOUNT_DIGITAL_PRIME",
        "ground_truth_escalation": esc
    })

# 5. PAYMENT_BILLING (25 cases)
billing_cases = [
    ("I was charged $14.99 twice on my bank statement for Prime this month!", True), # Billing default escalation
    ("There is a mysterious charge of $89.99 from Amazon Digital on my card.", True), # High risk / unauthorized
    ("My promo code SAVE15 failed at checkout saying code expired.", True),
    ("Why was my credit card declined when balance and info are correct?", True),
    ("I applied a $50 gift card but my credit card was still charged full amount.", True),
    ("Fraud alert: my credit card was charged for orders I never made!", True), # Fraud
    ("Will take legal action if double charge of $350 is not refunded immediately!", True), # Legal threat
    ("How do I get a formal VAT invoice for my business account purchase?", True),
    ("My payment went through but order status says 'Payment Pending'.", True),
    ("Gift card code purchased at supermarket shows already redeemed by another account.", True),
    ("Why did the price in my cart jump from $25 to $40 right before clicking place order?", True),
    ("Charged for item that was cancelled 3 days ago before shipping.", True),
    ("Bank statement shows charge from Amazon Pay that I didn't authorize.", True),
    ("Promo discount was not applied to my Subscribe & Save delivery.", True),
    ("My credit card was charged twice for order #112-990011.", True),
    ("How do I change payment method for an order already placed?", True),
    ("I have been billed monthly for a channel subscription I never signed up for.", True),
    ("Currency conversion fee was added to my checkout without disclosure.", True),
    ("Where can I see detailed payment receipt for my past purchases?", True),
    ("My balance shows -$12.50. Why is my gift card balance negative?", True),
    ("Payment authorization failed repeatedly with error code ERR_PAY_01.", True),
    ("I demand a full refund and compensation for unauthorized billing!", True), # Anger / dispute
    ("Why is Amazon holding $200 pre-authorization on my debit card for a week?", True),
    ("Gift card claimed success but balance is still 0. Order #401-112233.", True),
    ("Automatic reload charged my card $100 when threshold was reached.", True)
]

for idx, (text, esc) in enumerate(billing_cases, 101):
    test_cases.append({
        "id": idx,
        "text": f"@AmazonHelp {text}",
        "ground_truth_intent": "PAYMENT_BILLING",
        "ground_truth_escalation": esc
    })

# 6. GENERAL_FEEDBACK_COMPLAINT (25 cases)
feedback_cases = [
    ("Your delivery driver threw my box over the gate and broke my porch lights!", True), # Driver damage
    ("Big shoutout to support agent David for resolving my issue in seconds! Great job.", False),
    ("Customer service phone wait time is over 1 hour. Horrible customer service!", False),
    ("Why is search filter on your website so terrible lately showing unrelated items?", False),
    ("Driver opened my front screen door and put package inside without knocking.", False),
    ("I've been a loyal customer for 10 years and today's service was unacceptable.", False),
    ("App crashes every time I open customer service chat on Android.", False),
    ("Your driver was speeding down our quiet residential street dangerously!", True), # Safety risk
    ("Thank you Amazon team for fast Sunday delivery! Made my weekend.", False),
    ("Why do you use so much plastic packaging for tiny items? Environmental waste.", False),
    ("Customer rep ended the chat abruptly while I was typing my response!", False),
    ("Driver blocked my garage driveway with delivery van for 30 minutes.", False),
    ("Great packaging on fragile items! Everything arrived safe.", False),
    ("Search results are filled with sponsored ads instead of relevant products.", False),
    ("Representative was very rude on the phone call today.", False),
    ("I am filing a formal complaint regarding driver conduct today at my premises.", True),
    ("Loved the quick delivery time! 5 stars to Amazon logistics.", False),
    ("Website layout update is confusing and hard to navigate.", False),
    ("Delivery driver left package in front of my garage door where I almost ran over it.", False),
    ("Why does customer support keep transferring me to 5 different agents?", False),
    ("Compliments to the delivery driver who carried heavy boxes up 3 flights of stairs!", False),
    ("Your AI chatbot is useless and keeps looping the same questions.", False),
    ("Driver left package on porch of wrong address down the street.", False),
    ("Terrible experience with Amazon logistics in Seattle area recently.", False),
    ("I want to leave positive feedback for rep Ashley who assisted me.", False)
]

for idx, (text, esc) in enumerate(feedback_cases, 126):
    test_cases.append({
        "id": idx,
        "text": f"@AmazonHelp {text}",
        "ground_truth_intent": "GENERAL_FEEDBACK_COMPLAINT",
        "ground_truth_escalation": esc
    })

data_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(data_dir, "test_dataset_150.json")

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(test_cases, f, indent=2)

print(f"Generated 150 hand-labeled test cases successfully at {out_path}")
