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

BEDFRAME_VARIETY_OPTIONS = [
    "Embony",
    "Wave",
    "Loro"
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

BEDFRAME_COLOR_VALUES = """
Wave Light Grey|Wave Grey|Wave Dark Grey|Wave Gold|
Wave Cedar|Wave Peach|Wave Teal|Wave Olive Green|
Wave Forest Green|Wave Dark Blue|Wave Slate|

Loro Beige|Loro Silver|Loro Grey|Loro Bronze|
Loro Teal|Loro Light Grey|Loro Granite|Loro Slate|

Embony Beige|Embony Cedar|Embony Dark Beige|
Embony Denim Blue|Embony Forest Green|
Embony Gold|Embony Grey|Embony Grey Blue|
Embony Khaki|Embony Light Grey|
Embony Navy Blue|Embony Peach|
Embony Silver Ash|Embony Slate|
Embony Teal
"""

# ==========================
# PAGE
# ==========================

st.set_page_config(
    page_title="MPO/MELI New Product CSV"
)

st.title("MPO/MELI New Product CSV")

product_type = st.radio(
    "Product Type",
    ["Sofa", "Bedframe", "Mattress"]
)

if product_type == "Mattress":
    st.info("🚧 Mattress Coming Soon")
    st.stop()

if product_type == "Bedframe":
    st.success("🛏️ Bedframe Mode")

if "product_name" not in st.session_state:
    st.session_state.product_name = ""

if "product_description" not in st.session_state:
    st.session_state.product_description = ""

if "bulk_input" not in st.session_state:
    st.session_state.bulk_input = ""

if "parent_id" not in st.session_state:
    st.session_state.parent_id = 1

# ==========================
# INPUT
# ==========================

parent_id = st.number_input(
    "Parent ID",
    min_value=1,
    step=1000,
    key="parent_id"
)

product_name = st.text_input(
    "Product Name",
    key="product_name"
)

visibility = st.radio(
    "Visibility",
    ["Public", "Private"]
)

if product_type == "Bedframe":

    bedframe_variety = st.multiselect(
        "Bedframe Variety",
        [
            "Embony",
            "Wave",
            "Loro"
        ],
        default=[
            "Embony",
            "Wave",
            "Loro"
        ]
    )


product_description = st.text_area(
    "Product Description",
    height=200,
    key="product_description"
)

published_value = (
    1
    if visibility == "Public"
    else 0
)

# ==========================
# BULK SIZE + PRICE
# ==========================

if product_type == "Bedframe":

    st.subheader("Bedframe Price")

    bulk_input = st.text_area(
        "Paste Bedframe Size + Price",
        height=200,
        key="bulk_input",
        placeholder="""
Queen 2499
King 2999
"""
    )

else:

    st.subheader("Paste Size & Price")

    bulk_input = st.text_area(
        "Paste Excel Size + Price",
        height=200,
        key="bulk_input",
        placeholder="""
1MR (26")    3,790.00
2MRR (26")   6,290.00
"""
)

sizes_data = []

if bulk_input:

    lines = bulk_input.strip().split("\n")

    if product_type == "Bedframe":

        bedframe_size_map = [
            "King",
            "Queen",
            "Super Single",
            "Single"
        ]

        for i, line in enumerate(lines):

            if i >= len(bedframe_size_map):
                break

            try:

                price = int(
                    line
                    .replace(",", "")
                    .replace(".00", "")
                    .strip()
                )

                sizes_data.append({
                    "size": bedframe_size_map[i],
                    "price": price
                })

            except:
                pass

    else:

        for line in lines:

            parts = line.split()

            if len(parts) >= 2:

                try:

                    price_text = (
                        parts[-1]
                        .replace(",", "")
                        .replace(".00", "")
                    )

                    price = int(price_text)

                    size = " ".join(parts[:-1])

                    sizes_data.append({
                        "size": size,
                        "price": price
                    })

                except:
                    pass

    lines = bulk_input.strip().split("\n")

    for line in lines:

        parts = line.split()

        if len(parts) >= 2:

            try:

                price_text = (
                    parts[-1]
                    .replace(",", "")
                    .replace(".00", "")
                )

                price = int(price_text)

                size = " ".join(parts[:-1])

                sizes_data.append({
                    "size": size,
                    "price": price
                })

            except:
                pass

# ==========================
# GENERATE CSV
# ==========================
if st.button("Clear All"):

    for key in [
        "product_name",
        "product_description",
        "bulk_input",
        "parent_id"
    ]:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()

if st.button("Generate CSV"):

    rows = []

    size_list = [
        s["size"]
        for s in sizes_data
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
        "Visibility in catalog":
    "visible",

"Categories":
(
    "Sofa"
    if product_type == "Sofa"
    else "Bedframe"
),
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
    (
        "FG66151|FG66252|FG66353|Guardian"
        if product_type == "Sofa"
        else "Embony|Wave|Loro"
    ),

        "Attribute 6 name":
            "color",

        "Attribute 6 value(s)":
    (
        COLOR_VALUES
        if product_type == "Sofa"
        else BEDFRAME_COLOR_VALUES
    ),

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

    for s in sizes_data:

        size = s["size"]
        west_price = s["price"]
        east_price = west_price + 1000

        if product_type == "Sofa":

            variety_list = VARIETY_OPTIONS

        else:

            variety_list = BEDFRAME_VARIETY_OPTIONS

        for variety in variety_list:

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

    st.success("CSV Generated!")

    st.download_button(
        "Download CSV",
        csv,
        file_name=f"{product_name}.csv",
        mime="text/csv"
    )
