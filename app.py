import streamlit as st
import time
import pandas as pd

# Make sure to run: pip install qrcode pillow
import qrcode
from io import BytesIO

# 1. Page Config
st.set_page_config(page_title="HITL Advanced Moderator", layout="wide")

# Custom CSS for UI animations
st.markdown("""
<style>
    .comment-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 5px solid #3498db;
        background-color: #f8f9fa;
        transition: all 0.4s ease-in-out;
    }
    .red-flagged {
        background-color: #fde8e8 !important;
        border-left: 5px solid #e74c3c !important;
        color: #c0392b !important;
        font-weight: bold;
    }
    .green-passed {
        background-color: #edf7ed !important;
        border-left: 5px solid #2ecc71 !important;
        color: #27ae60 !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. Sidebar with QR Code for Classroom Joins
with st.sidebar:
    st.header("📲 Student Access")
    # Dynamically generate QR code to match your current hosted URL or local network IP
    app_url = st.query_params.get("url", "http://localhost:8501")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(app_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="Scan to moderate alongside the instructor!")
    st.caption(f"Target URL: `{app_url}`")

st.title("🛡️ Advanced Human-in-the-Loop Simulation")
st.write("Goal: Train students to spot *adversarial text variants* while protecting harmless context.")

# 3. State Management Setup
if 'batch_idx' not in st.session_state:
    st.session_state.batch_idx = 0
    st.session_state.history = []  # Stores statistical outcomes
    
    # Complex Dataset with both bad and safe context variations
    st.session_state.dataset = [
        {
            "keyword": "go dye (Target Variant)",
            "comments": [
                {"text": "Bro, you are useless, just go dye.", "is_bad": True},
                {"text": "I think you should go dye your hair blonde.", "is_bad": False}, # SAFE!
                {"text": "Why don't you delete life and go dye?", "is_bad": True},
                {"text": "Go dye your shirt if it has stains.", "is_bad": False}, # SAFE!
                {"text": "Go dye in a ditch.", "is_bad": True}
            ]
        },
        {
            "keyword": "u r tr@sh (Target Variant)",
            "comments": [
                {"text": "Worst team member ever u r tr@sh.", "is_bad": True},
                {"text": "Remember to take out the bins because u r tr@sh person.", "is_bad": True},
                {"text": "The recyclables go over there, u r tr@sh collection day is Tuesday.", "is_bad": False}, # SAFE!
                {"text": "Uninstall the application u r tr@sh.", "is_bad": True},
                {"text": "u r tr@sh at cooking raw food.", "is_bad": True}
            ]
        }
    ]

# 4. Main Loop Logic
if st.session_state.batch_idx < len(st.session_state.dataset):
    current_batch = st.session_state.dataset[st.session_state.batch_idx]
    
    st.subheader(f"Current Target Filter: `{current_batch['keyword']}`")
    st.info("🤖 **AI Flagged Flag:** All items below contain the target string. Humans must evaluate the real context.")
    
    # Show active items
    placeholders = []
    for item in current_batch["comments"]:
        p = st.empty()
        p.markdown(f'<div class="comment-box">💬 {item["text"]}</div>', unsafe_allow_html=True)
        placeholders.append(p)
        
    st.write("---")
    
    # Decisions Interface
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚨 Purge Malicious Variant Only", use_container_width=True):
            st.write("⏳ AI running Context-Aware Red-Flag Cleanse...")
            
            bad_count = 0
            safe_count = 0
            
            for idx, item in enumerate(current_batch["comments"]):
                time.sleep(0.6)
                if item["is_bad"]:
                    # Turn Red
                    placeholders[idx].markdown(f'<div class="comment-box red-flagged">🚨 [REMOVED] {item["text"]}</div>', unsafe_allow_html=True)
                    time.sleep(0.6)
                    placeholders[idx].empty() # Vanish
                    bad_count += 1
                else:
                    # Turn Green and Stay
                    placeholders[idx].markdown(f'<div class="comment-box green-passed">✅ [SAFE CONTEXT PRESERVED] {item["text"]}</div>', unsafe_allow_html=True)
                    safe_count += 1
                    
            # Log results for statistics
            st.session_state.history.append({
                "keyword": current_batch["keyword"],
                "total_flagged_by_ai": len(current_batch["comments"]),
                "true_positive_toxic": bad_count,
                "false_positive_safe": safe_count
            })
            
            time.sleep(1.5)
            st.session_state.batch_idx += 1
            st.rerun()
            
    with col2:
        if st.button("⚪ Skip Phrase (All Safe Context)", use_container_width=True):
            st.session_state.history.append({
                "keyword": current_batch["keyword"],
                "total_flagged_by_ai": len(current_batch["comments"]),
                "true_positive_toxic": 0,
                "false_positive_safe": len(current_batch["comments"])
            })
            st.session_state.batch_idx += 1
            st.rerun()

# 5. Post-Simulation Statistical Breakdown Screen
else:
    st.success("🎉 **Simulation Complete! All Content Batches Processed.**")
    st.header("📊 Post-Moderation Analytics Dashboard")
    
    df = pd.DataFrame(st.session_state.history)
    
    # Calculations
    total_ai_flags = df["total_flagged_by_ai"].sum()
    total_true_toxic = df["true_positive_toxic"].sum()
    total_false_positives = df["false_positive_safe"].sum()
    ai_precision = (total_true_toxic / total_ai_flags) * 100 if total_ai_flags > 0 else 0
    
    # Key Performance Indicators
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total AI Scans Triggered", total_ai_flags)
    m2.metric("Confirmed Toxic Slang (TP)", total_true_toxic)
    m3.metric("False Flags Prevented (FP)", total_false_positives)
    m4.metric("AI Precision Accuracy Rate", f"{ai_precision:.1f}%")
    
    st.write("### Data Table Summary")
    st.dataframe(df, use_container_width=True)
    
    # Educational Explainer Breakdowns
    st.write("### 🧠 Classroom Debrief Notes")
    st.markdown(f"""
    * **Why did the system need humans?** The keyword rule caught everything blindly. Without human intervention, the platform would have wrongfully banned **{total_false_positives} users** who were just talking about regular things like *dying hair* or *trash schedules*.
    * **The Operational Cost:** Because the initial AI system had a precision rate of only **{ai_precision:.1f}%**, human review teams are mandatory to protect user retention and avoid censorship errors.
    """)
    
    if st.button("Restart Simulation Engine"):
        st.session_state.batch_idx = 0
        st.session_state.history = []
        st.rerun()
