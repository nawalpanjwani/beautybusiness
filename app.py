from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)
dataset = pd.read_csv("beauty_data.csv")  # Ensure the dataset is loaded with correct column names

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    city = req.get("queryResult").get("parameters").get("city")
    service = req.get("queryResult").get("parameters").get("service")
    page = req.get("queryResult").get("parameters").get("page", 1)
    results_per_page = 5  # Number of results per page

    formatted_service = f"service_{service.lower().replace(' ', '_')}"

    # Ensure the column exists to prevent KeyError
    if formatted_service not in dataset.columns:
        response = {"fulfillmentText": f"Sorry, we don't have data for {service} in our system."}
        return jsonify(response)

    # Filter the dataset based on city and service
    filtered_data = dataset[
        (dataset["city"].str.contains(city, case=False)) &
        (dataset[formatted_service] == True)
    ]

    # Paginate results
    total_results = len(filtered_data)
    if total_results > 0:
        start_index = (page - 1) * results_per_page
        end_index = start_index + results_per_page
        paginated_data = filtered_data.iloc[start_index:end_index]
        
        # Format the response
        details = '\n'.join([f"{idx + 1 + start_index}. {row['name']}, located at {row['address']}, {row['city']}, {row['state']} {row['postal_code']}. Services: {row['categories']}." 
                             for idx, row in paginated_data.iterrows()])
        more_text = " Type 'more' to see additional results." if end_index < total_results else ""
        response_text = f"Here are your beauty business results for {service} in {city}:\n{details}{more_text}"
    else:
        response_text = f"No results found for {service} in {city}."

    response = {"fulfillmentText": response_text}
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)

