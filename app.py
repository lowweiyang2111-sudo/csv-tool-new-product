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
    "Loro",
    "Normal Fabric",
    "Easy Clean Fabric"
]

BED_SIZE_OPTIONS = [
    "King",
    "Queen",
    "Super Single",
    "Single"
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

if product_type == "Sofa":
    st.success("🛋 SOFA Mode")

if product_type == "Mattress":
    st.success("🛏 Mattress Mode")

if product_type == "Bedframe":
    st.success("🛏️ Bedframe Mode")

# ==========================
# SESSION STATE
# ==========================

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

# ==========================
# SIZE SELECTION
# ==========================

selected_sizes = []

if product_type in ["Bedframe", "Mattress"]:

    selected_sizes = st.multiselect(
        "Select Size",
        BED_SIZE_OPTIONS,
        default=BED_SIZE_OPTIONS
    )

    if selected_sizes:
        st.info(
            "Price order: "
            + " → ".join(selected_sizes)
        )

# ==========================
# BEDFRAME VARIETY
# ==========================

bedframe_variety = []
bedframe_plus_250_variety = []

if product_type == "Bedframe":

    bedframe_variety = st.multiselect(
        "Bedframe Variety",
        BEDFRAME_VARIETY_OPTIONS,
        default=[
            "Embony",
            "Wave",
            "Loro"
        ]
    )

    bedframe_plus_250_variety = st.multiselect(
        "Select Variety To Add RM250",
        bedframe_variety,
        default=[]
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

if product_type == "Mattress":

    st.subheader("Mattress Price")

    bulk_input = st.text_area(
        "Paste Mattress Price",
        height=200,
        key="bulk_input",
        placeholder="""2999
2599
2299
1999"""
    )

elif product_type == "Bedframe":

    st.subheader("Bedframe Price")

    bulk_input = st.text_area(
        "Paste Bedframe Price",
        height=200,
        key="bulk_input",
        placeholder="""2699
2499
2199
2099"""
    )

else:

    st.subheader("Paste Size & Price")

    bulk_input = st.text_area(
        "Paste Excel Size + Price",
        height=200,
        key="bulk_input",
        placeholder="""1MR (26")    3,790.00
2MRR (26")   6,290.00"""
    )

# ==========================
# PROCESS SIZE + PRICE
# ==========================

sizes_data = []

if bulk_input:

    lines = [
        line.strip()
        for line in bulk_input.strip().split("\n")
        if line.strip()
    ]

    if product_type in ["Bedframe", "Mattress"]:

        for index, line in enumerate(lines):

            if index >= len(selected_sizes):
                break

            try:

                price_text = (
                    line
                    .replace("RM", "")
                    .replace(",", "")
                    .replace(".00", "")
                    .strip()
                )

                price = int(price_text)

                sizes_data.append({
                    "size": selected_sizes[index],
                    "price": price
                })

            except ValueError:
                pass

    else:

        for line in lines:

            parts = line.split()

            if len(parts) >= 2:

                try:

                    price_text = (
                        parts[-1]
                        .replace("RM", "")
                        .replace(",", "")
                        .replace(".00", "")
                        .strip()
                    )

                    price = int(price_text)

                    size = " ".join(parts[:-1])

                    sizes_data.append({
                        "size": size,
                        "price": price
                    })

                except ValueError:
                    pass

# ==========================
# CLEAR ALL
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

# ==========================
# GENERATE CSV
# ==========================

if st.button("Generate CSV"):

    if not product_name.strip():
        st.error("Please enter Product Name.")
        st.stop()

    if product_type in ["Bedframe", "Mattress"]:

        if not selected_sizes:
            st.error("Please select at least one size.")
            st.stop()

        if len(sizes_data) != len(selected_sizes):
            st.error(
                "价格数量必须和选择的尺寸数量一样。"
            )
            st.stop()

    if not sizes_data:
        st.error("Please enter valid size and price.")
        st.stop()

    if product_type == "Bedframe" and not bedframe_variety:
        st.error(
            "Please select at least one Bedframe Variety."
        )
        st.stop()

    rows = []

    size_list = [
        size_item["size"]
        for size_item in sizes_data
    ]

    # ==========================
    # PARENT ROW
    # ==========================

    if product_type == "Mattress":

        parent_row = {
            "ID": parent_id,
            "Type": "variable",
            "SKU": "",
            "Name": product_name,
            "Published": published_value,
            "Visibility in catalog": "visible",
            "Parent": "",

            "Attribute 1 name": "Size",
            "Attribute 1 value(s)":
                ", ".join(size_list),

            "Attribute 2 name": "Shipping",
            "Attribute 2 value(s)":
                "West Malaysia, East Malaysia",

            "Regular price": "",

            "Stock": 10,
            "Stock status": "instock"
        }

    else:

        if product_type == "Bedframe":

            bedframe_series_values = []

            for variety in bedframe_variety:

                if variety == "Normal Fabric":
                    series = "normal fabric"
                else:
                    series = "easy clean fabric"

                if series not in bedframe_series_values:
                    bedframe_series_values.append(series)

            parent_series_value = "|".join(
                bedframe_series_values
            )

            parent_variety_value = "|".join(
                bedframe_variety
            )

        else:

            parent_series_value = "easy clean"

            parent_variety_value = (
                "FG66151|FG66252|FG66353|Guardian"
            )

        parent_row = {
            "ID": parent_id,
            "Type": "variable",
            "SKU": "",
            "Name": product_name,
            "Description": product_description,
            "Published": published_value,
            "Visibility in catalog": "visible",

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

            "Attribute 2 name": "shipping",
            "Attribute 2 value(s)":
                "West Malaysia|East Malaysia",

            "Attribute 3 name": "material",
            "Attribute 3 value(s)": "fabric",

            "Attribute 4 name": "series",
            "Attribute 4 value(s)":
                parent_series_value,

            "Attribute 5 name": "variety",
            "Attribute 5 value(s)":
                parent_variety_value,

            "Attribute 6 name": "color",

            "Attribute 6 value(s)":
                (
                    COLOR_VALUES
                    if product_type == "Sofa"
                    else BEDFRAME_COLOR_VALUES
                ),

            "Regular price": "",

            "Stock": 10,
            "Stock status": "instock"
        }

    rows.append(parent_row)

    # Parent 后的第一个 variation ID
    current_id = parent_id + 1

    # ==========================
    # MATTRESS VARIATIONS
    # ==========================

    if product_type == "Mattress":

        for size_item in sizes_data:

            size = size_item["size"]
            west_price = size_item["price"]
            east_price = west_price + 1000

            for shipping in [
                "West Malaysia",
                "East Malaysia"
            ]:

                if shipping == "West Malaysia":
                    price = west_price
                else:
                    price = east_price

                row = {
                    "ID": current_id,
                    "Type": "variation",
                    "SKU": "",
                    "Name": product_name,
                    "Published": published_value,
                    "Parent": f"id:{parent_id}",

                    "Attribute 1 name": "Size",
                    "Attribute 1 value(s)": size,

                    "Attribute 2 name": "Shipping",
                    "Attribute 2 value(s)": shipping,

                    "Visibility in catalog": "visible",

                    "Regular price": price,

                    "Stock": 10,
                    "Stock status": "instock"
                }

                rows.append(row)

                # 每生成一个 variation，ID +1
                current_id += 1

    # ==========================
    # SOFA / BEDFRAME VARIATIONS
    # ==========================

    else:

        for size_item in sizes_data:

            size = size_item["size"]
            west_price = size_item["price"]
            east_price = west_price + 1000

            if product_type == "Sofa":
                variety_list = VARIETY_OPTIONS
            else:
                variety_list = bedframe_variety

            for variety in variety_list:

                for shipping in [
                    "West Malaysia",
                    "East Malaysia"
                ]:

                    if shipping == "West Malaysia":
                        price = west_price
                    else:
                        price = east_price

                    # 只有手动选择的 Bedframe Variety 加 RM250
                    if (
                        product_type == "Bedframe"
                        and variety
                        in bedframe_plus_250_variety
                    ):
                        price += 250

                    if product_type == "Bedframe":

                        if variety == "Normal Fabric":
                            series_value = "normal fabric"
                        else:
                            series_value = "easy clean fabric"

                    else:
                        series_value = "easy clean"

                    row = {
                        "ID": current_id,
                        "Type": "variation",
                        "SKU": "",
                        "Name": product_name,
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
                            series_value,

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

                    # 每生成一个 variation，ID +1
                    current_id += 1

    # ==========================
    # CREATE CSV
    # ==========================

    df = pd.DataFrame(rows)

    csv = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.success(
        f"CSV Generated! Total rows: {len(rows)}"
    )

    st.download_button(
        "Download CSV",
        data=csv,
        file_name=f"{product_name}.csv",
        mime="text/csv"
    )
