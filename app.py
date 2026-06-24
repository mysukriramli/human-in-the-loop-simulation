import streamlit as st
import time
import pandas as pd

st.set_page_config(page_title="AI Knowledge Base Simulation", layout="wide")

# Custom CSS for UI Feedback
st.markdown("""
<style>
    .comment-card {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 5px solid #bdc3c7;
        background-color: #f8f9fa;
    }
    .toxic-style { background-color: #fde8e8 !important; border-left: 5px solid #e74c3c !important; color: #c0392b; font-weight: bold;}
    .safe-style { background-color: #edf7ed !important; border-left: 5px solid #2ecc71 !important; color: #27ae60; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# 1. Initialization & 12-Question Dataset
if 'sim_step' not in st.session_state:
    st.session_state.sim_step = 0  # Tracks our position from 0 to 12
    st.session_state.ai_knowledge_base = {}  # Dynamic rules learned from humans
    st.session_state.logs = []  # Statistical tracking
    
    # 12 Detailed Questions divided into your 3 requested structural phases
    st.session_state.questions = [
        # === PHASE 1: ALL POSSIBLE NEGATIVE COMMENTS ===
        {"text": "Bro, honestly just go dye.", "keyword": "go dye", "is_toxic": True, "phase": "Phase 1: Pure Negative"},
        {"text": "You are literal tr@sh throw yourself away.", "keyword": "tr@sh", "is_toxic": True, "phase": "Phase 1: Pure Negative"},
        {"text": "I hope your account gets deleted and you go dye in a hole.", "keyword": "go dye", "is_toxic": True, "phase": "Phase 1: Pure Negative"},
        {"text": "Delete this video u r tr@sh garbage human.", "keyword": "tr@sh", "is_toxic": True, "phase": "Phase 1: Pure Negative"},
        
        # === PHASE 2: ALL POSSIBLE SAFE COMMENTS ===
        {"text": "I need to go dye my hair roots dark blue this weekend.", "keyword": "go dye", "is_toxic": False, "phase": "Phase 2: Pure Safe"},
        {"text": "Don't forget that tr@sh collection day was moved to Tuesday.", "keyword": "tr@sh", "is_toxic": False, "phase": "Phase 2: Pure Safe"},
        {"text": "Should I go dye this cotton shirt or use fabric paint?", "keyword": "go dye", "is_toxic": False, "phase": "Phase 2: Pure Safe"},
        {"text": "Can you empty the tr@sh bin in the kitchen please?", "keyword": "tr@sh", "is_toxic": False, "phase": "Phase 2: Pure Safe"},
        
        # === PHASE 3: MIXED BAD AND GOOD ===
        {"text": "Go dye your hair? No, how about you just go dye.", "keyword": "go dye", "is_toxic": True, "phase": "Phase 3: Mixed Evaluation"},
        {"text": "This artwork is beautiful, it looks like custom tie-dye!", "keyword": "go dye", "is_toxic": False, "phase": "Phase 3: Mixed Evaluation"},
        {"text": "Stop posting your trash game clips u r tr@sh.", "keyword": "tr@sh", "is_toxic": True, "phase": "Phase 3: Mixed Evaluation"},
        {"text": "The recycling program helps reduce local tr@sh waste.", "keyword": "tr@sh", "is_toxic": False, "phase": "Phase 3: Mixed Evaluation"}
    ]

# 2. Main Sidebar Navigation & AI Memory View
with st.sidebar:
    st.title("🧠 AI Memory Core")
    st.write("This is what the AI is actively logging based on student inputs:")
    
    if st.session_state.ai_knowledge_base:
        for kw, decision in st.session_state.ai_knowledge_base.items():
            st.code(f"IF context contains '{kw}'\nTHEN pattern learned: {decision}")
    else:
        st.caption("AI knowledge base is currently empty. Awaiting student judgments...")
        
    st.write("---")
    # Progress Tracking
    progress = min(st.session_state.sim_step / 12, 1.0)
    st.progress(progress)
    st.caption(f"Completed: {st.session_state.sim_step} / 12 moderation tasks")

# 3. Execution Game Logic
if st.session_state.sim_step < 12:
    current_q = st.session_state.questions[st.session_state.sim_step]
    
    # Header display showing the explicit phase
    st.subheader(f"🎬 Current Simulation Block: {current_q['phase']}")
    st.write(f"**Item Progress:** Question {st.session_state.sim_step + 1} of 12")
    
    # Render the text container placeholder
    card_placeholder = st.empty()
    card_placeholder.markdown(f'<div class="comment-card">💬 "{current_q["text"]}"</div>', unsafe_allow_html=True)
    
    st.write("#### 🧑‍⚖️ Class Verdict: Does this comment require an administrative safety ban?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚨 YES - Flag As Malicious", use_container_width=True):
            # Show red-flag feedback transformation
            card_placeholder.markdown(f'<div class="comment-card toxic-style">🚨 [FLAGGED & PURGED] "{current_q["text"]}"</div>', unsafe_allow_html=True)
            time.sleep(0.8)
            card_placeholder.empty() # Vanishing animation step
            
            # Update AI Memory Core
            st.session_state.ai_knowledge_base[current_q["text"]] = "MARKED AS HARASSMENT"
            st.session_state.logs.append({"text": current_q["text"], "phase": current_q["phase"], "verdict": "Flagged", "correct": current_q["is_toxic"] == True})
            
            st.session_state.sim_step += 1
            st.rerun()
            
    with col2:
        if st.button("✅ NO - Approve Safe Content", use_container_width=True):
            # Show safe green feedback transformation
            card_placeholder.markdown(f'<div class="comment-card safe-style">✅ [APPROVED CONTENT] "{current_q["text"]}"</div>', unsafe_allow_html=True)
            time.sleep(0.8)
            card_placeholder.empty()
            
            # Update AI Memory Core
            st.session_state.ai_knowledge_base[current_q["text"]] = "MARKED AS SAFE CONTEXT"
            st.session_state.logs.append({"text": current_q["text"], "phase": current_q["phase"], "verdict": "Approved", "correct": current_q["is_toxic"] == False})
            
            st.session_state.sim_step += 1
            st.rerun()

# 4. Final Summary Page & Comprehensive Statistical Explainer
else:
    st.balloons()
    st.success("🏁 All 12 configuration cases have been fully moderated by the classroom!")
    st.header("📊 Final Simulation Analysis & Analytics Review")
    
    log_df = pd.DataFrame(st.session_state.logs)
    
    # Calculate performance metrics
    total_decisions = len(log_df)
    correct_decisions = log_df["correct"].sum()
    student_accuracy = (correct_decisions / total_decisions) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("Total Questions Evaluated", total_decisions)
    col2.metric("Classroom Accuracy Score", f"{student_accuracy:.1f}%")
    
    st.write("### Comprehensive Decision Audit Trail")
    st.dataframe(log_df, use_container_width=True)
    
    st.write("### 🎓 Core Learning Takeaways for the Class")
    st.markdown("""
    1. **Phase 1 Lessons:** When evaluating purely negative content, rule creation seems incredibly easy. If the AI simply blocked strings like `"go dye"`, it would catch 100% of the bad actors here.
    2. **Phase 2 Lessons:** When transitioning to purely safe content, context reverses everything. If the blind rules from Phase 1 remained completely unedited, the platform would have wrongfully censored users talking about *hair fashion* and *household chores*.
    3. **Phase 3 Lessons:** The final mixed test demonstrates why static code rules fail. Human-in-the-loop systems allow software infrastructure to constantly log edge cases and append exception tables dynamically, preserving free speech while containing true toxicity.
    """)
    
    if st.button("Reset Entire 12-Question Simulation Loop"):
        st.session_state.sim_step = 0
        st.session_state.ai_knowledge_base = {}
        st.session_state.logs = []
        st.rerun()
