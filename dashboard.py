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

# Custom CSS for improved styling with varying blue shades
st.markdown(
    """
    <style>
    .kpi-box {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
        border: 2px solid transparent;
        color: white;
        font-weight: bold;
    }
    .kpi-label {
        font-size: 1.3em;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 2.8em;
    }
    .kpi-box.kpi-1 {
        background-color: #1f77b4; /* Deep Blue */
    }
    .kpi-box.kpi-2 {
        background-color: #097bf5; /* Medium Blue */
    }
    .kpi-box.kpi-3 {
        background-color: #007bff; /* Light Blue */
    }
    .title-box {
        background-color: #34b7f1;
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.15);
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    h1 {
        color: #ffffff;
        font-weight: bold;
    }
    .chart-container {
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        background-color: #ffffff;
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

# Define the charts with enhanced styling
constant_color_theme = ['#34b7f1']  # Updated color scheme

gender_donut_chart = px.pie(
    df_gender_distribution, 
    names='GENDER',  
    values='COUNT',  
    title='Gender Distribution of Patients',
    color_discrete_sequence=constant_color_theme,
    hole=0.6
).update_traces(
    hoverinfo="label+percent", 
    textinfo="label+percent",
    textfont_size=16,
    marker=dict(line=dict(width=2, color='darkblue'))
).update_layout(
    height=350,
    width=350,
    margin=dict(l=10, r=10, t=30, b=10),
    title_font_size=22
)

age_donut_chart = px.pie(
    df_age_group_distribution,
    names='AGE_GROUP',
    values='COUNT',
    title='Age Group Distribution of Patients',
    color_discrete_sequence=constant_color_theme,
    hole=0.6
).update_traces(
    hoverinfo="label+percent", 
    textinfo="label+percent",
    textfont_size=16,
    marker=dict(line=dict(width=2, color='darkblue'))
).update_layout(
    height=350,
    width=350,
    margin=dict(l=10, r=10, t=30, b=10),
    title_font_size=22
)

admission_outcome_bar_chart = px.bar(
    df_admission_outcome,  
    x='COUNT',                 
    y='ADMISSION_TYPE',      
    title='Number of Patients per Admission Outcome',
    color_discrete_sequence=constant_color_theme
).update_traces(
    hoverinfo="x+y",
    marker=dict(line=dict(width=1, color='darkblue')),
    orientation='h'
).update_layout(
    height=400,
    margin=dict(l=10, r=10, t=30, b=10),
    title_font_size=22
)

medications_line_chart = px.line(
    df_common_medications,  
    x='MEDICATION_NAME',    
    y='COUNT',              
    title='Most Common Medications',
    color_discrete_sequence=constant_color_theme,
    markers=True  
).update_traces(
    hoverinfo="x+y",
    line=dict(width=3),
    marker=dict(size=10, color='blue')
).update_layout(
    height=400,
    margin=dict(l=10, r=10, t=30, b=10),
    title_font_size=22
)

surgeries_bubble_chart = px.scatter(
    df_surgeries_performed,  
    x='SURGERY_TYPE',        
    y='COUNT',               
    size='COUNT',            
    title='Surgeries Performed',
    color_discrete_sequence=constant_color_theme
).update_traces(
    hoverinfo="x+y",
    marker=dict(opacity=0.8, line=dict(width=2, color='darkblue'))
).update_layout(
    height=400,
    margin=dict(l=10, r=10, t=30, b=10),
    title_font_size=22
)

# Center the KPIs in separate boxes
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
kpi_column1, kpi_column2, kpi_column3 = st.columns(3)

with kpi_column1:
    st.markdown(f"""
    <div class="kpi-box kpi-1">
        <div class="kpi-label">Total Patients</div>
        <div class="kpi-value">{total_patients_kpi}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_column2:
    st.markdown(f"""
    <div class="kpi-box kpi-2">
        <div class="kpi-label">Total Doctors</div>
        <div class="kpi-value">{total_doctors_kpi}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_column3:
    st.markdown(f"""
    <div class="kpi-box kpi-3">
        <div class="kpi-label">Total Admissions</div>
        <div class="kpi-value">{total_admission_kpi}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Display the charts in a 2-column layout
st.markdown("<div class='chart-container' style='display: flex; justify-content: space-between;'>", unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(gender_donut_chart, use_container_width=True)
        st.plotly_chart(age_donut_chart, use_container_width=True)
    
    with col2:
        st.plotly_chart(admission_outcome_bar_chart, use_container_width=True)
        st.plotly_chart(medications_line_chart, use_container_width=True)
        st.plotly_chart(surgeries_bubble_chart, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
