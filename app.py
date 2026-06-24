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
    # Initializes a single dictionary accessible by all network users
    db = {
        "votes": {item["id"]: {} for item in DATASET}, # Structure: { q_id: { student_name: "Toxic"/"Safe" } }
        "active_students": set()
    }
    return db

global_db = get_classroom_database()

# 3. SIDEBAR (QR Code and Unique Role/Identity View)
with st.sidebar:
    st.header("📲 Classroom Connection")
    app_url = "https://human-in-the-loop-simulation-nwty9jxhv6vb7gjyc3dodw.streamlit.app/"
    
    # Static QR Generation
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(app_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="Scan to participate live")
    
    st.write("---")
    # Role Toggle: Allows you to switch the projector screen to monitor global results
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
            st.session_state.current_idx = 0 # Individual browser progress tracker
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
        
        # Check if this specific student has already voted on this question
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
    st.write("This screen aggregates data from all 30 students in real time to calculate the average validation threshold metrics.")
    
    rows = []
    for item in DATASET:
        v_dict = global_db["votes"][item["id"]]
        total_votes = len(v_dict)
        toxic_count = list(v_dict.values()).count("Toxic")
        safe_count = list(v_dict.values()).count("Safe")
        
        # Human average calculation formula
        avg_toxic_pct = (toxic_count / total_votes * 100) if total_votes > 0 else 0.0
        
        # Dynamic AI Weight calibration based on student validation average score
        ai_weight = round(avg_toxic_pct / 100, 2)
        
        rows.append({
            "ID": item["id"],
            "Keyword Target": item["keyword"],
            "Comment Content Log": item["text"],
            "Ground Truth": item["true_label"],
            "Total Votes Cast": total_votes,
            "Toxic Count": toxic_count,
            "Safe Count": safe_count,
            "Average Human Toxic Weight": f"{avg_toxic_pct:.1f}%",
            "Calibrated AI Memory Weight": ai_weight
        })
        
    master_df = pd.DataFrame(rows)
    
    # Display analytical performance components
    st.write("### 🧬 Real-time Data Validation Audit Log")
    st.dataframe(master_df, use_container_width=True, hide_index=True)
    
    # Hidden Secret Admin Clear Option (Only accessible if url ends with ?admin=true)
    if st.query_params.get("admin") == "true":
        if st.button("⚠️ Emergency Server Clear Database"):
            global_db["votes"] = {item["id"]: {} for item in DATASET}
            global_db["active_students"].clear()
            st.rerun()
