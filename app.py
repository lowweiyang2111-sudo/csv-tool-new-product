import streamlit as st
import pandas as pd

# ==========================
# FIXED VALUES
# ==========================

VARIETY_OPTIONS = [
    "FG66151",
    "FG66252",
    "FG66353",
    "Guardian"
]

COLOR_VALUES = """FG66151 Beige, FG66151 Carolina Blue, FG66151 Cedar,
FG66151 Dark Brown, FG66151 Dark Cyan, FG66151 Dark Grey,
FG66151 Denim Blue, FG66151 Espresso, FG66151 Gold,
FG66151 Grey, FG66151 Light Grey, FG66151 Onyx,
FG66151 Peach, FG66151 Police Blue, FG66151 Prussian Blue,
FG66151 Teal, FG66252 Beige, FG66252 Cedar,
FG66252 Charcoal, FG66252 Dark Cyan, FG66252 Gold,
FG66252 Granite, FG66252 Grey, FG66252 Light Grey,
FG66252 Mahogany, FG66252 Navy Blue, FG66252 Onyx,
FG66252 Red Orange, FG66353 Beige, FG66353 Brown,
FG66353 Dark Blue, FG66353 Dark Cyan,
FG66353 Denim Blue, FG66353 Forest Green,
FG66353 Grey, FG66353 Greyish Blue,
FG66353 Light Blue, FG66353 Mahogany,
FG66353 Midnight Blue, FG66353 Onyx,
FG66353 Teal, Guardian Beige,
Guardian Cedar, Guardian Dark Blue,
Guardian Dark Grey, Guardian Denim Blue,
Guardian Gold, Guardian Grey,
Guardian Khaki, Guardian Light Grey,
Guardian Navy Blue, Guardian Peach,
Guardian Teal"""

# ==========================
# PAGE
# ==========================

st.set_page_config(page_title="MPO/MELI nwe product csv")

st.title("MPO/MELI nwe product csv")

# ==========================
# INPUT
# ==========================

parent_id = st.number_input(
    "Parent ID",
    min_value=1,
    step=1
)

product_name = st.text_input(
    "Product Name"
)

visibility = st.radio(
    "Visibility",
    ["Public", "Private"]
)

product_description = st.text_area(
    "Product Description",
    height=200
)

published_value = (
    1
    if visibility == "Public"
    else 0
)

st.subheader("Sizes & West Malaysia Price")

if "sizes" not in st.session_state:
    st.session_state.sizes = [
        {"size": "", "price": 0}
    ]

for i, item in enumerate(st.session_state.sizes):

    col1, col2 = st.columns(2)

    with col1:
        size = st.text_input(
            f"Size {i+1}",
            value=item["size"],
            key=f"size_{i}"
        )

    with col2:
        price = st.number_input(
            f"West Price {i+1}",
            min_value=0,
            step=100,
            value=item["price"],
            key=f"price_{i}"
        )

    st.session_state.sizes[i] = {
        "size": size,
        "price": price
    }

if st.button("+ Add Size"):
    st.session_state.sizes.append(
        {
            "size": "",
            "price": 0
        }
    )

# ==========================
# GENERATE CSV
# ==========================

if st.button("Generate CSV"):

    rows = []

    size_list = [
        s["size"]
        for s in st.session_state.sizes
        if s["size"].strip()
    ]

    # ==========================
    # PARENT ROW
    # ==========================

    parent_row = {
        "ID": parent_id,
        "Type": "variable",
        "SKU": "",
        "Name": product_name,
        "Description": product_description,
        "Published": published_value,
        "Parent": "",

        "Attribute 1 name": "seater",
        "Attribute 1 value(s)":
            "|".join(size_list),

        "Attribute 2 name":
            "shipping",
        "Attribute 2 value(s)":
            "West Malaysia|East Malaysia",

        "Attribute 3 name":
            "material",
        "Attribute 3 value(s)":
            "fabric",

        "Attribute 4 name":
            "series",
        "Attribute 4 value(s)":
            "easy clean",

        "Attribute 5 name":
            "variety",
        "Attribute 5 value(s)":
            "FG66151|FG66252|FG66353|Guardian",

        "Attribute 6 name":
            "color",
        "Attribute 6 value(s)":
            COLOR_VALUES,

        "Regular price": "",
        "Stock": 10,
        "Stock status":
            "instock"
    }

    rows.append(parent_row)

    current_id = parent_id + 1

    # ==========================
    # VARIATION ROWS
    # ==========================

    for s in st.session_state.sizes:

        size = s["size"].strip()

        if not size:
            continue

        west_price = s["price"]
        east_price = west_price + 1000

        for variety in VARIETY_OPTIONS:

            for shipping in [
                "West Malaysia",
                "East Malaysia"
            ]:

                price = (
                    west_price
                    if shipping ==
                    "West Malaysia"
                    else east_price
                )

                row = {
                    "ID":
                        current_id,

                    "Type":
                        "variation",

                    "SKU":
                        "",

                    "Name":
                        product_name,

                    "Description":
                        product_description,

                    "Published":
                        published_value,

                    "Parent":
                        f"id:{parent_id}",

                    "Attribute 1 name":
                        "seater",

                    "Attribute 1 value(s)":
                        size,

                    "Attribute 2 name":
                        "shipping",

                    "Attribute 2 value(s)":
                        shipping,

                    "Attribute 3 name":
                        "material",

                    "Attribute 3 value(s)":
                        "fabric",

                    "Attribute 4 name":
                        "series",

                    "Attribute 4 value(s)":
                        "easy clean",

                    "Attribute 5 name":
                        "variety",

                    "Attribute 5 value(s)":
                        variety,

                    "Attribute 6 name":
                        "color",

                    "Attribute 6 value(s)":
                        "",

                    "Regular price":
                        price,

                    "Stock":
                        10,

                    "Stock status":
                        "instock"
                }

                rows.append(row)
                current_id += 1

    df = pd.DataFrame(rows)

    csv = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.success(
        "CSV Generated!"
    )

    st.download_button(
        "Download CSV",
        csv,
        file_name=
        f"{product_name}.csv",
        mime="text/csv"
    )