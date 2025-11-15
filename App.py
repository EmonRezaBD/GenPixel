import streamlit as st
from PIL import Image
from fractions import Fraction
import io

# --- 1. Key Counter Initialization ---
# Initialize the counter used for key rotation in the file uploader
if "uploader_key_counter" not in st.session_state:
    st.session_state["uploader_key_counter"] = 0
    # Initialize a variable to hold the actual uploaded file object
    st.session_state["current_uploaded_file"] = None 

# --- 2. Correct Reset Callback Function ---
def reset_app_state():
    """Increments the key counter to force the file_uploader widget to reset."""
    # This is the correct way to reset st.file_uploader: change its key!
    st.session_state["uploader_key_counter"] += 1 
    
    # Clear the saved file object
    st.session_state["current_uploaded_file"] = None


def app():
    """
    Streamlit application function to upload an image, display it, 
    and show analysis results in a two-column layout.
    """
    # --- Configuration and Browser Title ---
    st.set_page_config(
        page_title="Image Dimension Analyzer", 
        layout="wide", 
        initial_sidebar_state="auto"
    )

    # --- Centering the Main App Title ---
    col_center_1, col_center_2, col_center_3 = st.columns([1, 3, 1])

    with col_center_2:
        # Using centered HTML for the main title
        st.markdown(
            """
            <div style='text-align: center; color: #1E90FF;'>
                <h1>🖼️ Image Dimension Analyzer</h1>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <div style='text-align: center;'>
                Upload an image on the left, analyze dimensions, or clear the app state using the Reset button.
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    st.markdown("---") 

    # --- Setup Two Columns for the Body Layout ---
    col_upload, col_analysis = st.columns([1, 1]) 

    image_data = None
    uploaded_file = None
    
    # --- Left Column: Uploader and Preview ---
    with col_upload:
        st.subheader("1. Upload Image")
        
        # Use the dynamic key based on the counter to allow programmatic reset
        uploaded_file = st.file_uploader(
            "Choose an image file...", 
            type=["png", "jpg", "jpeg"],
            key=f"file_uploader_{st.session_state['uploader_key_counter']}" 
        )
        
        # Logic to persist the file object across Streamlit runs
        if uploaded_file is not None:
            # If a file is newly uploaded, save it to session state
            st.session_state["current_uploaded_file"] = uploaded_file
        
        # Use the file object saved in session state for consistency
        current_file = st.session_state.get("current_uploaded_file")
        
        if current_file is not None:
            uploaded_file = current_file # Use the stored object for processing
            
            try:
                # Read the file object using io.BytesIO for compatibility with key rotation
                image_bytes = uploaded_file.getvalue()
                image_data = Image.open(io.BytesIO(image_bytes))
                
                st.subheader("2. Image Preview")
                with st.container(border=True):
                    # Using the correct parameter: use_container_width=True
                    st.image(image_data, caption=uploaded_file.name, use_container_width=True) 

            except Exception as e:
                # Clear state on processing error
                st.error(f"An error occurred while processing the image: {e}")
                image_data = None
                st.session_state["current_uploaded_file"] = None 
                uploaded_file = None 

    # --- Right Column: Analysis Button and Report ---
    with col_analysis:
        # Create a container for the analysis button and the new reset button
        button_col, reset_col = st.columns([3, 1])
        
        is_file_ready = uploaded_file is not None and image_data is not None
        analysis_clicked = False
        
        with button_col:
            st.subheader("3. Image Analysis Report")
            
            if is_file_ready:
                analysis_clicked = st.button("Analyze Image Dimensions", type="primary", use_container_width=True)
            else:
                # Disabled button when no file is ready
                st.button("Analyze Image Dimensions", disabled=True, use_container_width=True)
        
        # RESET BUTTON setup
        with reset_col:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button(
                "🔄 Reset", 
                on_click=reset_app_state, 
                type="secondary"
            )

        report_container = st.empty()
        
        if is_file_ready:
            
            if analysis_clicked:
                # --- Perform Analysis ---
                width, height = image_data.size
                
                try:
                    aspect_ratio_fraction = Fraction(width, height)
                    aspect_ratio_str = f"{aspect_ratio_fraction.numerator}:{aspect_ratio_fraction.denominator}"
                except ZeroDivisionError:
                    aspect_ratio_str = "N/A"
                
                # Write results to the report container
                with report_container.container(border=True):
                    st.success("✅ Analysis Complete!")
                    st.write(f"**File Name:** `{uploaded_file.name}`")
                    
                    st.markdown("---")
                    
                    # Display Dimensions and Aspect Ratio using metrics
                    col1_r, col2_r, col3_r = st.columns(3)
                    
                    with col1_r:
                        st.metric(label="Width (Pixels)", value=f"{width:,} px")
                    
                    with col2_r:
                        st.metric(label="Height (Pixels)", value=f"{height:,} px")

                    with col3_r:
                        st.metric(label="Aspect Ratio", value=aspect_ratio_str)
                        
                    st.caption("Dimensions are retrieved using the Pillow (PIL) library.")

            else:
                report_container.info("Click the Analyze button to see the dimensions, or the Reset button to clear.")

        else:
            report_container.warning("Upload a supported image file (PNG, JPG) in the left column to begin analysis.")

# Run the app function
if __name__ == "__main__":
    app()