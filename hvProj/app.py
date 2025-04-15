#
#  app.py
#  hvProj
#
#  Created by Michael Wong on 3/3/25.
#


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from urllib.parse import quote

app = FastAPI()

API_KEY = "6070b9e2b5d2404b858ffaca7f40a819"

# API call to get property value based on address
def get_property_data(address: str) -> float:
    # URL-encode the address (to replace spaces with %20, etc.)
    encoded_address = quote(address)  # URL encode the address
    
    # Ensure the URL starts with 'https://'
    url = f'https://api.rentcast.io/v1/properties?address={encoded_address}'
    
    # Set the headers
    headers = {
        'Accept': 'application/json',
        'X-Api-Key': API_KEY
    }
    
    # Make the GET request to the RentCast API
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=404, detail="Property data not found")


# Mortgage calculation helper function
def calculate_mortgage(principal, annual_rate, years):
    monthly_rate = annual_rate / 12 / 100  # Convert to monthly rate
    months = years * 12  # Number of months
    if monthly_rate > 0:
        mortgage = (
                    principal
                    * (monthly_rate * (1 + monthly_rate) ** months)
                    / ((1 + monthly_rate) ** months - 1)
                    )
    else:
        mortgage = principal / months  # If 0% interest rate
    return mortgage


# Minimal income calculation helper function
def calculate_min_income(mortgage, tax_insurance, hoa_fees):
    # Assuming a 30% DTI ratio for housing costs
    total_monthly_cost = mortgage + tax_insurance + hoa_fees
    minimal_income = 12 * (total_monthly_cost / 0.30)
    return minimal_income


def get_latest_year(data):
    # Return the latest year based on the keys
    return max(data.keys(), key=int)

class Address(BaseModel):
    address: str

@app.post("/address")
@app.post("/address")
async def receive_address(address: Address):
    try:
        property_data = get_property_data(address.address)
#        print("DEBUG response from RentCast:", property_data)
        
        if not property_data or not isinstance(property_data, list):
            raise HTTPException(status_code=404, detail="No property data found for the given address")
        
        property_info = property_data[0]  # Safely access first result
        
        tax_assessments = property_info.get("taxAssessments", {})
        property_taxes = property_info.get("propertyTaxes", {})
        
        if not tax_assessments:
            raise KeyError("Missing 'taxAssessments' data")
        if not property_taxes:
            raise KeyError("Missing 'propertyTaxes' data")
        
        latest_year_tax_assessments = get_latest_year(tax_assessments)
        latest_year_property_taxes = get_latest_year(property_taxes)
        
        property_value = tax_assessments[latest_year_tax_assessments]["value"]
        property_tax = property_taxes[latest_year_property_taxes]["total"]
        square_footage = property_info["squareFootage"]
        hoa_fees = property_info.get("hoa", {}).get("fee", 0)

    except (KeyError, IndexError, TypeError) as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving property data: {str(e)}")
    
    # Down payment percentage and mortgage calculation
    down_payment_percentage = 0.20  # 20% down payment
    loan_amount = property_value * (1 - down_payment_percentage)  # Calculate loan amount
    loan_term_years = 30  # Loan term in years
    interest_rate = 4.0  # Annual interest rate
    mortgage_payment = calculate_mortgage(loan_amount, interest_rate, loan_term_years)
                                    
    # Minimal income calculation
    tax_and_insurance = (property_tax / 12)  # Divide yearly property tax by 12 to get monthly value
    minimal_income = calculate_min_income(mortgage_payment, tax_and_insurance, hoa_fees)
                         
    return {
        "message": "Address received successfully",
        "address": property_data[0]["formattedAddress"],  # Correctly reference the address
        "property_value": property_value,
        "monthly_mortgage_payment": mortgage_payment,
        "minimal_income_required": minimal_income,
        "square_footage": square_footage,
        "property_tax": property_tax,
        "hoa_fees": hoa_fees,
        "property_data": property_data[0],  # Return full property data for debugging
        "latest_tax_assessment_year": latest_year_tax_assessments,
        "latest_property_tax_year": latest_year_property_taxes,
    }

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Address API!"}
    
# Handling the favicon.ico request
@app.get("/favicon.ico")
async def favicon():
    return {}
