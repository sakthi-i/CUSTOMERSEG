import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from pymongo import MongoClient  # MongoDB client library

# Set the title of the Streamlit app
st.title("Customer Segmentation with K-Means Clustering")

# File uploader for CSV input
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV file
    customer_data = pd.read_csv(uploaded_file)

    # Display the first few rows of the dataset
    st.subheader("Dataset Preview")
    st.write(customer_data.head())

    # Check for missing values
    if customer_data.isnull().sum().sum() > 0:
        st.warning("The dataset contains missing values. Please clean the data before proceeding.")
    else:
        # Allow user to select columns for clustering
        st.subheader("Select Columns for Clustering")
        numeric_columns = customer_data.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_columns) < 2:
            st.error("The dataset must contain at least two numeric columns for clustering.")
        else:
            selected_columns = st.multiselect(
                "Choose at least two numeric columns:",
                options=numeric_columns,
                default=numeric_columns[:2]
            )

            if len(selected_columns) < 2:
                st.warning("Please select at least two columns to proceed.")
            else:
                # Prepare data for clustering
                X = customer_data[selected_columns].values

                # Elbow method to find the optimal number of clusters
                st.subheader("Elbow Method for Optimal Cluster Count")
                wcss = []
                max_clusters = min(10, len(X))  # Limit clusters to 10 or dataset size
                for i in range(1, max_clusters + 1):
                    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
                    kmeans.fit(X)
                    wcss.append(kmeans.inertia_)

                # Plot the Elbow Method graph
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.plot(range(1, max_clusters + 1), wcss, marker='o', linestyle='-', color='b')
                ax.set_title('The Elbow Point Graph')
                ax.set_xlabel('Number of Clusters')
                ax.set_ylabel('WCSS')
                st.pyplot(fig)

                # Allow user to set the number of clusters
                st.subheader("Select Number of Clusters")
                n_clusters = st.slider("Number of Clusters (k):", min_value=2, max_value=max_clusters, value=5, step=1)

                # Perform K-Means clustering
                kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42)
                Y = kmeans.fit_predict(X)

                # Add cluster labels to the dataframe
                customer_data['Cluster'] = Y

                # Display the clustered data preview
                st.subheader("Clustered Data Preview")
                st.write(customer_data.head())

                # MongoDB connection
                client = MongoClient("mongodb://localhost:27017/")  # Connect to MongoDB
                db = client["customer_segmentation_db"]  # Create a database called 'customer_segmentation_db'
                collection = db["customer_segments"]  # Create a collection called 'customer_segments'

                # Convert DataFrame to list of dictionaries (documents for MongoDB)
                data_to_store = customer_data.to_dict(orient="records")

                # Insert the clustered data into MongoDB
                collection.insert_many(data_to_store)

                # Success message
                st.success("Clustered data has been successfully stored in MongoDB!")

                # Customer Segmentation Graph (Scatter Plot)
                st.subheader("Customer Segmentation Visualization")
                fig, ax = plt.subplots(figsize=(8, 8))
                colors = ['green', 'red', 'yellow', 'violet', 'blue', 'orange', 'pink', 'cyan', 'brown', 'gray']

                # Plot the clusters
                for i in range(n_clusters):
                    ax.scatter(
                        X[Y == i, 0], X[Y == i, 1],
                        s=50, c=colors[i % len(colors)], label=f'Cluster {i + 1}'
                    )

                # Plot centroids
                ax.scatter(
                    kmeans.cluster_centers_[:, 0],
                    kmeans.cluster_centers_[:, 1],
                    s=100, c='black', label='Centroids'
                )

                ax.set_title('Customer Groups')
                ax.set_xlabel(selected_columns[0])
                ax.set_ylabel(selected_columns[1])
                ax.legend()

                # Display the plot
                st.pyplot(fig)

                # Option to download clustered data
                st.subheader("Download Clustered Data")
                csv = customer_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="clustered_data.csv",
                    mime="text/csv"
                )
else:
    st.info("Please upload a CSV file to proceed.")
