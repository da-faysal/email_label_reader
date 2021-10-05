# Import required modules
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import psycopg2
from datetime import datetime, timedelta
import plotly.graph_objects as go
import base64



# Login credentials
email = st.sidebar.text_input(label="Enter username")
password = st.sidebar.text_input("Enter password", type="password")
login_options = st.sidebar.radio("Login?", ("no", "yes"))

# Make logged in if the email is from google and password is "shared_with_you"
if "@gmail.com" in email and password=="shared_with_you":

	# If login_options=="yes" is clicked
	if login_options=="yes":

		# This function downloads a dataframe as csv
		def download_as_csv(df, file_name):
			csv = df.to_csv(index=False)
			b64 = base64.b64encode(csv.encode()).decode()
			link_to = f'<a href="data:file/csv;base64,{b64}" download="{file_name}.csv">Download as csv</a>'
			return link_to


		# Establish database connection or read from a csv file
		# engine = create_engine("postgresql+psycopg2://postgres:6125@localhost:5432/email_label")
		# df = pd.read_sql("select * from label", con=engine)
		df = pd.read_csv("data.csv")
		df.start_date = pd.to_datetime(df.start_date, format="%d/%m/%Y")
		df.end_date = pd.to_datetime(df.end_date, format="%d/%m/%Y")
		df = df.sort_values("start_date")

		# Set title for the application
		st.title("Email Label Frequency Application")

		# Select date rage
		with st.form(key="my_form"):
			start_date = pd.to_datetime(st.date_input(f'Select a start date (not less than {df.start_date.iloc[0].strftime("%d_%b_%y")})'))
			end_date = pd.to_datetime(st.date_input(f'Select an end date (not greater than {df.start_date.iloc[-1].strftime("%d_%b_%y")})'))
			# st.write(start_date)

			# Select barnds
			brand_option = st.selectbox("Select a brand", 
				tuple(list(df.brand.unique())) + ("All Brands", ))

			# Proceed futher if submit_button is not empty
			submit_button = st.form_submit_button(label="Calculate")
			if submit_button and brand_option!="All Brands":
				# Select data in between time and filter by brand
				filter_df = df[df.start_date.between(start_date, end_date)]
				filter_df = filter_df[filter_df.brand==brand_option]
				grouped_by = filter_df.groupby(["label"])["total_email"].sum().reset_index()

				# Insert start date
				grouped_by["start_date"] = start_date
				grouped_by.start_date = grouped_by.start_date.dt.strftime("%d_%b_%y")
				grouped_by["end_date"] = end_date
				grouped_by.end_date = grouped_by.end_date.dt.strftime("%d_%b_%y")
				grouped_by["brand"] = brand_option
				grouped_by = grouped_by[["start_date", "end_date", "label", "total_email", "brand"]].sort_values("total_email", ascending=False).reset_index(drop=True)
				

				# Plot table using plotly
				fig = go.Figure(data=[go.Table(
					header=dict(values=list(grouped_by.columns),
						fill_color='paleturquoise',
		                align='left'),

					cells=dict(values=[grouped_by.start_date, grouped_by.end_date, grouped_by.label, grouped_by.total_email, grouped_by.brand],
						fill_color='lavender',
						align='left'))])
				fig.update_layout(title_text=f'{brand_option} Label Frequency from {start_date.strftime("%d_%b_%y")} to {end_date.strftime("%d_%b_%y")}')
				st.plotly_chart(fig)


				# Can be downloaded as csv
				st.markdown(download_as_csv(grouped_by, brand_option), unsafe_allow_html=True)

				# Make plotly charts
				fig = go.Figure()

				# Update figure layout
				fig.update_layout(
		        	xaxis_tickangle=90,
		        	xaxis_title="Label",
		        	yaxis_title="Label Count",
		        	title_text=f'{brand_option} Email Label Frequency from {start_date.strftime("%d_%b_%y")} to {end_date.strftime("%d_%b_%y")}',
		        	width=700,
				    height=500)


				# Add trace to the fig
				fig.add_trace(go.Bar(
		            x=grouped_by.label.iloc[:12].tolist(),
		            y=grouped_by.total_email.iloc[:12].tolist(),
		            name=f"{start_date} to {end_date}",
		            text=grouped_by.total_email.iloc[:12].tolist(),
		            marker_color='indianred',
		            textposition="auto"))

				# Render chart on streamlit
				st.plotly_chart(fig)


			# If "All Brands" is selected on dropdown
			if submit_button and brand_option=="All Brands":

				# This function return one provider data
				def download_all(brand_option):

					# Filter dataframe by a brand
					filter_df = df[df.start_date.between(start_date, end_date)]
					filter_df = filter_df[filter_df.brand==brand_option]
					grouped_by = filter_df.groupby(["label"])["total_email"].sum().reset_index()

					# Insert start date
					grouped_by["start_date"] = start_date
					grouped_by.start_date = grouped_by.start_date.dt.strftime("%d_%b_%y")

					grouped_by["end_date"] = end_date
					grouped_by.end_date = grouped_by.end_date.dt.strftime("%d_%b_%y")

					grouped_by["brand"] = brand_option
					grouped_by = grouped_by[["start_date", "end_date", "label", "total_email", "brand"]].sort_values("total_email", ascending=False).reset_index(drop=True)
					return grouped_by

				# Merge all the dataframe together
				merged = pd.concat(list(map(download_all, df.brand.unique()))).reset_index(drop=True)

				# Make "All Brands" data downloadable
				st.markdown(download_as_csv(merged, "All Brands"), unsafe_allow_html=True)
else:
	if login_options=="yes":
		st.error("Invalid email or password!")

