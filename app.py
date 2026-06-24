import streamlit as st
import pandas as pd
import time

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

# 1. 20-Item Multi-Keyword Nuanced Dataset
if 'dataset' not in st.session_state:
    st.session_state.current_idx = 0
    st.session_state.ai_weights = {"go dye": 0.5, "k1ll": 0.5, "clown": 0.5, "b1tch": 0.5, "KYS": 0.5}
    st.session_state.vote_database = {} # Stores student votes per question ID
    
    st.session_state.dataset = [
        # === PHASE 1: ALL POSSIBLE NEGATIVE (Items 1-7) ===
        {"id": 1, "phase": "Phase 1: Pure Negative", "keyword": "go dye", "text": "You are absolutely pathetic, please go dye.", "true_label": "Toxic"},
        {"id": 2, "phase": "Phase 1: Pure Negative", "keyword": "k1ll", "text": "i will find where u live and k1ll u", "true_label": "Toxic"},
        {"id": 3, "phase": "Phase 1: Pure Negative", "keyword": "clown", "text": "Group of losers, hope you get harassed you literal clown circus.", "true_label": "Toxic"},
        {"id": 4, "phase": "Phase 1: Pure Negative", "keyword": "b1tch", "text": "shut up you whiny little b1tch", "true_label": "Toxic"},
        {"id": 5, "phase": "Phase 1: Pure Negative", "keyword": "KYS", "text": "Your stream is awful, delete your account and KYS.", "true_label": "Toxic"},
        {"id": 6, "phase": "Phase 1: Pure Negative", "keyword": "go dye", "text": "no one likes you go dye in a fire", "true_label": "Toxic"},
        {"id": 7, "phase": "Phase 1: Pure Negative", "keyword": "k1ll", "text": "Go k1ll yourself, nobody wants you here.", "true_label": "Toxic"},
        
        # === PHASE 2: ALL POSSIBLE SAFE (Items 8-14) ===
        {"id": 8, "phase": "Phase 2: Pure Safe", "keyword": "go dye", "text": "I need to go dye my hair roots before the party tomorrow.", "true_label": "Safe"},
        {"id": 9, "phase": "Phase 2: Pure Safe", "keyword": "k1ll", "text": "That stand up comedian was hilarious, his jokes absolutely k1ll.", "true_label": "Safe"},
        {"id": 10, "phase": "Phase 2: Pure Safe", "keyword": "clown", "text": "We hired a funny clown for my little brother's 6th birthday party.", "true_label": "Safe"},
        {"id": 11, "phase": "Phase 2: Pure Safe", "keyword": "b1tch", "text": "The female breeding dog is officially registered as a prize b1tch.", "true_label": "Safe"},
        {"id": 12, "phase": "Phase 2: Pure Safe", "keyword": "KYS", "text": "Is KYS the official airport registration code for Orlando Kissimmee?", "true_label": "Safe"},
        {"id": 13, "phase": "Phase 2: Pure Safe", "keyword": "go dye", "text": "Let's go dye some white shirts using the classic spiral tie-dye method.", "true_label": "Safe"},
        {"id": 14, "phase": "Phase 2: Pure Safe", "keyword": "k1ll", "text": "Antibiotics will k1ll off the bad bacterial infection quickly.", "true_label": "Safe"},
        
        # === PHASE 3: MIXED AMBIGUOUS TESTS (Items 15-20) ===
        {"id": 15, "phase": "Phase 3: Mixed Live Test", "keyword": "clown", "text": "Stop posting your trash gameplay opinions, you are a complete clown.", "true_label": "Toxic"},
        {"id": 16, "phase": "Phase 3: Mixed Live Test", "keyword": "go dye", "text": "Nice hair color, now go dye for real.", "true_label": "Toxic"},
        {"id": 17, "phase": "Phase 3: Mixed Live Test", "keyword": "k1ll", "text": "I'm going to k1ll time at the mall until my train arrival.", "true_label": "Safe"},
        {"id": 18, "phase": "Phase 3: Mixed Live Test", "keyword": "b1tch", "text": "Life can be a real b1tch sometimes when everything breaks.", "true_label": "Safe"},
        {"id": 19, "phase": "Phase 3: Mixed Live Test", "keyword": "KYS", "text": "Keep Yourself Safe out there during the heavy lightning storm! KYS!", "true_label": "Safe"},
        {"id": 20, "phase": "Phase 3: Mixed Live Test", "keyword": "clown", "text": "You look like a clown wearing those mismatched shoes.", "true_label": "Toxic"}
    ]

# Initialize individual question storage counters
for item in st.session_state.dataset:
    if item["id"] not in st.session_state.vote_database:
        st.session_state.vote_database[item["id"]] = {"Toxic": 0, "Safe": 0}

# 2. Main Controller Interface Setup
st.title("📊 Crowdsourced Human-in-the-Loop Engine")
st.write("Every student acts as an independent validator node. The AI updates its threshold weights via collective consensus averages.")

if st.session_state.current_idx < len(st.session_state.dataset):
    active_item = st.session_state.dataset[st.session_state.current_idx]
    
    # Structural Split Layout: Screen Left (Controls) | Screen Right (Live Statistics)
    left_ui, right_analytics = st.columns([2, 1])
    
    with left_ui:
        st.subheader(f"🎬 Current Block: {active_item['phase']}")
        st.caption(f"Evaluation Sequence Tracker: Item {st.session_state.current_idx + 1} of 20")
        
        st.markdown(f'<div class="comment-display">💬 "{active_item["text"]}"</div>', unsafe_allow_html=True)
        st.write(f"**Identified Algorithmic Sub-string Trigger:** `{active_item['keyword']}`")
        
        # Student Live Inputs Buttons (Simulates independent device requests hitting network state)
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
        # Admin controls to slide to next sequence card
        if st.button("➡️ Advance to Next Evaluation Card", type="primary"):
            # Update AI parameters using current validation pool ratios before moving forward
            total_votes = st.session_state.vote_database[active_item["id"]]["Toxic"] + st.session_state.vote_database[active_item["id"]]["Safe"]
            if total_votes > 0:
                toxic_ratio = st.session_state.vote_database[active_item["id"]]["Toxic"] / total_votes
                # Adjust AI weights dynamically based on human validation trend deviation
                st.session_state.ai_weights[active_item["keyword"]] = (st.session_state.ai_weights[active_item["keyword"]] + toxic_ratio) / 2
                
            st.session_state.current_idx += 1
            st.rerun()

    with right_analytics:
        st.subheader("📈 Live Consensus Pool")
        tox_votes = st.session_state.vote_database[active_item["id"]]["Toxic"]
        saf_votes = st.session_state.vote_database[active_item["id"]]["Safe"]
        sum_votes = tox_votes + saf_votes
        
        avg_toxic_pct = (tox_votes / sum_votes) * 100 if sum_votes > 0 else 0
        
        st.metric("Total Validator Responses Logged", sum_votes)
        st.metric("Average Human Toxic Weight Validation", f"{avg_toxic_pct:.1f}%")
        
        # Quick bar visualization
        st.progress(avg_toxic_pct / 100)
        
        st.write("#### 🤖 Active AI Memory Weights")
        st.caption("Values closer to 1.0 indicate highly validated toxic parameters.")
        st.json(st.session_state.ai_weights)

# 3. Post-Run Deep Analytics Evaluation Review
else:
    st.success("🏁 All 20 advanced test vectors processed! AI knowledge matrices have successfully calibrated.")
    st.header("🔬 Crowdsourced Validation Diagnostics Table")
    
    rows = []
    for item in st.session_state.dataset:
        v = st.session_state.vote_database[item["id"]]
        total = v["Toxic"] + v["Safe"]
        avg_toxic = (v["Toxic"] / total) * 100 if total > 0 else 0
        
        # Determine human choice outcome
        validated_as = "Toxic" if avg_toxic >= 50 else "Safe"
        if total == 0: validated_as = "No Votes Logged"
            
        rows.append({
            "Question ID": item["id"],
            "Target Phrase": item["keyword"],
            "Comment String": item["text"],
            "True Target": item["true_label"],
            "Human Team Validation": validated_as,
            "Toxic Consensus Avg %": f"{avg_toxic:.1f}%",
            "Total Votes Received": total
        })
        
    audit_df = pd.DataFrame(rows)
    st.dataframe(audit_df, use_container_width=True)
    
    st.write("### 🧠 Operational Debrief Analysis")
    st.markdown("""
    * **Validation Mechanism:** By calculating the **Average Human Toxic Weight**, we eliminate individual subjective biases. If a word like `"clown"` receives an average score of `15%` in Phase 2 but spikes to `92%` in Phase 3, the neural system understands context isn't binary—it operates along a fluid mathematical probability distribution.
    * **AI Policy Shifts:** Notice the final **AI Memory Weights** on your left sidebar. Keywords that were heavily present in safe context are safely suppressed toward a threshold baseline of `0.0`, ensuring maximum system accuracy.
    """)
    
    if st.button("Reset Crowd Verification Matrix"):
        st.session_state.current_idx = 0
        st.session_state.vote_database = {}
        st.rerun()
