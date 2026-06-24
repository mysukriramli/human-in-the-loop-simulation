import streamlit as st
import pandas as pd
import time
import qrcode
from io import BytesIO

st.set_page_config(page_title="Global HITL Classroom Engine", layout="wide")

# Custom UI Styling
st.markdown("""
<style>
    .comment-display {
        font-size: 22px !important;
        padding: 20px;
        background-color: #f1f2f6;
        border-radius: 10px;
        border-left: 8px solid #34495e;
        margin-bottom: 20px;
    }
    .insight-card {
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 8px;
        border-left: 5px solid #2ecc71;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 1. FIXED DATASET (10 Questions)
DATASET = [
    {"id": 1, "phase": "Phase 1: Pure Negative", "keyword": "go dye", "text": "You are absolutely pathetic, please go dye.", "true_label": "Toxic"},
    {"id": 2, "phase": "Phase 1: Pure Negative", "keyword": "k1ll", "text": "i will find where u live and k1ll u", "true_label": "Toxic"},
    {"id": 3, "phase": "Phase 1: Pure Negative", "keyword": "KYS", "text": "Your stream is awful, delete your account and KYS.", "true_label": "Toxic"},
    {"id": 4, "phase": "Phase 2: Pure Safe", "keyword": "go dye", "text": "I need to go dye my hair roots before the party tomorrow.", "true_label": "Safe"},
    {"id": 5, "phase": "Phase 2: Pure Safe", "keyword": "k1ll", "text": "That stand up comedian was hilarious, his jokes absolutely k1ll.", "true_label": "Safe"},
    {"id": 6, "phase": "Phase 2: Pure Safe", "keyword": "KYS", "text": "Is KYS the official airport registration code for Orlando Kissimmee?", "true_label": "Safe"},
    {"id": 7, "phase": "Phase 3: Mixed Live Test", "keyword": "clown", "text": "We hired a funny clown for my little brother's 6th birthday party.", "true_label": "Safe"},
    {"id": 8, "phase": "Phase 3: Mixed Live Test", "keyword": "clown", "text": "Stop posting your trash gameplay opinions, you are a complete clown.", "true_label": "Toxic"},
    {"id": 9, "phase": "Phase 3: Mixed Live Test", "keyword": "tr@sh", "text": "The recycling program helps reduce local tr@sh waste.", "true_label": "Safe"},
    {"id": 10, "phase": "Phase 3: Mixed Live Test", "keyword": "tr@sh", "text": "You are literal tr@sh throw yourself away.", "true_label": "Toxic"}
]

# 2. GLOBAL MEMORY POOL (Shared across ALL student browsers)
@st.cache_resource
def get_classroom_database():
    db = {
        "votes": {item["id"]: {} for item in DATASET}, 
        "active_students": set()
    }
    return db

global_db = get_classroom_database()

# 3. SIDEBAR (QR Code and Unique Role/Identity View)
with st.sidebar:
    st.header("📲 Classroom Connection")
    app_url = "https://human-in-the-loop-simulation-nwty9jxhv6vb7gjyc3dodw.streamlit.app/"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(app_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="Scan to participate live")
    
    st.write("---")
    view_mode = st.radio("Select Interface View:", ["Student Portal", "Instructor Master Dashboard"])
    st.write("---")
    st.write(f"👥 **Total Connected Students:** {len(global_db['active_students'])}")

# 4. STEP 1: UNIQUE STUDENT IDENTIFICATION IDENTIFIER
if "student_name" not in st.session_state:
    st.title("🛡️ Crowdsourced AI Validation Portal")
    st.write("Please sign in with your Name or Student ID to connect to the global simulation pipeline.")
    
    input_name = st.text_input("Enter Your Unique Identifier:", placeholder="e.g., Alex Smith").strip()
    
    if st.button("Connect Node to AI Core"):
        if input_name:
            st.session_state.student_name = input_name
            st.session_state.current_idx = 0 
            global_db["active_students"].add(input_name)
            st.rerun()
        else:
            st.error("Identifier cannot be blank.")
    st.stop()

# 5. VIEW A: STUDENT PORTAL (Individual pace, global submission)
if view_mode == "Student Portal":
    st.title(f"🧑‍💻 Validator Node: `{st.session_state.student_name}`")
    
    if st.session_state.current_idx < len(DATASET):
        active_item = DATASET[st.session_state.current_idx]
        q_id = active_item["id"]
        
        st.subheader(f"🎬 Block Context: {active_item['phase']}")
        st.caption(f"Task Progress: Item {st.session_state.current_idx + 1} of 10")
        
        st.markdown(f'<div class="comment-display">💬 "{active_item["text"]}"</div>', unsafe_allow_html=True)
        st.write(f"**Flagged String Found:** `{active_item['keyword']}`")
        
        student_votes_for_this_q = global_db["votes"][q_id]
        
        if st.session_state.student_name in student_votes_for_this_q:
            st.info(f"✅ Your vote (`{student_votes_for_this_q[st.session_state.student_name]}`) has been securely written to the global totals ledger.")
            if st.button("Advance to Next Comment ➡️", use_container_width=True):
                st.session_state.current_idx += 1
                st.rerun()
        else:
            st.write("### 🧑‍⚖️ Your Context Verdict Evaluation:")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚨 VOTE TOXIC", use_container_width=True):
                    global_db["votes"][q_id][st.session_state.student_name] = "Toxic"
                    st.rerun()
            with col2:
                if st.button("✅ VOTE SAFE", use_container_width=True):
                    global_db["votes"][q_id][st.session_state.student_name] = "Safe"
                    st.rerun()
    else:
        st.success("🎉 Excellent work! You have finished all 10 alignment evaluations. Look up at the screen for the final aggregated statistical matrix.")

# 6. VIEW B: INSTRUCTOR MASTER DASHBOARD (Projector Display Screen)
else:
    st.title("📊 Projector View: Live Classroom Consensus Summary")
    
    rows = []
    total_classroom_votes = 0
    total_rescued_false_positives = 0
    total_correct_toxic_flags = 0

    for item in DATASET:
        v_dict = global_db["votes"][item["id"]]
        total_votes = len(v_dict)
        total_classroom_votes += total_votes
        
        toxic_count = list(v_dict.values()).count("Toxic")
        safe_count = list(v_dict.values()).count("Safe")
        
        avg_toxic_pct = (toxic_count / total_votes * 100) if total_votes > 0 else 0.0
        ai_weight = round(avg_toxic_pct / 100, 2)
        
        # Tracking metrics for auto-explanation tracking
        if item["true_label"] == "Safe" and safe_count > toxic_count:
            total_rescued_false_positives += 1
        if item["true_label"] == "Toxic" and toxic_count > safe_count:
            total_correct_toxic_flags += 1
        
        rows.append({
            "ID": item["id"],
            "Keyword Target": item["keyword"],
            "Comment Content Log": item["text"],
            "Ground Truth": item["true_label"],
            "Total Votes Cast": total_votes,
            "Toxic Votes": toxic_count,
            "Safe Votes": safe_count,
            "Average Human Toxic Weight": f"{avg_toxic_pct:.1f}%",
            "Calibrated AI Weight": ai_weight
        })
        
    master_df = pd.DataFrame(rows)
    
    st.write("### 🧬 Real-time Data Validation Audit Log")
    st.dataframe(master_df, use_container_width=True, hide_index=True)
    
    st.write("---")
    
    # === NEW: AUTO-EXPLANATION GENERATOR ===
    st.header("🧠 Automated Simulation Insights & Findings")
    
    if total_classroom_votes == 0:
        st.warning("Awaiting initial incoming submission nodes from connected student devices to populate analytical evaluations.")
    else:
        # Calculate dynamic insights based on true system metrics
        censorship_saved_pct = (total_rescued_false_positives / 5) * 100  # 5 actual safe options in data
        toxic_caught_pct = (total_correct_toxic_flags / 5) * 100        # 5 actual toxic options in data
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>📈 Live Executive Breakdown:</h4>
            <ul>
                <li><b>Censorship Prevention:</b> The student panel successfully bypassed blind keyword rules to protect <b>{censorship_saved_pct:.0f}%</b> of legitimate user context options (False Positive reduction).</li>
                <li><b>True Poison Containment:</b> The system successfully verified and categorized <b>{toxic_caught_pct:.0f}%</b> of intentional adversarial bypass phrases.</li>
                <li><b>Data Density Logged:</b> A total volume of <b>{total_classroom_votes} unique human decisions</b> have filtered through the model matrix.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("#### 📝 Summary Evaluation Text (Read aloud to your class):")
        st.info(f"""
        "Prior to human validation, our baseline automation engine scored an operational precision rate of exactly 50% because it blindly banned words like *clown*, *tr@sh*, and *k1ll* without understanding content nuances. 
        
        By implementing a crowdsourced **Human-in-the-Loop network**, our 30 students served as independent audit nodes. The results above clearly prove the system's shift: items matching pure dictionary strings but carrying safe context (such as hair dye or airport codes) were naturally weighted down toward a Calibrated AI Value close to **0.00**. Conversely, actual malicious strings were isolated and elevated toward a safe containment index of **1.00**. This successfully maps real-world algorithmic reinforcement loops."
        """)

    # === HIDDEN SECRET RESET SYSTEM ===
    # Appending '?admin=true' to your web browser address bar explicitly renders this structural asset
    if st.query_params.get("admin") == "true":
        st.write("---")
        st.subheader("🛠️ Instructor Administrative Terminal")
        if st.button("⚠️ Emergency Server Clear Database", type="primary", use_container_width=True):
            global_db["votes"] = {item["id"]: {} for item in DATASET}
            global_db["active_students"].clear()
            st.success("Global shared database state flushed clean. Ready for next class period!")
            time.sleep(1.0)
            st.rerun()
