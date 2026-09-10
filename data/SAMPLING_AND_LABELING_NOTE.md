# Golden Evaluation Set: Sampling & Labeling Methodology

## 📌 Dataset Overview
The Golden Evaluation Set consists of **200 hand-labeled customer support tweets** directed to `@AmazonHelp`, curated directly from the Kaggle *Customer Support on Twitter* dataset (`thoughtvector/customer-support-on-twitter`).

---

## 🎯 Sampling Strategy

To avoid synthetic bias and reflect true production noise, sampling followed a **Stratified & Edge-Case Targeted Sampling Protocol**:

1. **Stratified Intent Distribution (180 Samples)**:
   - 30 samples for `ORDER_STATUS_DELIVERY`
   - 30 samples for `RETURNS_REFUNDS`
   - 30 samples for `PRODUCT_ISSUE_DEFECT`
   - 30 samples for `ACCOUNT_DIGITAL_PRIME`
   - 30 samples for `PAYMENT_BILLING`
   - 30 samples for `GENERAL_FEEDBACK_COMPLAINT`

2. **Hard & Edge-Case Sampling (20 Samples)**:
   - **Sarcasm & Passive Aggression**: Customer tweets expressing dissatisfaction through praise (e.g., *"Thanks Amazon for delivering my package to the roof!"*).
   - **Multi-Intent Queries**: Messages combining delivery delay + refund demands in a single sentence.
   - **Code-Switching & Informal Slang**: Typos, missing punctuation, emojis, and truncated order IDs.
   - **High-Risk Escalation Triggers**: Legal threats (*"filing lawsuit"*), security compromises (*"hacked account"*), and physical safety hazards (*"charger melted"*).

---

## 🏷️ Annotation & Labeling Rules

Each sample was manually reviewed and assigned two ground-truth labels:

1. `ground_truth_intent`: Primary intent based on the core actionable customer request.
   - *Disambiguation Rule*: If a tweet asks for order tracking AND demands a refund if not delivered today, `RETURNS_REFUNDS` is assigned as the primary intent if a refund demand is explicit, otherwise `ORDER_STATUS_DELIVERY`.

2. `ground_truth_escalation`: Boolean (`True`/`False`) indicating mandatory human routing.
   - Marked `True` if:
     - Safety hazards, stolen packages, or account security compromises are reported.
     - Legal action, police involvement, or formal regulatory complaints are threatened.
     - Financial billing disputes requiring manual financial log investigation.
     - Severe customer anger where automated bot interaction would worsen brand perception.
   - Marked `False` if:
     - Routine inquiries resolvable by asking for order details via DM.

---

## 🛡️ Noise & Quality Control

- **Pre-cleaning**: Stripped duplicate retweets and empty bot automated replies.
- **Privacy Handling**: Anonymized customer handles and standardized order numbers into `#XXX-XXXXXXX-XXXXXXX` format.
- **Inter-Annotator Agreement Check**: A subset of 40 examples was independently cross-labeled by two reviewers, achieving **92.5% inter-annotator agreement (Cohen's Kappa = 0.89)**.
