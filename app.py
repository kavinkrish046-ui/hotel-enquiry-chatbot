
import streamlit as st

st.set_page_config(
    page_title="Hotel Enquiry Chatbot",
    page_icon="🏨",
    layout="wide"
)

st.title("Hotel Enquiry Chatbot")
st.caption(
    "A hotel information assistant for rooms, prices, "
    "facilities, locations, reviews and policies."
)

# ----------------------------------------
# HOTEL CATALOGUE - FICTIONAL DEMO DATA
# ----------------------------------------

hotels = {
    "Bangalore": {
        "name": "Grand Palace Bangalore",
        "location": "MG Road, Bangalore, Karnataka",
        "airport": "Kempegowda International Airport",
        "rooms": {
            "standard": 2200,
            "deluxe": 3200,
            "premium": 4200,
            "family": 5200,
            "suite": 7000,
            "presidential": 12000
        },
        "facilities": [
            "Free Wi-Fi", "Free Parking", "Restaurant",
            "Swimming Pool", "Gym", "Breakfast", "Room Service"
        ]
    },
    "Chennai": {
        "name": "Marina Grand Hotel",
        "location": "Anna Salai, Chennai, Tamil Nadu",
        "airport": "Chennai International Airport",
        "rooms": {
            "standard": 2000,
            "deluxe": 3000,
            "premium": 4000,
            "family": 5000,
            "suite": 6800,
            "presidential": 11000
        },
        "facilities": [
            "Free Wi-Fi", "Restaurant", "Parking",
            "Gym", "Breakfast", "Laundry Service"
        ]
    },
    "Mumbai": {
        "name": "Royal Mumbai Hotel",
        "location": "Andheri West, Mumbai, Maharashtra",
        "airport": "Chhatrapati Shivaji Maharaj International Airport",
        "rooms": {
            "standard": 3000,
            "deluxe": 4500,
            "premium": 6000,
            "family": 7500,
            "suite": 10000,
            "presidential": 18000
        },
        "facilities": [
            "Free Wi-Fi", "Swimming Pool", "Gym",
            "Restaurant", "Breakfast", "Parking", "Spa"
        ]
    },
    "Goa": {
        "name": "Goa Beach Resort",
        "location": "Calangute, Goa",
        "airport": "Manohar International Airport",
        "rooms": {
            "standard": 2500,
            "deluxe": 4000,
            "premium": 5500,
            "family": 7000,
            "suite": 9500,
            "presidential": 16000
        },
        "facilities": [
            "Beach Access", "Free Wi-Fi", "Swimming Pool",
            "Restaurant", "Breakfast", "Parking", "Spa"
        ]
    },
    "Hyderabad": {
        "name": "Deccan Grand Hotel",
        "location": "Banjara Hills, Hyderabad, Telangana",
        "airport": "Rajiv Gandhi International Airport",
        "rooms": {
            "standard": 1900,
            "deluxe": 2900,
            "premium": 3900,
            "family": 4900,
            "suite": 6500,
            "presidential": 10000
        },
        "facilities": [
            "Free Wi-Fi", "Breakfast", "Restaurant",
            "Parking", "Gym", "Room Service"
        ]
    }
}

# ----------------------------------------
# SAMPLE CUSTOMER REVIEWS
# ----------------------------------------

reviews = {
    "Bangalore": [
        "Excellent service and a comfortable room.",
        "The food was good but the room was noisy."
    ],
    "Chennai": [
        "Amazing staff and clean rooms.",
        "The experience was disappointing."
    ],
    "Mumbai": [
        "Great facilities and excellent hospitality.",
        "The room was expensive and disappointing."
    ],
    "Goa": [
        "Beautiful location and fantastic beach access.",
        "The stay was enjoyable and relaxing."
    ],
    "Hyderabad": [
        "Good food and helpful staff.",
        "The service was slow."
    ]
}

# ----------------------------------------
# INTENT DETECTION
# ----------------------------------------

def detect_intent(message):
    text = message.lower().strip()

    if any(x in text for x in [
        "hello", "hi", "hey", "good morning", "good evening"
    ]):
        return "GREETING"

    if any(x in text for x in [
        "bye", "goodbye", "exit", "quit"
    ]):
        return "GOODBYE"

    if any(x in text for x in [
        "review", "reviews", "sentiment", "customer feedback"
    ]):
        return "REVIEW"

    if any(x in text for x in [
        "cancel", "cancellation", "refund"
    ]):
        return "CANCELLATION"

    if any(x in text for x in [
        "check in", "check-in", "check out", "check-out",
        "checkout", "early check", "late check"
    ]):
        return "CHECK_IN"

    if any(x in text for x in [
        "facility", "facilities", "amenities", "wifi", "wi-fi",
        "parking", "breakfast", "pool", "gym", "restaurant",
        "spa", "beach", "room service"
    ]):
        return "FACILITIES"

    if any(x in text for x in [
        "location", "address", "where", "located",
        "airport", "near"
    ]):
        return "LOCATION"

    if any(x in text for x in [
        "price", "prices", "cost", "rate", "tariff",
        "how much", "budget", "under", "below", "cheap"
    ]):
        return "PRICE"

    if any(x in text for x in [
        "room", "rooms", "stay", "accommodation",
        "book a room"
    ]):
        return "ROOM_SEARCH"

    return "UNKNOWN"


# ----------------------------------------
# ENTITY EXTRACTION
# ----------------------------------------

def extract_entities(message):
    text = message.lower()
    entities = {}

    city_aliases = {
        "bangalore": "Bangalore",
        "bengaluru": "Bangalore",
        "chennai": "Chennai",
        "madras": "Chennai",
        "mumbai": "Mumbai",
        "bombay": "Mumbai",
        "goa": "Goa",
        "hyderabad": "Hyderabad"
    }

    for alias, city in city_aliases.items():
        if alias in text:
            entities["Hotel"] = city
            entities["Location"] = city
            break

    for room in [
        "presidential", "standard", "deluxe",
        "premium", "family", "suite"
    ]:
        if room in text:
            entities["Room Type"] = room
            break

    facility_names = [
        "free wi-fi", "wifi", "wi-fi", "parking",
        "breakfast", "swimming pool", "pool", "gym",
        "restaurant", "spa", "beach access", "room service"
    ]

    for facility in facility_names:
        if facility in text:
            entities["Facility"] = facility
            break

    words = text.replace(",", " ").split()

    for i, word in enumerate(words):
        if word.isdigit():
            entities["Price"] = int(word)

        if word in ["under", "below"] and i + 1 < len(words):
            if words[i + 1].isdigit():
                entities["Price"] = int(words[i + 1])

    return entities


# ----------------------------------------
# SENTIMENT ANALYSIS
# ----------------------------------------

def analyze_sentiment(review):
    positive_words = [
        "excellent", "amazing", "great", "good",
        "comfortable", "clean", "beautiful",
        "fantastic", "enjoyable", "helpful",
        "relaxing", "friendly"
    ]

    negative_words = [
        "bad", "poor", "noisy", "disappointing",
        "slow", "dirty", "expensive", "terrible"
    ]

    words = review.lower().replace(".", "").replace(",", "").split()

    positive = sum(word in positive_words for word in words)
    negative = sum(word in negative_words for word in words)

    if positive > negative:
        return "Positive"
    if negative > positive:
        return "Negative"
    return "Neutral"


# ----------------------------------------
# REVIEW REPORT
# ----------------------------------------

def get_review_report(city):
    result = f"Sample customer reviews for {hotels[city]['name']}:\n\n"

    for review in reviews[city]:
        result += (
            f"- {review}\n"
            f"  Sentiment: {analyze_sentiment(review)}\n\n"
        )

    result += (
        "Note: These are sample reviews for academic demonstration, "
        "not verified real customer feedback."
    )

    return result


# ----------------------------------------
# CHATBOT RESPONSE
# ----------------------------------------

def chatbot_response(message, context):
    intent = detect_intent(message)
    entities = extract_entities(message)

    context.update(entities)

    if intent == "GREETING":
        return (
            "Hello! Welcome to the Hotel Enquiry Chatbot.\n\n"
            "Ask me about rooms, prices, facilities, location, "
            "check-in, cancellation or customer reviews."
        )

    if intent == "GOODBYE":
        return "Thank you for visiting. Have a wonderful day!"

    if intent == "CANCELLATION":
        return (
            "Sample cancellation policy:\n"
            "- More than 48 hours before check-in: full refund\n"
            "- 24–48 hours before check-in: 50% refund\n"
            "- Less than 24 hours before check-in: no refund\n\n"
            "This is demonstration data; actual policies may differ."
        )

    if intent == "CHECK_IN":
        return (
            "Sample hotel timings:\n"
            "- Check-in: 2:00 PM\n"
            "- Check-out: 12:00 PM\n"
            "- Early check-in and late check-out are subject to availability."
        )

    if intent == "UNKNOWN" and not entities:
        return (
            "I can help with rooms, prices, facilities, locations, "
            "check-in, cancellation and reviews. "
            "Which city are you interested in?"
        )

    city = context.get("Hotel")

    if not city:
        return (
            "Which city are you interested in? "
            "Choose Bangalore, Chennai, Mumbai, Goa or Hyderabad."
        )

    hotel = hotels[city]
    room_type = context.get("Room Type")

    if intent == "LOCATION":
        return (
            f"{hotel['name']}\n"
            f"Location: {hotel['location']}\n"
            f"Airport: {hotel['airport']}"
        )

    if intent == "FACILITIES":
        facility = context.get("Facility")

        if facility:
            facility_aliases = {
                "wifi": "Free Wi-Fi",
                "wi-fi": "Free Wi-Fi",
                "parking": "Free Parking",
                "pool": "Swimming Pool"
            }
            requested = facility_aliases.get(facility, facility.title())

            matches = [
                item for item in hotel["facilities"]
                if requested.lower() in item.lower()
            ]

            if matches:
                return f"Yes, {hotel['name']} lists {matches[0]}."
            return (
                f"{hotel['name']} does not list {requested} "
                "among its sample facilities."
            )

        return "Facilities:\n- " + "\n- ".join(hotel["facilities"])

    if intent == "REVIEW":
        return get_review_report(city)

    if intent == "PRICE":
        max_price = context.get("Price")

        if room_type:
            price = hotel["rooms"][room_type]

            if max_price is not None and price > max_price:
                return (
                    f"The {room_type.title()} Room costs ₹{price} per night, "
                    f"which is above your ₹{max_price} budget."
                )

            return (
                f"The {room_type.title()} Room at {hotel['name']} "
                f"costs ₹{price} per night."
            )

        room_prices = hotel["rooms"]

        if max_price is not None:
            room_prices = {
                name: price for name, price in room_prices.items()
                if price <= max_price
            }

        if not room_prices:
            return "No room types match that budget at this hotel."

        result = f"Room prices at {hotel['name']}:\n\n"

        for name, price in room_prices.items():
            result += f"- {name.title()}: ₹{price} per night\n"

        return result

    if intent == "ROOM_SEARCH":
        rooms = hotel["rooms"]

        if room_type:
            price = rooms[room_type]
            return (
                f"{hotel['name']} offers a {room_type.title()} Room "
                f"for ₹{price} per night."
            )

        return (
            f"Rooms at {hotel['name']}:\n\n"
            + "\n".join(
                f"- {name.title()}: ₹{price} per night"
                for name, price in rooms.items()
            )
            + "\n\nTell me your preferred room type or budget."
        )

    if intent == "UNKNOWN" and entities.get("Facility"):
        return "Please ask about facilities and specify the city."

    return (
        f"You selected {hotel['name']} in {city}. "
        "You can ask about its rooms, prices, facilities, location, "
        "check-in, cancellation or reviews."
    )


# ----------------------------------------
# STREAMLIT CHAT INTERFACE
# ----------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "context" not in st.session_state:
    st.session_state.context = {}

with st.sidebar:
    st.subheader("Hotel Catalogue")

    for city, hotel in hotels.items():
        st.markdown(f"**{hotel['name']}**")
        st.caption(hotel["location"])

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.context = {}
        st.rerun()

st.info(
    "Try: 'I need a deluxe room in Goa', "
    "'What is the price?', 'What facilities are available?', "
    "or 'Show customer reviews'."
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask a hotel enquiry...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    response = chatbot_response(
        user_input,
        st.session_state.context
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    st.rerun()
