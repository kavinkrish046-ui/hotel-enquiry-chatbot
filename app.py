import re
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(
    page_title="Hotel Enquiry Chatbot",
    page_icon="🏨",
    layout="wide",
)

# ----------------------------------------
# HOTEL CATALOGUE - FICTIONAL DEMO DATA
# ----------------------------------------

hotels = {
    "Bangalore": {
        "name": "Grand Palace Bangalore",
        "location": "MG Road, Bangalore, Karnataka",
        "airport": "Kempegowda International Airport",
        "colors": ((30, 60, 114), (42, 82, 152)),
        "rooms": {"standard": 2200, "deluxe": 3200, "premium": 4200,
                  "family": 5200, "suite": 7000, "presidential": 12000},
        "facilities": ["Free Wi-Fi", "Free Parking", "Restaurant",
                       "Swimming Pool", "Gym", "Breakfast", "Room Service"],
    },
    "Chennai": {
        "name": "Marina Grand Hotel",
        "location": "Anna Salai, Chennai, Tamil Nadu",
        "airport": "Chennai International Airport",
        "colors": ((0, 105, 148), (0, 168, 150)),
        "rooms": {"standard": 2000, "deluxe": 3000, "premium": 4000,
                  "family": 5000, "suite": 6800, "presidential": 11000},
        "facilities": ["Free Wi-Fi", "Restaurant", "Parking",
                       "Gym", "Breakfast", "Laundry Service"],
    },
    "Mumbai": {
        "name": "Royal Mumbai Hotel",
        "location": "Andheri West, Mumbai, Maharashtra",
        "airport": "Chhatrapati Shivaji Maharaj International Airport",
        "colors": ((106, 17, 203), (37, 117, 252)),
        "rooms": {"standard": 3000, "deluxe": 4500, "premium": 6000,
                  "family": 7500, "suite": 10000, "presidential": 18000},
        "facilities": ["Free Wi-Fi", "Swimming Pool", "Gym",
                       "Restaurant", "Breakfast", "Parking", "Spa"],
    },
    "Goa": {
        "name": "Goa Beach Resort",
        "location": "Calangute, Goa",
        "airport": "Manohar International Airport",
        "colors": ((255, 126, 95), (254, 180, 123)),
        "rooms": {"standard": 2500, "deluxe": 4000, "premium": 5500,
                  "family": 7000, "suite": 9500, "presidential": 16000},
        "facilities": ["Beach Access", "Free Wi-Fi", "Swimming Pool",
                       "Restaurant", "Breakfast", "Parking", "Spa"],
    },
    "Hyderabad": {
        "name": "Deccan Grand Hotel",
        "location": "Banjara Hills, Hyderabad, Telangana",
        "airport": "Rajiv Gandhi International Airport",
        "colors": ((120, 40, 60), (200, 90, 80)),
        "rooms": {"standard": 1900, "deluxe": 2900, "premium": 3900,
                  "family": 4900, "suite": 6500, "presidential": 10000},
        "facilities": ["Free Wi-Fi", "Breakfast", "Restaurant",
                       "Parking", "Gym", "Room Service"],
    },
}

ROOM_TYPES = ["standard", "deluxe", "premium", "family", "suite", "presidential"]

# ----------------------------------------
# SAMPLE CUSTOMER REVIEWS
# ----------------------------------------

reviews = {
    "Bangalore": ["Excellent service and a comfortable room.",
                  "The food was good but the room was noisy."],
    "Chennai": ["Amazing staff and clean rooms.",
                "The experience was disappointing."],
    "Mumbai": ["Great facilities and excellent hospitality.",
               "The room was expensive and disappointing."],
    "Goa": ["Beautiful location and fantastic beach access.",
            "The stay was enjoyable and relaxing."],
    "Hyderabad": ["Good food and helpful staff.",
                  "The service was slow."],
}

# ----------------------------------------
# IMAGE GENERATION (no internet needed)
# ----------------------------------------


def _font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


@st.cache_data(show_spinner=False)
def make_banner(title, subtitle, c1, c2, width=1200, height=320, icons=True):
    """Draws a gradient banner with a simple skyline and text."""
    img = Image.new("RGB", (width, height))
    px = img.load()
    for y in range(height):
        for x in range(width):
            t = (x / width * 0.6) + (y / height * 0.4)
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

    d = ImageDraw.Draw(img, "RGBA")

    # skyline of buildings
    if icons:
        x = 0
        seed = sum(ord(ch) for ch in title)
        while x < width:
            seed = (seed * 1103515245 + 12345) % (2 ** 31)
            w = 50 + seed % 60
            h = 70 + (seed // 7) % 130
            d.rectangle([x, height - h, x + w, height], fill=(0, 0, 0, 70))
            for wy in range(height - h + 12, height - 10, 22):
                for wx in range(x + 10, x + w - 10, 18):
                    if (wx + wy + seed) % 3:
                        d.rectangle([wx, wy, wx + 7, wy + 10],
                                    fill=(255, 235, 150, 190))
            x += w + 6

    d.text((40, 50), title, font=_font(58), fill=(255, 255, 255, 255))
    d.text((42, 125), subtitle, font=_font(28), fill=(255, 255, 255, 220))
    return img


# ----------------------------------------
# INTENT DETECTION
# ----------------------------------------


def has_word(text, words):
    return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)


def detect_intent(message):
    text = message.lower().strip()

    if has_word(text, ["hello", "hi", "hey", "good morning", "good evening"]):
        return "GREETING"
    if has_word(text, ["bye", "goodbye", "exit", "quit"]):
        return "GOODBYE"
    if has_word(text, ["review", "reviews", "sentiment", "feedback"]):
        return "REVIEW"
    if has_word(text, ["cancel", "cancellation", "refund"]):
        return "CANCELLATION"
    if has_word(text, ["check in", "check-in", "check out", "check-out",
                       "checkout", "early check", "late check"]):
        return "CHECK_IN"
    if has_word(text, ["facility", "facilities", "amenities", "wifi", "wi-fi",
                       "parking", "breakfast", "pool", "gym", "restaurant",
                       "spa", "beach", "room service"]):
        return "FACILITIES"
    if has_word(text, ["location", "address", "where", "located",
                       "airport", "near"]):
        return "LOCATION"
    if has_word(text, ["price", "prices", "cost", "rate", "tariff",
                       "how much", "budget", "under", "below", "cheap"]):
        return "PRICE"
    if has_word(text, ["room", "rooms", "stay", "accommodation", "book"]):
        return "ROOM_SEARCH"
    return "UNKNOWN"


# ----------------------------------------
# ENTITY EXTRACTION
# ----------------------------------------


def extract_entities(message):
    text = message.lower()
    entities = {}

    city_aliases = {
        "bangalore": "Bangalore", "bengaluru": "Bangalore",
        "chennai": "Chennai", "madras": "Chennai",
        "mumbai": "Mumbai", "bombay": "Mumbai",
        "goa": "Goa", "hyderabad": "Hyderabad",
    }
    for alias, city in city_aliases.items():
        if alias in text:
            entities["Hotel"] = city
            break

    for room in ["presidential", "standard", "deluxe", "premium", "family", "suite"]:
        if room in text:
            entities["Room Type"] = room
            break

    for facility in ["free wi-fi", "wifi", "wi-fi", "parking", "breakfast",
                     "swimming pool", "pool", "gym", "restaurant", "spa",
                     "beach access", "room service"]:
        if facility in text:
            entities["Facility"] = facility
            break

    # Budget only when it is clearly a price: "under 4000", "below ₹5,000", "budget 3500"
    m = re.search(r"(?:under|below|budget(?: of)?|within|max)\s*(?:rs\.?|inr|₹)?\s*([\d,]+)", text)
    if not m:
        m = re.search(r"(?:₹|rs\.?|inr)\s*([\d,]+)", text)
    if m:
        digits = m.group(1).replace(",", "")
        if digits.isdigit():
            entities["Price"] = int(digits)

    return entities


# ----------------------------------------
# SENTIMENT ANALYSIS
# ----------------------------------------


def analyze_sentiment(review):
    positive_words = ["excellent", "amazing", "great", "good", "comfortable",
                      "clean", "beautiful", "fantastic", "enjoyable",
                      "helpful", "relaxing", "friendly"]
    negative_words = ["bad", "poor", "noisy", "disappointing",
                      "slow", "dirty", "expensive", "terrible"]

    words = re.findall(r"[a-z]+", review.lower())
    positive = sum(w in positive_words for w in words)
    negative = sum(w in negative_words for w in words)

    if positive > negative:
        return "Positive"
    if negative > positive:
        return "Negative"
    return "Neutral"


def get_review_report(city):
    result = f"Sample customer reviews for {hotels[city]['name']}:\n\n"
    for review in reviews[city]:
        result += f"- {review}\n  Sentiment: {analyze_sentiment(review)}\n\n"
    result += ("Note: These are sample reviews for academic demonstration, "
               "not verified real customer feedback.")
    return result


# ----------------------------------------
# CHATBOT RESPONSE
# ----------------------------------------


def chatbot_response(message, context):
    intent = detect_intent(message)
    entities = extract_entities(message)
    context.update(entities)

    if intent == "GREETING":
        return ("Hello! Welcome to the Hotel Enquiry Chatbot.\n\n"
                "Ask me about rooms, prices, facilities, location, "
                "check-in, cancellation or customer reviews.")

    if intent == "GOODBYE":
        return "Thank you for visiting. Have a wonderful day!"

    if intent == "CANCELLATION":
        return ("Sample cancellation policy:\n"
                "- More than 48 hours before check-in: full refund\n"
                "- 24–48 hours before check-in: 50% refund\n"
                "- Less than 24 hours before check-in: no refund\n\n"
                "This is demonstration data; actual policies may differ.")

    if intent == "CHECK_IN":
        return ("Sample hotel timings:\n"
                "- Check-in: 2:00 PM\n"
                "- Check-out: 12:00 PM\n"
                "- Early check-in and late check-out are subject to availability.")

    if intent == "UNKNOWN" and not entities:
        return ("I can help with rooms, prices, facilities, locations, "
                "check-in, cancellation and reviews. "
                "Which city are you interested in?")

    city = context.get("Hotel")
    if not city:
        return ("Which city are you interested in? "
                "Choose Bangalore, Chennai, Mumbai, Goa or Hyderabad.")

    hotel = hotels[city]
    room_type = context.get("Room Type")

    if intent == "LOCATION":
        return (f"{hotel['name']}\nLocation: {hotel['location']}\n"
                f"Airport: {hotel['airport']}")

    if intent == "FACILITIES":
        facility = context.get("Facility")
        if facility:
            aliases = {"wifi": "wi-fi", "free wi-fi": "wi-fi",
                       "pool": "swimming pool"}
            requested = aliases.get(facility, facility)
            matches = [f for f in hotel["facilities"]
                       if requested.lower() in f.lower()]
            if matches:
                return f"Yes, {hotel['name']} lists {matches[0]}."
            return (f"{hotel['name']} does not list {requested.title()} "
                    "among its sample facilities.")
        return "Facilities:\n- " + "\n- ".join(hotel["facilities"])

    if intent == "REVIEW":
        return get_review_report(city)

    if intent == "PRICE":
        max_price = context.get("Price")

        if room_type:
            price = hotel["rooms"][room_type]
            if max_price is not None and price > max_price:
                return (f"The {room_type.title()} Room costs ₹{price:,} per night, "
                        f"which is above your ₹{max_price:,} budget.")
            return (f"The {room_type.title()} Room at {hotel['name']} "
                    f"costs ₹{price:,} per night.")

        room_prices = hotel["rooms"]
        if max_price is not None:
            room_prices = {n: p for n, p in room_prices.items() if p <= max_price}
        if not room_prices:
            return "No room types match that budget at this hotel."

        result = f"Room prices at {hotel['name']}:\n\n"
        for name, price in room_prices.items():
            result += f"- {name.title()}: ₹{price:,} per night\n"
        return result

    if intent == "ROOM_SEARCH":
        rooms = hotel["rooms"]
        if room_type:
            return (f"{hotel['name']} offers a {room_type.title()} Room "
                    f"for ₹{rooms[room_type]:,} per night.")
        return (f"Rooms at {hotel['name']}:\n\n"
                + "\n".join(f"- {n.title()}: ₹{p:,} per night"
                            for n, p in rooms.items())
                + "\n\nTell me your preferred room type or budget.")

    return (f"You selected {hotel['name']} in {city}. "
            "You can ask about its rooms, prices, facilities, location, "
            "check-in, cancellation or reviews.")


# ----------------------------------------
# SESSION STATE
# ----------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = {}
if "enquiries" not in st.session_state:
    st.session_state.enquiries = []

# ----------------------------------------
# SIDEBAR – INPUT BOXES / FILTERS
# ----------------------------------------

with st.sidebar:
    st.header("🔎 Search Filters")

    sel_city = st.selectbox("City", ["Any"] + list(hotels.keys()))
    sel_room = st.selectbox("Room type", ["Any"] + [r.title() for r in ROOM_TYPES])
    max_budget = st.slider("Max budget per night (₹)", 1500, 20000, 8000, step=500)
    sel_facilities = st.multiselect(
        "Must-have facilities",
        sorted({f for h in hotels.values() for f in h["facilities"]}),
    )

    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.context = {}
        st.rerun()

    with st.expander("Chat context (debug)"):
        st.json(st.session_state.context)

# Sync the sidebar city into the chatbot context so chat follows the filter
if sel_city != "Any":
    st.session_state.context["Hotel"] = sel_city
if sel_room != "Any":
    st.session_state.context["Room Type"] = sel_room.lower()

# ----------------------------------------
# HEADER
# ----------------------------------------

st.image(
    make_banner("Hotel Enquiry Chatbot",
                "Rooms • Prices • Facilities • Locations • Reviews • Policies",
                (30, 60, 114), (106, 17, 203)),
    use_container_width=True,
)

st.caption("A demo hotel information assistant. All data is fictional.")

k1, k2, k3, k4 = st.columns(4)
all_prices = [p for h in hotels.values() for p in h["rooms"].values()]
k1.metric("Hotels", len(hotels))
k2.metric("Room types", len(ROOM_TYPES))
k3.metric("Cheapest room", f"₹{min(all_prices):,}")
k4.metric("Most premium", f"₹{max(all_prices):,}")

tab_chat, tab_explore, tab_calc, tab_enquiry, tab_about = st.tabs(
    ["💬 Chat", "🏨 Explore Hotels", "🧮 Price Calculator",
     "📝 Enquiry Form", "ℹ️ About"]
)

# ----------------------------------------
# TAB 1 – CHAT
# ----------------------------------------

with tab_chat:
    st.info("Try: 'I need a deluxe room in Goa', 'What is the price?', "
            "'Does it have a pool?', 'Rooms under 4000 in Chennai', "
            "or 'Show customer reviews'.")

    qcols = st.columns(4)
    quick = {
        "💰 Prices": "What is the price?",
        "🏊 Facilities": "What facilities are available?",
        "📍 Location": "Where is it located?",
        "⭐ Reviews": "Show customer reviews",
    }
    clicked = None
    for col, (label, text) in zip(qcols, quick.items()):
        if col.button(label, use_container_width=True):
            clicked = text

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask a hotel enquiry...") or clicked

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = chatbot_response(user_input, st.session_state.context)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# ----------------------------------------
# TAB 2 – EXPLORE HOTELS (dynamic, filter driven)
# ----------------------------------------

with tab_explore:
    matches = []
    for city, h in hotels.items():
        if sel_city != "Any" and city != sel_city:
            continue
        if any(f not in h["facilities"] for f in sel_facilities):
            continue
        if sel_room != "Any":
            price = h["rooms"][sel_room.lower()]
            if price > max_budget:
                continue
        elif min(h["rooms"].values()) > max_budget:
            continue
        matches.append(city)

    st.subheader(f"{len(matches)} hotel(s) match your filters")

    if not matches:
        st.warning("No hotels match. Try increasing the budget or removing filters.")

    for city in matches:
        h = hotels[city]
        c_img, c_info = st.columns([1, 2])
        with c_img:
            st.image(make_banner(h["name"], city, h["colors"][0], h["colors"][1],
                                 width=700, height=260, icons=True),
                     use_container_width=True)
        with c_info:
            st.markdown(f"### {h['name']}")
            st.write(f"📍 {h['location']}")
            st.write(f"✈️ {h['airport']}")
            st.write("**Facilities:** " + ", ".join(h["facilities"]))

            affordable = {n.title(): p for n, p in h["rooms"].items()
                          if p <= max_budget}
            if affordable:
                st.write("**Rooms within budget:** " + " | ".join(
                    f"{n} ₹{p:,}" for n, p in affordable.items()))

            sentiments = [analyze_sentiment(r) for r in reviews[city]]
            st.write(f"**Review sentiment:** {', '.join(sentiments)}")
        st.divider()

    st.subheader("Price comparison")
    df = pd.DataFrame(
        {city: hotels[city]["rooms"] for city in hotels}
    )
    df.index = [i.title() for i in df.index]
    shown = df[matches] if matches else df
    st.bar_chart(shown)
    st.dataframe(shown.style.format("₹{:,}"), use_container_width=True)

# ----------------------------------------
# TAB 3 – PRICE CALCULATOR
# ----------------------------------------

with tab_calc:
    st.subheader("Estimate your stay")

    c1, c2, c3 = st.columns(3)
    calc_city = c1.selectbox("Hotel city", list(hotels.keys()), key="calc_city")
    calc_room = c2.selectbox("Room type", [r.title() for r in ROOM_TYPES],
                             key="calc_room")
    rooms_count = c3.number_input("Number of rooms", 1, 10, 1)

    d1, d2, d3 = st.columns(3)
    checkin = d1.date_input("Check-in", date.today() + timedelta(days=7))
    checkout = d2.date_input("Check-out", date.today() + timedelta(days=9))
    guests = d3.number_input("Guests", 1, 20, 2)

    include_breakfast = st.checkbox("Add breakfast (₹400 per guest per night)")

    nights = (checkout - checkin).days
    if nights <= 0:
        st.error("Check-out must be after check-in.")
    else:
        rate = hotels[calc_city]["rooms"][calc_room.lower()]
        room_total = rate * nights * rooms_count
        breakfast_total = 400 * guests * nights if include_breakfast else 0
        subtotal = room_total + breakfast_total
        tax = round(subtotal * 0.12)
        total = subtotal + tax

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Nights", nights)
        m2.metric("Room charges", f"₹{room_total:,}")
        m3.metric("GST (12%)", f"₹{tax:,}")
        m4.metric("Total", f"₹{total:,}")

        if guests > rooms_count * 3:
            st.warning("That's a lot of guests for the rooms selected — "
                       "consider adding another room or a Family room.")

# ----------------------------------------
# TAB 4 – ENQUIRY FORM
# ----------------------------------------

with tab_enquiry:
    st.subheader("Send an enquiry")
    st.caption("Demo form — nothing is sent anywhere; entries are kept in this session only.")

    with st.form("enquiry_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        name = f1.text_input("Full name")
        email = f2.text_input("Email")
        phone = f1.text_input("Phone number")
        e_city = f2.selectbox("Preferred city", list(hotels.keys()))
        e_room = f1.selectbox("Room type", [r.title() for r in ROOM_TYPES])
        e_date = f2.date_input("Planned check-in", date.today() + timedelta(days=14))
        message = st.text_area("Your question or special request",
                               placeholder="e.g. Need a quiet room and airport pickup")
        submitted = st.form_submit_button("Submit enquiry")

    if submitted:
        if not name.strip() or not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            st.error("Please enter your name and a valid email address.")
        else:
            st.session_state.enquiries.append({
                "Name": name, "Email": email, "Phone": phone,
                "City": e_city, "Room": e_room,
                "Check-in": str(e_date), "Message": message,
            })
            st.success(f"Thanks {name}! Your enquiry for {hotels[e_city]['name']} "
                       "has been recorded.")

    if st.session_state.enquiries:
        st.subheader("Enquiries this session")
        st.dataframe(pd.DataFrame(st.session_state.enquiries),
                     use_container_width=True)

# ----------------------------------------
# TAB 5 – ABOUT
# ----------------------------------------

with tab_about:
    st.subheader("What this app does")

    a1, a2, a3 = st.columns(3)
    cards = [
        ("Ask", "Chat in plain English", (30, 60, 114), (42, 82, 152),
         "Intent detection and entity extraction understand city, room type, "
         "facility and budget from your message."),
        ("Compare", "Filter & compare hotels", (0, 105, 148), (0, 168, 150),
         "Use the sidebar to filter by city, room, budget and facilities, "
         "then compare prices in charts."),
        ("Plan", "Estimate & enquire", (255, 126, 95), (254, 180, 123),
         "Calculate the cost of a stay with tax and breakfast, then submit "
         "an enquiry form."),
    ]
    for col, (t, s, c1_, c2_, desc) in zip((a1, a2, a3), cards):
        with col:
            st.image(make_banner(t, s, c1_, c2_, width=600, height=240,
                                 icons=False),
                     use_container_width=True)
            st.write(desc)

    st.markdown(
        "**Tech:** Streamlit, rule-based NLP (intents + entities), lexicon "
        "sentiment analysis, pandas.\n\n"
        "**Disclaimer:** Hotels, prices, policies and reviews are fictional "
        "demo data for academic purposes."
    )
