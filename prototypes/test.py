import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

# Sample data
data = {
    'StudentID': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010,
                  1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020],
    'MathGrade': [85, 92, 78, 95, 88, 79, 83, 90, 87, 91,
                  76, 92, 85, 89, 94, 83, 79, 87, 88, 90]
}

# Create a Bokeh histogram plot
def create_histogram(data):
    p = figure(title="Math Grade Distribution", tools="hover", background_fill_color="#f9f9f9")
    hist, edges = np.histogram(data['MathGrade'], bins=10)
    source = ColumnDataSource(data=dict(hist=hist, left=edges[:-1], right=edges[1:]))
    p.quad(top='hist', bottom=0, left='left', right='right', source=source, fill_color="#0365c0")
    p.y_range.start = 0
    p.xaxis.axis_label = 'Math Grade'
    p.yaxis.axis_label = 'Frequency'
    return p

# Streamlit app
def main():
    st.title("Grade Distribution")
    st.sidebar.title("Settings")

    # Display the histogram
    p = create_histogram(data)
    st.bokeh_chart(p, use_container_width=True)

if __name__ == '__main__':
    main()
