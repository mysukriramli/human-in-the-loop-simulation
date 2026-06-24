import streamlit as st
import pandas as pd
import time
import qrcode
from io import BytesIO

st.set_page_config(page_title="Crowdsourced AI Validator", layout="wide")

# Custom Styles for Phase Blocks
st.markdown("""
<style>
    .comment-display {
        font-size: 24px !important;
        padding: 20px;
        background-color: #f1f2f6;
        border-radius: 10px;
        border-left: 8px solid #34495e;
        margin-bottom: 20px;
        font-weight: 500;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 1. 10-Item Multi-Keyword Dataset (3 Pure Negative, 3 Pure Safe, 4 Mixed)
if 'dataset' not in st.session_state:
    st.session_state.current_idx = 0
    st.session_state.ai_weights = {"go dye": 0.5, "k1ll": 0.5, "KYS": 0.5, "clown": 0.5, "tr@sh": 0.5}
    st.session_state.vote_database = {} 
    
    st.session_state.dataset = [
        # === PHASE 1: ALL POSSIBLE NEGATIVE (Items 1-3) ===
        {"id": 1, "phase": "Phase 1: Pure Negative", "keyword": "go dye", "text": "You are absolutely pathetic, please go dye.", "true_label": "Toxic"},
        {"id": 2, "phase": "Phase 1: Pure Negative", "keyword": "k1ll", "text": "i will find where u live and k1ll u", "true_label": "Toxic"},
        {"id": 3, "phase": "Phase 1: Pure Negative", "keyword": "KYS", "text": "Your stream is awful, delete your account and KYS.", "true_label": "Toxic"},
        
        # === PHASE 2: ALL POSSIBLE SAFE (Items 4-6) ===
        {"id": 4, "phase": "Phase 2: Pure Safe", "keyword": "go dye", "text": "I need to go dye my hair roots before the party tomorrow.", "true_label": "Safe"},
        {"id": 5, "phase": "Phase 2: Pure Safe", "keyword": "k1ll", "text": "That stand up comedian was hilarious, his jokes absolutely k1ll.", "true_label": "Safe"},
        {"id": 6, "phase": "Phase 2: Pure Safe", "keyword": "KYS", "text": "Is KYS the official airport registration code for Orlando Kissimmee?", "true_label": "Safe"},
        
        # === PHASE 3: MIXED AMBIGUOUS TESTS (Items 7-10) ===
        {"id": 7, "phase": "Phase 3: Mixed Live Test", "keyword": "clown", "text": "We hired a funny clown for my little brother's 6th birthday party.", "true_label": "Safe"},
        {"id": 8, "phase": "Phase 3: Mixed Live Test", "keyword": "clown", "text": "Stop posting your trash gameplay opinions, you are a complete clown.", "true_label": "Toxic"},
        {"id": 9, "phase": "Phase 3: Mixed Live Test", "keyword": "tr@sh", "text": "The recycling program helps reduce local tr@sh waste.", "true_label": "Safe"},
        {"id": 10, "phase": "Phase 3: Mixed Live Test", "keyword": "tr@sh", "text": "You are literal tr@sh throw yourself away.", "true_label": "Toxic"}
    ]

# Initialize individual question storage counters
for item in st.session_state.dataset:
    if item["id"] not in st.session_state.vote_database:
        st.session_state.vote_database[item["id"]] = {"Toxic": 0, "Safe": 0}

# 2. Sidebar with YOUR LIVE APP QR Code & Live AI Memory Weights
with st.sidebar:
    st.header("📲 Student Access")
    
    # YOUR DEPLOYED URL DETAILED HERE
    app_url = "https://human-in-the-loop-simulation-nwty9jxhv6vb7gjyc3dodw.streamlit.app/"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(app_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="Scan to cast your vote!")
    st.caption(f"Target URL: `{app_url}`")
    
    st.write("---")
    st.write("#### 🤖 Active AI Memory Weights")
    st.caption("Values adjust based on human validation averages.")
    st.json(st.session_state.ai_weights)
    
    st.write("---")
    progress = min(st.session_state.current_idx / 10, 1.0)
    st.progress(progress)
    st.caption(f"Progress: {st.session_state.current_idx} / 10 Evaluated")

# 3. Controller Interface
st.title("📊 Crowdsourced Human-in-the-Loop Engine")
st.write("Every student acts as an independent validator node. The AI updates its baseline weights via collective consensus averages.")

if st.session_state.current_idx < len(st.session_state.dataset):
    active_item = st.session_state.dataset[st.session_state.current_idx]
    
    # Layout Split: Left (Voting Controls) | Right (Live Progress Dashboard)
    left_ui, right_analytics = st.columns([2, 1])
    
    with left_ui:
        st.subheader(f"🎬 Current Block: {active_item['phase']}")
        st.caption(f"Evaluation Sequence: Item {st.session_state.current_idx + 1} of 10")
        
        st.markdown(f'<div class="comment-display">💬 "{active_item["text"]}"</div>', unsafe_allow_html=True)
        st.write(f"**Identified Trigger Word:** `{active_item['keyword']}`")
        
        st.write("### 🧑‍💻 Cast Your Validator Vote:")
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            if st.button("🚨 Vote: TOXIC CONTEXT", use_container_width=True):
                st.session_state.vote_database[active_item["id"]]["Toxic"] += 1
                st.rerun()
        with v_col2:
            if st.button("✅ Vote: SAFE CONTEXT", use_container_width=True):
                st.session_state.vote_database[active_item["id"]]["Safe"] += 1
                st.rerun()
                
        st.write("---")
        if st.button("➡️ Lock Votes & Advance", type="primary"):
            total_votes = st.session_state.vote_database[active_item["id"]]["Toxic"] + st.session_state.vote_database[active_item["id"]]["Safe"]
            if total_votes > 0:
                toxic_ratio = st.session_state.vote_database[active_item["id"]]["Toxic"] / total_votes
                st.session_state.ai_weights[active_item["keyword"]] = round((st.session_state.ai_weights[active_item["keyword"]] + toxic_ratio) / 2, 2)
                
            st.session_state.current_idx += 1
            st.rerun()

    with right_analytics:
        st.subheader("📈 Live Consensus Pool")
        tox_votes = st.session_state.vote_database[active_item["id"]]["Toxic"]
        saf_votes = st.session_state.vote_database[active_item["id"]]["Safe"]
        sum_votes = tox_votes + saf_votes
        
        avg_toxic_pct = (tox_votes / sum_votes) * 100 if sum_votes > 0 else 0
        
        st.metric("Total Votes Logged", sum_votes)
        st.metric("Average Human Toxic Weight", f"{avg_toxic_pct:.1f}%")
        st.progress(avg_toxic_pct / 100)

# 4. Post-Run Deep Analytics Evaluation Review
else:
    st.balloons()
    st.success("🏁 All 10 advanced test vectors processed! AI knowledge matrices have calibrated.")
    st.header("🔬 Crowdsourced Validation Diagnostics Table")
    
    rows = []
    for item in st.session_state.dataset:
        v = st.session_state.vote_database[item["id"]]
        total = v["Toxic"] + v["Safe"]
        avg_toxic = (v["Toxic"] / total) * 100 if total > 0 else 0
        
        validated_as = "Toxic" if avg_toxic >= 50 else "Safe"
        if total == 0: validated_as = "No Votes Logged"
            
        rows.append({
            "ID": item["id"],
            "Target Phrase": item["keyword"],
            "Comment String": item["text"],
            "True Target": item["true_label"],
            "Classroom Consensus Decision": validated_as,
            "Toxic Weight Avg": f"{avg_toxic:.1f}%",
            "Total Votes": total
        })
        
    audit_df = pd.DataFrame(rows)
    st.dataframe(audit_df, use_container_width=True)
    
    if st.button("Reset Crowd Verification Matrix"):
        st.session_state.current_idx = 0
        st.session_state.vote_database = {}
        st.session_state.ai_weights = {"go dye": 0.5, "k1ll": 0.5, "KYS": 0.5, "clown": 0.5, "tr@sh": 0.5}
        st.rerun()
