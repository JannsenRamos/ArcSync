import streamlit as st
from agents.manager import ManagerAgent
from agents.context_agent import ContextAgent

# Page Configuration for a Professional Hackathon MVP
st.set_page_config(page_title="Arch-Sync | Feature-to-Spec", layout="wide")

def main():
    st.title("🚀 Arch-Sync: Context-Aware Spec Generator")
    st.markdown("---")

    # Initialize our Agents
    manager = ManagerAgent()
    context_engine = ContextAgent()

    # Sidebar: Compliance & Context Status
    with st.sidebar:
        st.header("🛠 IBM Bob Status")
        # Satisfies FR2: Showing the active tech stack detected by Bob
        constraints = context_engine.get_grounding_constraints()
        st.success(f"Tech Stack: {constraints['tech_stack']}")
        st.info(f"Files Indexed: {constraints['file_count']}")
        
        st.markdown("---")
        # Mandatory Hackathon Deliverable: Export Button
        if st.button("📦 Export IBM Bob Session Report"):
            st.write("Report generated in `/logs/ibm_bob_audit/`")
            st.caption("Submit this JSONL file with your entry.")

    # Main Interface: FR1 Natural Language Intake
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Feature Intent")
        feature_name = st.text_input("Feature Name", placeholder="e.g., User Authentication")
        user_input = st.text_area(
            "Describe the feature requirements:",
            placeholder="Describe what you want to build in plain language...",
            height=200
        )
        
        generate_btn = st.button("Generate Technical Specification")

    # Output Pane: FR3 Specification Generation
    with col2:
        st.subheader("2. Grounded Specification")
        if generate_btn and user_input:
            with st.spinner("Querying IBM Bob & Generating Spec..."):
                # The Manager Agent orchestrates the retrieval and generation
                final_spec = manager.orchestrate_spec_request(feature_name, user_input)
                st.markdown(final_spec)
        else:
            st.info("Enter feature details and click generate to see the context-aware blueprint.")

if __name__ == "__main__":
    main()