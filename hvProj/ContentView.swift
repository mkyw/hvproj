//  ContentView.swift
//  hvProj
//
//  Created by Michael Wong on 2/26/25.
//

import SwiftUI
import Combine
import CoreLocation
import MapKit

struct ContentView: View {
    @StateObject private var mapSearch = MapSearch()
    
    func reverseGeo(location: MKLocalSearchCompletion) {
        let searchRequest = MKLocalSearch.Request(completion: location)
        let search = MKLocalSearch(request: searchRequest)
        var coordinateK : CLLocationCoordinate2D?
        search.start { (response, error) in
            if error == nil, let coordinate = response?.mapItems.first?.placemark.coordinate {
                coordinateK = coordinate
            }
            
            if let c = coordinateK {
                let location = CLLocation(latitude: c.latitude, longitude: c.longitude)
                CLGeocoder().reverseGeocodeLocation(location) { placemarks, error in
                    
                    guard let placemark = placemarks?.first else {
                        let errorString = error?.localizedDescription ?? "Unexpected Error"
                        print("Unable to reverse geocode the given location. Error: \(errorString)")
                        return
                    }
                    
                    let reversedGeoLocation = ReversedGeoLocation(with: placemark)
                    
                    address = "\(reversedGeoLocation.streetNumber) \(reversedGeoLocation.streetName), \(reversedGeoLocation.city), \(reversedGeoLocation.state), \(reversedGeoLocation.zipCode)"
                    mapSearch.searchTerm = address
                    isFocused = false
                    
                }
            }
        }
    }
    
    //  Function to send the address to the backend
    func sendAddressToBackend(address: String) {
        guard let url = URL(string: "http://localhost:8000/address") else {
            print("Invalid URL")
            return
        }
        
        // Create URLRequest
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Create a dictionary to send as JSON
        let addressData = ["address": address]
        
        // Convert the dictionary to JSON
        do {
            let jsonData = try JSONSerialization.data(withJSONObject: addressData, options: [])
            request.httpBody = jsonData
        } catch {
            print("Error serializing address data: \(error)")
            return
        }
        
        // Send the request using URLSession
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error: \(error)")
                return
            }
            
            if let data = data, let responseString = String(data: data, encoding: .utf8) {
                DispatchQueue.main.async {
                    print("Response: \(responseString)") // Update UI with response or handle it as needed
                }
            }
        }
        task.resume()
    }
    
    // Form Variables
    
    @FocusState private var isFocused: Bool
    
    @State private var btnHover = false
    @State private var isBtnActive = false
    
    @State private var address = ""
    @State private var city = ""
    @State private var state = ""
    @State private var zip = ""
    
    // Main UI
    
    var body: some View {
        
        VStack {
            // TextField for address input
            TextField("Search Address", text: $mapSearch.searchTerm)
                .padding()
                .textFieldStyle(RoundedBorderTextFieldStyle())
            
            // Show auto-complete results
            if !mapSearch.searchTerm.isEmpty && address != mapSearch.searchTerm && isFocused == false {
                ForEach(mapSearch.locationResults, id: \.self) { location in
                    Button {
                        reverseGeo(location: location)
                    } label: {
                        VStack(alignment: .leading) {
                            Text(location.title)
                            Text(location.subtitle)
                                .font(.system(.caption))
                        }
                    } // End Label
                } // End ForEach
            } // End if
            // End show auto-complete
            
            
            // Button to trigger sending the address to the backend
            Button("Enter") {
                sendAddressToBackend(address: address)
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
        }
        .padding()
        
    } // End Var Body
    
} // End Struct

struct Test_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
