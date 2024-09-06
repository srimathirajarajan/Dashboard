import streamlit as st
import pandas as pd
import plotly.express as px
import snowflake.connector

st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to style the KPI boxes and dashboard with hover effect
st.markdown(
    """
    <style>
    .kpi-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 20px;
        transition: border-color 0.3s ease;
        border: 2px solid transparent;
    }
    .kpi-box:hover {
        border-color: #2596BE; /* Blue color on hover */
    }
    .kpi-label {
        font-size: 1.2em;
        color: #333333;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 2.5em;
        color: #2596BE;
        font-weight: bold;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    h1 {
        color: #2596BE;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

conn = snowflake.connector.connect(
    user='SRIMATHI',
    password='Shri@1608',
    account='ev90757.ap-southeast-1',
    warehouse='COMPUTE_WH',
    database='MEC',
    schema='JSON'
)

def run_query(query):
    cur = conn.cursor()
    cur.execute(query)
    df = cur.fetch_pandas_all()
    cur.close()
    return df

# Sample Queries
gender_distribution_query = """
SELECT PATIENT_DETAILS:gender::STRING AS gender, COUNT(*) AS count
FROM PATIENT_DETAILS
GROUP BY PATIENT_DETAILS:gender
"""
df_gender_distribution = run_query(gender_distribution_query)

total_admission_query = """
SELECT COUNT(*) AS count
FROM ADMISSION_DISCHARGE_DATA;
"""
df_admission = run_query(total_admission_query)

total_doctors_query = """
SELECT COUNT(DISTINCT DOCTOR_DETAILS:doctor_id) AS count
FROM DOCTOR_DETAILS;
"""
df_doctors = run_query(total_doctors_query)

admission_outcome_query = """
SELECT 
    ADMISSION_DISCHARGE_DATA:admission.admission_type::STRING AS admission_type,  
    COUNT(*) AS count
FROM ADMISSION_DISCHARGE_DATA
GROUP BY admission_type;
"""
df_admission_outcome = run_query(admission_outcome_query)

common_medications_query = """
SELECT MEDICAL_HISTORIES:medical_history.medications[0].medication_name::STRING AS medication_name, COUNT(*) AS count
FROM MEDICAL_HISTORIES
GROUP BY MEDICAL_HISTORIES:medical_history.medications[0].medication_name
ORDER BY count DESC
LIMIT 10
"""
df_common_medications = run_query(common_medications_query)

surgeries_performed_query = """
SELECT MEDICAL_HISTORIES:medical_history.surgeries[0].surgery_type::STRING AS surgery_type, COUNT(*) AS count
FROM MEDICAL_HISTORIES
GROUP BY MEDICAL_HISTORIES:medical_history.surgeries[0].surgery_type
"""
df_surgeries_performed = run_query(surgeries_performed_query)

age_group_distribution_query = """
SELECT 
    CASE 
        WHEN PATIENT_DETAILS:age::INT BETWEEN 0 AND 18 THEN '0-18'
        WHEN PATIENT_DETAILS:age::INT BETWEEN 19 AND 35 THEN '19-35'
        WHEN PATIENT_DETAILS:age::INT BETWEEN 36 AND 50 THEN '36-50'
        WHEN PATIENT_DETAILS:age::INT BETWEEN 51 AND 65 THEN '51-65'
        ELSE '65+'
    END AS age_group,
    COUNT(*) AS count
FROM PATIENT_DETAILS
GROUP BY age_group
"""
df_age_group_distribution = run_query(age_group_distribution_query)

total_patients_kpi = df_gender_distribution['COUNT'].sum()
total_admission_kpi = df_admission['COUNT'].iloc[0] 
total_doctors_kpi = df_doctors['COUNT'].iloc[0]

constant_color_theme = ['#2596BE']

# Define the charts
gender_donut_chart = px.pie(
    df_gender_distribution, 
    names='GENDER',  
    values='COUNT',  
    title='Gender Distribution of Patients',
    color_discrete_sequence=constant_color_theme,
    hole=0.6
).update_layout(
    height=250,
    width=250,
    margin=dict(l=10, r=10, t=30, b=10)
)

age_donut_chart = px.pie(
    df_age_group_distribution,
    names='AGE_GROUP',
    values='COUNT',
    title='Age Group Distribution of Patients',
    color_discrete_sequence=constant_color_theme,
    hole=0.6
).update_layout(
    height=250,
    width=250,
    margin=dict(l=10, r=10, t=30, b=10)
)

admission_outcome_bar_chart = px.bar(
    df_admission_outcome,  
    x='COUNT',                 
    y='ADMISSION_TYPE',      
    title='Number of Patients per Admission Outcome',
    color_discrete_sequence=constant_color_theme
).update_layout(
    height=300,
    margin=dict(l=10, r=10, t=30, b=10)
)

medications_line_chart = px.line(
    df_common_medications,  
    x='MEDICATION_NAME',    
    y='COUNT',              
    title='Most Common Medications',
    color_discrete_sequence=constant_color_theme,
    markers=True  
).update_layout(
    height=300,
    margin=dict(l=10, r=10, t=30, b=10)
)

surgeries_bubble_chart = px.scatter(
    df_surgeries_performed,  
    x='SURGERY_TYPE',        
    y='COUNT',               
    size='COUNT',            
    title='Surgeries Performed',
    color_discrete_sequence=constant_color_theme
).update_layout(
    height=300,
    margin=dict(l=10, r=10, t=30, b=10)
)

# Custom CSS for header
st.markdown("<h1 style='text-align: center; margin-top: 0rem;'>Analytics Dashboard</h1>", unsafe_allow_html=True)

# Center the KPIs in separate boxes
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
kpi_column1, kpi_column2, kpi_column3 = st.columns(3)

with kpi_column1:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-label">Total Patients</div>
        <div class="kpi-value">{total_patients_kpi}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_column2:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-label">Total Doctors</div>
        <div class="kpi-value">{total_doctors_kpi}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_column3:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-label">Total Admitted Patients</div>
        <div class="kpi-value">{total_admission_kpi}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Main layout: Left and right columns for charts
left_column, right_column = st.columns([1, 2])

with left_column:
    st.plotly_chart(gender_donut_chart, use_container_width=True)
    st.plotly_chart(age_donut_chart, use_container_width=True)

with right_column:
    col1, col2 = st.columns(2)
    col1.plotly_chart(surgeries_bubble_chart, use_container_width=True)
    col2.plotly_chart(medications_line_chart, use_container_width=True)
    st.plotly_chart(admission_outcome_bar_chart, use_container_width=True)
