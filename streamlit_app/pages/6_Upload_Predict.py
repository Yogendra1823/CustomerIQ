import streamlit as st
import pandas as pd
import sys
import os

# Set page config
st.set_page_config(page_title="Upload & Predict", page_icon="📤", layout="wide")

# Add utils to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.ml import predict_customer

st.title("Batch Segment Predictor")
st.markdown("Upload a CSV file containing customer demographics and behavioral features to run real-time segment prediction.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        
        # Display preview of first 5 rows
        st.subheader("Uploaded Data Preview")
        st.dataframe(df.head(5), use_container_width=True)
        
        # Run prediction on click
        if st.button("Run Batch Segment Predictions"):
            st.info("Processing predictions...")
            results = []
            
            # Show progress bar
            progress_bar = st.progress(0)
            total_rows = len(df)
            
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                pred = predict_customer(row_dict)
                
                results.append({
                    "Customer ID": row.get("external_id") or row.get("Customer ID") or f"ROW_{idx}",
                    "Predicted Segment": pred["segment_name"],
                    "Churn Probability": pred["churn_probability"],
                    "Value Persona": pred["persona"],
                    "Recommended Strategy": pred["recommended_action"]
                })
                progress_bar.progress((idx + 1) / total_rows)
                
            df_results = pd.DataFrame(results)
            st.success("Batch prediction completed!")
            
            st.subheader("Prediction Results")
            st.dataframe(
                df_results,
                column_config={
                    "Churn Probability": st.column_config.ProgressColumn("Churn Risk", format="%.2f", min_value=0.0, max_value=1.0)
                },
                use_container_width=True
            )
            
            # Export CSV button
            csv_data = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Segmented CSV Output",
                data=csv_data,
                file_name="customeriq_batch_predictions.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"Error processing CSV file: {str(e)}")
else:
    st.info("Please upload a CSV file matching the customer features structure.")
