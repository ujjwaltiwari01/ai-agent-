# Radian Marketing Cold Email Automation
# This script automates the process of generating and sending personalized cold emails

import streamlit as st
import pandas as pd
import time
import openai
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import email_validator
import os
import requests
from bs4 import BeautifulSoup

# ----------------------------
# 🔑 YOUR API KEYS
# ----------------------------
# For local development, load .env (optional, not needed on Streamlit Cloud)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
import os

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
BREVO_API_KEY = get_secret("BREVO_API_KEY")
SENDER_NAME = get_secret("SENDER_NAME")
SENDER_EMAIL = get_secret("SENDER_EMAIL")

openai.api_key = OPENAI_API_KEY

config = sib_api_v3_sdk.Configuration()
config.api_key['api-key'] = BREVO_API_KEY
email_api = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(config))



# ----------------------------
# 📬 Email Validation
# ----------------------------
def is_valid_email_address(email):
    try:
        if isinstance(email, bytes):
            email = email.decode("utf-8")
        email_validator.validate_email(email)
        return True
    except email_validator.EmailNotValidError:
        return False

def is_role_based_email(email):
    role_keywords = ["info", "support", "admin", "contact", "sales", "team", "hello"]
    local_part = email.split("@")[0].lower()
    return any(local_part.startswith(role) for role in role_keywords)

# ----------------------------
# 🌐 Website Scraping for Personalization
# ----------------------------
def scrape_website_info(website_url):
    """Scrape website title and meta description for personalization."""
    try:
        resp = requests.get(website_url, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title else ""
        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()
        return title, meta_desc
    except Exception as e:
        return "", ""

# ----------------------------
# ✍️ Email Generation
# ----------------------------
def generate_email(company, website, keywords):
    # Now this works!
    title, meta_desc = scrape_website_info(website)
    website_info = f"Website Title: {title}\nMeta Description: {meta_desc}" if (title or meta_desc) else "No website info found."

    prompt = f"""
- Subject: Write a short, highly personalized, persuasive cold email for potential clients of Radian Marketing. The email should feel handcrafted, warm, and results-focused while subtly selling the expertise and unique benefits of working with Radian.

- Email Body Prompt:

- You are an elite prompt engineer and seasoned B2B email strategist with 20+ years of expertise in digital marketing, neuro-selling, and client acquisition psychology.

- Your task is to generate an ultra-personalized cold email on behalf of **Radian Marketing**, a top digital marketing agency in Delhi that serves B2B, B2C, and ecommerce clients.

- Use a professional, approachable tone that builds trust while quickly demonstrating how Radian Marketing can help overcome a *specific challenge* the recipient’s business is likely facing.

- Email Purpose: Establish a personal connection, identify a relatable marketing challenge, introduce Radian’s solution, and encourage a low-friction next step (soft CTA).

- What Radian Marketing Offers (Use the most relevant services based on the challenge):
- B2B & B2C Performance Marketing
- Social Media Management & Ads
- SEO (Local, National, Technical)
- Google Business Optimization
- CRO & Website Optimization
- Content Development & Strategy
- Influencer & Podcast Marketing
- Amazon, QuickCommerce & Ecommerce PPC
- WhatsApp & Community Marketing
- End-to-end Lead Generation Services
- Custom Digital Strategies for every business stage

- Follow this structure for the email body:

- 1. Personal Appreciation Hook:  
  - Start with a genuine compliment about the recipient’s website, mission, product, or recent campaign (if available).  
  - Keep it short and relevant, showing that this is not a mass email.

- 2. Identify a Realistic Marketing Challenge:  
  - Call out a common issue like: inconsistent lead flow, high CAC, low engagement, poor retention, underperforming SEO, or fragmented brand presence.  
  - Be specific and results-oriented. Avoid fluff or marketing jargon.

- 3. Amplify the Problem Slightly:  
  - Help the reader emotionally connect by revealing what this challenge costs them — in time, growth potential, revenue, or market trust.

- 4. Introduce Radian as the Smart, Trusted Solution:  
  - Briefly explain how Radian Marketing has helped similar businesses fix the same issue.  
  - Use phrases like “We’ve helped brands like [X]...” or “Our team has driven [Y] results…” if applicable.  
  - Mention their expertise across paid and organic marketing channels.

- 5. Soft CTA (Choose One):
  - “Would it make sense to explore what this might look like for your brand?”  
  - “Open to a short, no-strings call to show you what’s working right now?”  
  - “If this hits home, I’d love to share what we’ve done for similar brands.”

- 6. Sign-Off:  
  - Always end with:  
  - Looking forward,  
  - Bhaskar  

- Formatting & Rules:
- Subject line + email body only. Nothing else.  
- Use short paragraphs, max 1–2 sentences per block.  
- Max 7 total sentences.  
- Write clearly, humanly — avoid robotic or overly salesy tone.  
- Avoid emojis, ALL CAPS, or hype language.  
- Sound like a helpful peer, not a hungry seller.  
- The reader should feel like they were seen, heard, and helped — not pitched.

- Psychological & Persuasion Rules:
- Apply reciprocity: give value before asking.  
- Use social proof subtly (mention successful clients or stats if relevant).  
- Tap into FOMO, ease, and opportunity cost without pressuring.  
- Avoid overexplaining. Less is more.  
- Keep copy lean, warm, and strategic.

- Personalization Tips:
- If possible, mention the business type (e.g., D2C brand, SaaS startup, real estate firm).  
- Reference common growth goals like scaling outreach, boosting ROAS, improving local visibility, etc.  
- Adapt the tone if the audience is more creative, corporate, or ecommerce-focused.

- Final Goal:
- Make the recipient feel:
  - “This person gets my marketing struggle.”  
  - “The message feels personal, not automated.”  
  - “They’ve helped others like me — it’s worth replying.”  
  - “They aren’t overselling — I’m curious.”

Company: {company}
Website: {website}
Keywords: {keywords}
Website Info (scraped): {website_info}

Email Format:
Subject: <short subject>
Body:
- 1st: Personal appreciation hook
- 2nd: Identify a realistic marketing challenge
- 3rd: Amplify the problem
- 4th: Introduce Radian as the solution
- 5th: Soft CTA
- 6th: Sign-off ("Looking forward,\nBhaskar")
"""

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=700,
    )
    result = response.choices[0].message.content.strip()

    # Extract subject and body, ensuring subject is not duplicated in the body
    subject = ""
    body = ""
    lines = result.splitlines()
    found_subject = False
    found_body = False
    body_lines = []

    for line in lines:
        if not found_subject and line.lower().startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
            found_subject = True
        elif line.lower().startswith("body:"):
            found_body = True
            continue  # skip the "Body:" line itself
        elif found_body:
            body_lines.append(line)

    # If subject/body not found, fallback to defaults
    if not subject:
        subject = "AI Outreach That Converts"
    if not body_lines:
        # fallback: use everything except subject line
        body_lines = [l for l in lines if not l.lower().startswith("subject:") and not l.lower().startswith("body:")]

    body = "\n".join(body_lines).strip()

    # Remove subject line if it accidentally appears at the top of the body
    if body.lower().startswith(subject.lower()):
        body = body[len(subject):].lstrip(" :\n")

    if "stop" not in body.lower():
        body += "\n\nIf this isn't for you, just reply STOP."

    return subject, body

    if "stop" not in body.lower():
        body += "\n\nIf this isn't for you, just reply STOP."

    return subject, body

def generate_followup_email(company, website, keywords, prev_subject, prev_body):
    # Scrape website info for personalization
    title, meta_desc = scrape_website_info(website)
    website_info = f"Website Title: {title}\nMeta Description: {meta_desc}" if (title or meta_desc) else "No website info found."

    prompt = f"""
- Subject: Write a short, warm, and highly personalized follow-up cold email for a potential client of Radian Marketing. 
- The recipient received a previous email with the subject: "{prev_subject}".
- The follow-up should reference the previous outreach, show genuine interest, and offer new value or insight based on their website or business.
- Avoid sounding pushy or desperate. Keep it friendly, helpful, and results-focused.
- Use any relevant info from their website for personalization.

Company: {company}
Website: {website}
Keywords: {keywords}
Website Info (scraped): {website_info}
Previous Email Body: {prev_body}

Email Format:
Subject: <short subject>
Body:
- 1st: Reference previous email and express continued interest
- 2nd: Add a new insight, value, or question based on their business/website
- 3rd: Soft CTA (invite to connect, offer value, etc.)
- 4th: Sign-off ("Looking forward,\nBhaskar")
"""

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=700,
    )
    result = response.choices[0].message.content.strip()

    # Extract subject and body
    subject = ""
    body = ""
    lines = result.splitlines()
    found_subject = False
    found_body = False
    body_lines = []

    for line in lines:
        if not found_subject and line.lower().startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
            found_subject = True
        elif line.lower().startswith("body:"):
            found_body = True
            continue
        elif found_body:
            body_lines.append(line)

    if not subject:
        subject = "Quick Follow-up: Radian Marketing"
    if not body_lines:
        body_lines = [l for l in lines if not l.lower().startswith("subject:") and not l.lower().startswith("body:")]

    body = "\n".join(body_lines).strip()

    if body.lower().startswith(subject.lower()):
        body = body[len(subject):].lstrip(" :\n")

    if "stop" not in body.lower():
        body += "\n\nIf this isn't for you, just reply STOP."

    return subject, body

# ----------------------------
# 📤 Send Email
# ----------------------------
def send_email(to_email, to_name, subject, body):
    email_data = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email, "name": to_name}],
        sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
        subject=subject,
        html_content=body.replace("\n", "<br>")
    )
    return email_api.send_transac_email(email_data)

# ----------------------------
# 🖥️ Streamlit UI
# ----------------------------
st.set_page_config(page_title="Radian Marketing Outreach", layout="wide")
st.title("📬 Radian Marketing: Cold Email Automation")
st.markdown("Upload your lead CSV and let AI generate and send personalized cold emails.")

file = st.file_uploader("📁 Upload CSV (with columns: co_name, website, email, keywords, Name)", type="csv")

if file:
    df = pd.read_csv(file)
    st.success(f"Loaded {len(df)} leads from file.")

    start = st.number_input("Start index", 0, len(df)-1, value=0)
    end = st.number_input("End index", start+1, len(df), value=min(len(df), start+10))

    if st.button("🚀 Start Sending Emails"):
        skipped = []
        for i in range(start, end):
            row = df.iloc[i]
            company = str(row.get("co_name", "")).strip()
            website = str(row.get("website", "")).strip()
            email = str(row.get("email", "")).strip()
            keywords = str(row.get("keywords", "")).strip()
            name = str(row.get("Name", company)).strip()

            # Only skip if email is missing or invalid
            if not email or not is_valid_email_address(email):
                skipped.append((i, email, "Invalid email"))
                continue

            st.markdown(f"#### ✉️ Sending to {name} ({email})")

            try:
                subject, body = generate_email(company, website, keywords)
                st.code(f"Subject: {subject}", language="text")
                st.code(body, language="markdown")

                send_email(email, name, subject, body)
                st.success(f"✅ Sent to {email}")
            except ApiException as e:
                st.error(f"❌ Brevo API Error: {e}")
                skipped.append((i, email, "Brevo error"))
            except Exception as e:
                st.error(f"❌ AI/General Error: {e}")
                skipped.append((i, email, "General error"))

            time.sleep(1.5)  # avoid rate limits

        st.balloons()
        st.success("✅ All emails processed!")

        if skipped:
            st.warning(f"⚠️ Skipped {len(skipped)} emails.")
            st.dataframe(pd.DataFrame(skipped, columns=["Row", "Email", "Reason"]))
    if st.button("🔁 Send Follow-up Emails"):
        skipped = []
        for i in range(start, end):
            row = df.iloc[i]
            company = str(row.get("co_name", "")).strip()
            website = str(row.get("website", "")).strip()
            email = str(row.get("email", "")).strip()
            keywords = str(row.get("keywords", "")).strip()
            name = str(row.get("Name", company)).strip()

            if not email or not is_valid_email_address(email):
                skipped.append((i, email, "Invalid email"))
                continue

            st.markdown(f"#### 🔁 Sending follow-up to {name} ({email})")

            try:
                # Generate the original email to use as context for the follow-up
                prev_subject, prev_body = generate_email(company, website, keywords)
                subject, body = generate_followup_email(company, website, keywords, prev_subject, prev_body)
                st.code(f"Subject: {subject}", language="text")
                st.code(body, language="markdown")

                send_email(email, name, subject, body)
                st.success(f"✅ Follow-up sent to {email}")
            except ApiException as e:
                st.error(f"❌ Brevo API Error: {e}")
                skipped.append((i, email, "Brevo error"))
            except Exception as e:
                st.error(f"❌ AI/General Error: {e}")
                skipped.append((i, email, "General error"))

            time.sleep(1.5)  # avoid rate limits

        st.balloons()
        st.success("✅ All follow-up emails processed!")

        if skipped:
            st.warning(f"⚠️ Skipped {len(skipped)} emails.")
            st.dataframe(pd.DataFrame(skipped, columns=["Row", "Email", "Reason"]))
else:
    st.info("Please upload a CSV to begin.")