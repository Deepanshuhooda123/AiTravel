import streamlit as st
import google.generativeai as genai
import urllib.parse
from typing import Dict, List

# Configure API key (Note: Use st.secrets for API keys in production)
GEMINI_API_KEY = "AIzaSyDpEGGhkNIWIQfdBk18jJzW6QfsZyy27nE"  # Replace with your valid API key

def get_gemini_response(prompt: str) -> str:
    """Get response from Gemini AI model."""
    try:
        genai.configure(api_key=GEMINI_API_KEY)

        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        response = model.generate_content(prompt)
        return response.text if response and hasattr(response, 'text') else "❗ No valid response."
    except Exception as e:
        return f"❗ Error: {str(e)}"


def get_maps_link(place: str, city: str) -> str:
    """Generate Google Maps link for a place in a city."""
    query = urllib.parse.quote(f"{place}, {city}")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def get_city_description(city: str) -> str:
    """Get city description using Gemini API"""
    prompt = f"Provide a concise 3-sentence description of {city}, focusing on its history, geography, and cultural significance."
    return get_gemini_response(prompt)


def get_travel_info_gemini(city: str) -> Dict[str, List[str]]:
    """Get structured travel info from Gemini AI."""
    prompt = f"""Provide structured travel details for {city} with the following sections:
    🏛 Famous Places
    - (List three famous places)
    🍽 Popular Foods
    - (List three popular local foods)
    🛍 Best Malls
    - (List three best shopping malls)
    🍴 Recommended Restaurants
    - (List three recommended restaurants)

    Format exactly like this example for Paris:
    🏛 Famous Places
    - Eiffel Tower
    - Louvre Museum
    - Notre-Dame Cathedral
    🍽 Popular Foods
    - Croissant
    - Coq au Vin
    - Ratatouille
    🛍 Best Malls
    - Galeries Lafayette
    - Printemps Haussmann
    - Westfield Les 4 Temps
    🍴 Recommended Restaurants
    - Le Jules Verne
    - L'Ambroisie
    - Chez L'Ami Jean"""

    response = get_gemini_response(prompt)
    return parse_travel_details(response)


def parse_travel_details(details: str) -> Dict[str, List[str]]:
    """Parse the raw travel details into structured sections."""
    sections = {
        "🏛 Famous Places": [],
        "🍽 Popular Foods": [],
        "🛍 Best Malls": [],
        "🍴 Recommended Restaurants": []
    }
    
    current_section = None
    
    for line in details.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        # Check for section headers
        if any(section in line for section in sections):
            for section in sections:
                if section in line:
                    current_section = section
                    break
        elif current_section and line.startswith(('-', '•')):
            item = line.lstrip('-• ').strip()
            if item:  # Only add non-empty items
                sections[current_section].append(item)
    
    return sections


# Streamlit UI
def main():
    st.set_page_config(page_title="AI Travel Guide", page_icon="🌍")
    
    # Add some CSS styling
    st.markdown("""
    <style>
    .section-header {
        font-size: 1.2em;
        font-weight: bold;
        margin-top: 1em;
        margin-bottom: 0.5em;
        color: #2c3e50;
    }
    .description {
        margin-bottom: 1.5em;
        line-height: 1.6;
    }
    .item {
        margin-bottom: 0.5em;
        line-height: 1.5;
    }
    .map-link {
        color: #4285F4;
        text-decoration: none;
        font-size: 0.9em;
    }
    .map-link:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌍 AI Travel Guide")
    
    city = st.text_input("Enter a city name:", key="city_input").strip()
    
    if city:
        city_title = city.title()
        st.markdown(
            f"<div class='section-header'>🌐 Explore {city_title} on "
            f"<a class='map-link' href='{get_maps_link(city_title, '')}' target='_blank'>Google Maps</a></div>",
            unsafe_allow_html=True
        )

        if st.button("Get Travel Information", key="get_info_btn"):
            with st.spinner("Fetching travel information..."):
                st.subheader(f"📍 About {city_title}")

                # Get city description
                description = get_city_description(city)
                st.markdown(f"<div class='description'>{description}</div>", unsafe_allow_html=True)

                # Get structured travel details
                try:
                    sections = get_travel_info_gemini(city)
                    
                    for title, items in sections.items():
                        st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
                        if items:
                            for item in items:
                                link = get_maps_link(item, city)
                                st.markdown(
                                    f"<div class='item'>🔹 <b>{item}</b> | "
                                    f"<a class='map-link' href='{link}' target='_blank'>Open in Google Maps</a></div>",
                                    unsafe_allow_html=True
                                )
                        else:
                            st.markdown("<div class='item'>🔹 <i>Information not available</i></div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❗ Error fetching travel information: {str(e)}")
    else:
        st.warning("⚠ Please enter a city name.")


if __name__ == "__main__":
    main()
