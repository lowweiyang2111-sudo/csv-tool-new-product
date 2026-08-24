import re
import streamlit as st
import pandas as pd


# =========================================================
# FABRIC / COLOR DATABASE
# =========================================================

EASY_CLEAN_VARIETIES = [
    "FG66151",
    "FG66252",
    "FG66353",
    "Guardian",
    "Embony",
    "Wave",
    "Loro",
]

FABRIC_COLORS = {
    "FG66151": [
        "FG66151 Beige",
        "FG66151 Carolina Blue",
        "FG66151 Cedar",
        "FG66151 Dark Brown",
        "FG66151 Dark Cyan",
        "FG66151 Dark Grey",
        "FG66151 Denim Blue",
        "FG66151 Espresso",
        "FG66151 Gold",
        "FG66151 Grey",
        "FG66151 Light Grey",
        "FG66151 Onyx",
        "FG66151 Peach",
        "FG66151 Police Blue",
        "FG66151 Prussian Blue",
        "FG66151 Teal",
    ],
    "FG66252": [
        "FG66252 Beige",
        "FG66252 Cedar",
        "FG66252 Charcoal",
        "FG66252 Dark Cyan",
        "FG66252 Gold",
        "FG66252 Granite",
        "FG66252 Grey",
        "FG66252 Light Grey",
        "FG66252 Mahogany",
        "FG66252 Navy Blue",
        "FG66252 Onyx",
        "FG66252 Red Orange",
    ],
    "FG66353": [
        "FG66353 Beige",
        "FG66353 Brown",
        "FG66353 Dark Blue",
        "FG66353 Dark Cyan",
        "FG66353 Denim Blue",
        "FG66353 Forest Green",
        "FG66353 Grey",
        "FG66353 Greyish Blue",
        "FG66353 Light Blue",
        "FG66353 Mahogany",
        "FG66353 Midnight Blue",
        "FG66353 Onyx",
        "FG66353 Teal",
    ],
    "Guardian": [
        "Guardian Beige",
        "Guardian Cedar",
        "Guardian Dark Blue",
        "Guardian Dark Grey",
        "Guardian Denim Blue",
        "Guardian Gold",
        "Guardian Grey",
        "Guardian Khaki",
        "Guardian Light Grey",
        "Guardian Navy Blue",
        "Guardian Peach",
        "Guardian Teal",
    ],
    "Embony": [
        "Embony Beige",
        "Embony Cedar",
        "Embony Dark Beige",
        "Embony Denim Blue",
        "Embony Forest Green",
        "Embony Gold",
        "Embony Grey",
        "Embony Grey Blue",
        "Embony Khaki",
        "Embony Light Grey",
        "Embony Navy Blue",
        "Embony Peach",
        "Embony Silver Ash",
        "Embony Slate",
        "Embony Teal",
    ],
    "Wave": [
        "Wave Light Grey",
        "Wave Grey",
        "Wave Dark Grey",
        "Wave Gold",
        "Wave Cedar",
        "Wave Peach",
        "Wave Teal",
        "Wave Olive Green",
        "Wave Forest Green",
        "Wave Dark Blue",
        "Wave Slate",
    ],
    "Loro": [
        "Loro Beige",
        "Loro Silver",
        "Loro Grey",
        "Loro Bronze",
        "Loro Teal",
        "Loro Light Grey",
        "Loro Granite",
        "Loro Slate",
    ],
}


# Mattress and Bedframe price order
SIZE_ORDER = [
    "King",
    "Queen",
    "Super Single",
    "Single",
]


# =========================================================
# CSV COLUMNS
# =========================================================

SOFA_COLUMNS = [
    "ID",
    "Type",
    "SKU",
    "Name",
    "Published",
    "Visibility in catalog",
    "Parent",
    "Attribute 1 name",
    "Attribute 1 value(s)",
    "Attribute 2 name",
    "Attribute 2 value(s)",
    "Attribute 3 name",
    "Attribute 3 value(s)",
    "Attribute 4 name",
    "Attribute 4 value(s)",
    "Attribute 5 name",
    "Attribute 5 value(s)",
    "Attribute 6 name",
    "Attribute 6 value(s)",
    "Regular price",
    "Stock",
    "In stock?",
]

MATTRESS_COLUMNS = [
    "ID",
    "Type",
    "SKU",
    "Name",
    "Published",
    "Visibility in catalog",
    "Parent",
    "Attribute 1 name",
    "Attribute 1 value(s)",
    "Attribute 2 name",
    "Attribute 2 value(s)",
    "Attribute 3 name",
    "Attribute 3 value(s)",
    "Regular price",
    "Stock",
    "In stock?",
]

BEDFRAME_COLUMNS = [
    "ID",
    "Name",
    "Type",
    "Categories",
    "Published",
    "Visibility in catalog",
    "Attribute 1 name",
    "Attribute 1 value(s)",
    "Attribute 4 name",
    "Attribute 4 value(s)",
    "Attribute 5 name",
    "Attribute 5 value(s)",
    "Attribute 6 name",
    "Attribute 6 value(s)",
    "Attribute 7 name",
    "Attribute 7 value(s)",
    "Regular price",
    "Stock",
    "In stock?",
    "Parent",
    "SKU",
]


# =========================================================
# HELPERS
# =========================================================

def parse_price(text):
    cleaned = (
        str(text)
        .strip()
        .upper()
        .replace("RM", "")
        .replace(",", "")
        .replace(" ", "")
    )

    if not cleaned:
        raise ValueError("Empty price")

    return int(round(float(cleaned)))


def parse_sofa_size_price(text):
    result = []
    invalid = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) < 2:
            invalid.append(raw_line)
            continue

        try:
            price = parse_price(parts[-1])
            size = " ".join(parts[:-1]).strip()

            if not size:
                raise ValueError("Missing size")

            result.append({"size": size, "price": price})

        except Exception:
            invalid.append(raw_line)

    return result, invalid


def parse_price_only(text, selected_sizes):
    price_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not selected_sizes:
        return [], "Please select at least one Size."

    if len(price_lines) != len(selected_sizes):
        return [], (
            f"You selected {len(selected_sizes)} Size(s), so you need "
            f"{len(selected_sizes)} price(s). Current: {len(price_lines)}."
        )

    result = []

    try:
        for size, price_line in zip(selected_sizes, price_lines):
            result.append({
                "size": size,
                "price": parse_price(price_line),
            })

    except Exception:
        return [], "Invalid price. Example: 2699 or 2,699.00."

    return result, None


def parse_custom_colors(text):
    if not text.strip():
        return []

    values = re.split(r"[\n,]+", text)

    return [
        value.strip()
        for value in values
        if value.strip()
    ]


def unique_list(values):
    result = []

    for value in values:
        if value not in result:
            result.append(value)

    return result


def get_colors_for_varieties(varieties):
    colors = []

    for variety in varieties:
        colors.extend(FABRIC_COLORS.get(variety, []))

    return colors


def safe_filename(name):
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name.strip())
    return cleaned or "product"


def generate_auto_sku(product_name, product_type):
    name_part = re.sub(
        r"[^A-Za-z0-9]+",
        "-",
        product_name.strip(),
    ).strip("-")

    if not name_part:
        return ""

    return f"{name_part}-{product_type}".upper()


# =========================================================
# ID / SKU SYSTEM
# =========================================================

def get_id_value(id_mode, parent_id, variation_index=None):
    if id_mode == "Auto ID":
        return ""

    if variation_index is None:
        return int(parent_id)

    return int(parent_id) + variation_index


def get_parent_reference(id_mode, parent_id, main_sku):
    if id_mode == "Auto ID":
        return main_sku.strip()

    return f"id:{int(parent_id)}"


def get_parent_sku(id_mode, main_sku):
    if id_mode == "Auto ID":
        return main_sku.strip()

    return ""


# =========================================================
# COLOR SELECTOR
# =========================================================

def render_color_selector(prefix, selected_varieties):
    available_colors = get_colors_for_varieties(selected_varieties)

    selected_key = f"{prefix}_selected_colors"
    previous_options_key = f"_{prefix}_previous_color_options"

    previous_options = st.session_state.get(previous_options_key, [])

    if selected_key not in st.session_state:
        st.session_state[selected_key] = available_colors.copy()

    elif available_colors != previous_options:
        current_selected = st.session_state.get(selected_key, [])

        previously_all_selected = (
            bool(previous_options)
            and set(current_selected) == set(previous_options)
        )

        if previously_all_selected:
            st.session_state[selected_key] = available_colors.copy()
        else:
            st.session_state[selected_key] = [
                color
                for color in current_selected
                if color in available_colors
            ]

    st.session_state[previous_options_key] = available_colors.copy()

    selected_colors = st.multiselect(
        "Choose Available Colors",
        available_colors,
        key=selected_key,
    )

    return selected_colors


# =========================================================
# CLEAR FORM
# =========================================================

def clear_form():
    keys = [
        "product_name",
        "main_sku",
        "_last_auto_sku",
        "parent_id",
        "sofa_bulk",
        "bedframe_bulk",
        "mattress_bulk",
        "sofa_varieties",
        "bedframe_varieties",
        "sofa_selected_colors",
        "bedframe_selected_colors",
        "_sofa_previous_color_options",
        "_bedframe_previous_color_options",
        "sofa_custom_colors",
        "bedframe_custom_colors",
        "bedframe_sizes",
        "mattress_sizes",
        "bedframe_normal_fabric",
    ]

    for key in keys:
        if key in st.session_state:
            del st.session_state[key]


# =========================================================
# SOFA GENERATOR
# =========================================================

def generate_sofa(
    name,
    published,
    size_data,
    id_mode,
    parent_id,
    main_sku,
    varieties,
    colors,
):
    rows = []
    sizes = [item["size"] for item in size_data]

    parent_reference = get_parent_reference(
        id_mode,
        parent_id,
        main_sku,
    )

    parent_row = {
        "ID": get_id_value(id_mode, parent_id),
        "Type": "variable",
        "SKU": get_parent_sku(id_mode, main_sku),
        "Name": name,
        "Published": published,
        "Visibility in catalog": "visible",
        "Parent": "",
        "Attribute 1 name": "Seater",
        "Attribute 1 value(s)": ", ".join(sizes),
        "Attribute 2 name": "Shipping",
        "Attribute 2 value(s)": "West Malaysia, East Malaysia",
        "Attribute 3 name": "Material",
        "Attribute 3 value(s)": "Fabric",
        "Attribute 4 name": "Series",
        "Attribute 4 value(s)": "Easy Clean",
        "Attribute 5 name": "Variety",
        "Attribute 5 value(s)": ", ".join(varieties),
        "Attribute 6 name": "Color",
        "Attribute 6 value(s)": ", ".join(colors),
        "Regular price": "",
        "Stock": "",
        "In stock?": "",
    }

    rows.append(parent_row)

    variation_index = 1

    for item in size_data:
        size = item["size"]
        west_price = item["price"]

        for shipping in ["West Malaysia", "East Malaysia"]:
            price = (
                west_price
                if shipping == "West Malaysia"
                else west_price + 1000
            )

            for variety in varieties:
                row = {
                    "ID": get_id_value(
                        id_mode,
                        parent_id,
                        variation_index,
                    ),
                    "Type": "variation",
                    "SKU": "",
                    "Name": name,
                    "Published": published,
                    "Visibility in catalog": "visible",
                    "Parent": parent_reference,
                    "Attribute 1 name": "Seater",
                    "Attribute 1 value(s)": size,
                    "Attribute 2 name": "Shipping",
                    "Attribute 2 value(s)": shipping,
                    "Attribute 3 name": "Material",
                    "Attribute 3 value(s)": "Fabric",
                    "Attribute 4 name": "Series",
                    "Attribute 4 value(s)": "Easy Clean",
                    "Attribute 5 name": "Variety",
                    "Attribute 5 value(s)": variety,
                    "Attribute 6 name": "Color",
                    "Attribute 6 value(s)": "",
                    "Regular price": price,
                    "Stock": 10,
                    "In stock?": 1,
                }

                rows.append(row)
                variation_index += 1

    return pd.DataFrame(rows, columns=SOFA_COLUMNS)


# =========================================================
# BEDFRAME GENERATOR
# =========================================================

def generate_bedframe(
    name,
    published,
    size_data,
    id_mode,
    parent_id,
    main_sku,
    easy_clean_varieties,
    easy_clean_colors,
    include_normal_fabric,
):
    rows = []
    sizes = [item["size"] for item in size_data]

    parent_reference = get_parent_reference(
        id_mode,
        parent_id,
        main_sku,
    )

    series_values = []
    variety_values = list(easy_clean_varieties)
    color_values = list(easy_clean_colors)

    if easy_clean_varieties:
        series_values.append("Easy Clean")

    if include_normal_fabric:
        series_values.append("Normal Fabric")
        variety_values.append("Normal Fabric")
        color_values.append("Normal Fabric")

    variety_values = unique_list(variety_values)
    color_values = unique_list(color_values)

    parent_row = {
        "ID": get_id_value(id_mode, parent_id),
        "Name": name,
        "Type": "variable",
        "Categories": "Bedframe",
        "Published": published,
        "Visibility in catalog": "visible",
        "Attribute 1 name": "Size",
        "Attribute 1 value(s)": ",".join(sizes),
        "Attribute 4 name": "Shipping",
        "Attribute 4 value(s)": "West Malaysia,East Malaysia",
        "Attribute 5 name": "Series",
        "Attribute 5 value(s)": ",".join(series_values),
        "Attribute 6 name": "Variety",
        "Attribute 6 value(s)": ",".join(variety_values),
        "Attribute 7 name": "Color",
        "Attribute 7 value(s)": ",".join(color_values),
        "Regular price": "",
        "Stock": "",
        "In stock?": "",
        "Parent": "",
        "SKU": get_parent_sku(id_mode, main_sku),
    }

    rows.append(parent_row)

    variation_index = 1

    for item in size_data:
        size = item["size"]
        base_price = item["price"]

        if include_normal_fabric:
            normal_west_price = base_price

            for shipping in ["West Malaysia", "East Malaysia"]:
                normal_price = (
                    normal_west_price
                    if shipping == "West Malaysia"
                    else normal_west_price + 1000
                )

                row = {
                    "ID": get_id_value(
                        id_mode,
                        parent_id,
                        variation_index,
                    ),
                    "Name": name,
                    "Type": "variation",
                    "Categories": "Bedframe",
                    "Published": published,
                    "Visibility in catalog": "visible",
                    "Attribute 1 name": "Size",
                    "Attribute 1 value(s)": size,
                    "Attribute 4 name": "Shipping",
                    "Attribute 4 value(s)": shipping,
                    "Attribute 5 name": "Series",
                    "Attribute 5 value(s)": "Normal Fabric",
                    "Attribute 6 name": "Variety",
                    "Attribute 6 value(s)": "Normal Fabric",
                    "Attribute 7 name": "Color",
                    "Attribute 7 value(s)": "Normal Fabric",
                    "Regular price": normal_price,
                    "Stock": 10,
                    "In stock?": 1,
                    "Parent": parent_reference,
                    "SKU": "",
                }

                rows.append(row)
                variation_index += 1

        if easy_clean_varieties:
            easy_clean_west_price = (
                base_price + 250
                if include_normal_fabric
                else base_price
            )

            for shipping in ["West Malaysia", "East Malaysia"]:
                easy_clean_price = (
                    easy_clean_west_price
                    if shipping == "West Malaysia"
                    else easy_clean_west_price + 1000
                )

                for variety in easy_clean_varieties:
                    row = {
                        "ID": get_id_value(
                            id_mode,
                            parent_id,
                            variation_index,
                        ),
                        "Name": name,
                        "Type": "variation",
                        "Categories": "Bedframe",
                        "Published": published,
                        "Visibility in catalog": "visible",
                        "Attribute 1 name": "Size",
                        "Attribute 1 value(s)": size,
                        "Attribute 4 name": "Shipping",
                        "Attribute 4 value(s)": shipping,
                        "Attribute 5 name": "Series",
                        "Attribute 5 value(s)": "Easy Clean",
                        "Attribute 6 name": "Variety",
                        "Attribute 6 value(s)": variety,
                        "Attribute 7 name": "Color",
                        "Attribute 7 value(s)": "",
                        "Regular price": easy_clean_price,
                        "Stock": 10,
                        "In stock?": 1,
                        "Parent": parent_reference,
                        "SKU": "",
                    }

                    rows.append(row)
                    variation_index += 1

    return pd.DataFrame(rows, columns=BEDFRAME_COLUMNS)


# =========================================================
# MATTRESS GENERATOR
# =========================================================

def generate_mattress(
    name,
    published,
    size_data,
    id_mode,
    parent_id,
    main_sku,
):
    rows = []
    sizes = [item["size"] for item in size_data]

    parent_reference = get_parent_reference(
        id_mode,
        parent_id,
        main_sku,
    )

    parent_row = {
        "ID": get_id_value(id_mode, parent_id),
        "Type": "variable",
        "SKU": get_parent_sku(id_mode, main_sku),
        "Name": name,
        "Published": published,
        "Visibility in catalog": "visible",
        "Parent": "",
        "Attribute 1 name": "Size",
        "Attribute 1 value(s)": ", ".join(sizes),
        "Attribute 2 name": "Shipping",
        "Attribute 2 value(s)": "West Malaysia, East Malaysia",
        "Attribute 3 name": "",
        "Attribute 3 value(s)": "",
        "Regular price": "",
        "Stock": "",
        "In stock?": "",
    }

    rows.append(parent_row)

    variation_index = 1

    for item in size_data:
        size = item["size"]
        west_price = item["price"]

        for shipping in ["West Malaysia", "East Malaysia"]:
            price = (
                west_price
                if shipping == "West Malaysia"
                else west_price + 1000
            )

            row = {
                "ID": get_id_value(
                    id_mode,
                    parent_id,
                    variation_index,
                ),
                "Type": "variation",
                "SKU": "",
                "Name": name,
                "Published": published,
                "Visibility in catalog": "visible",
                "Parent": parent_reference,
                "Attribute 1 name": "Size",
                "Attribute 1 value(s)": size,
                "Attribute 2 name": "Shipping",
                "Attribute 2 value(s)": shipping,
                "Attribute 3 name": "",
                "Attribute 3 value(s)": "",
                "Regular price": price,
                "Stock": 10,
                "In stock?": 1,
            }

            rows.append(row)
            variation_index += 1

    return pd.DataFrame(rows, columns=MATTRESS_COLUMNS)


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="MPO/MELI New Product CSV",
    layout="centered",
)

st.title("MPO/MELI New Product CSV")


# =========================================================
# PRODUCT TYPE
# =========================================================

product_type = st.radio(
    "Product Type",
    ["Sofa", "Bedframe", "Mattress"],
    horizontal=True,
    key="product_type",
)


# =========================================================
# ID METHOD
# =========================================================

id_mode = st.radio(
    "WordPress ID Method",
    ["Auto ID", "Manual ID"],
    horizontal=True,
    key="id_mode",
)


# =========================================================
# PRODUCT NAME
# =========================================================

product_name = st.text_input(
    "Product Name",
    key="product_name",
)


# =========================================================
# AUTO SKU / MANUAL ID
# =========================================================

if id_mode == "Auto ID":
    auto_sku = generate_auto_sku(
        product_name,
        product_type,
    )

    last_auto_sku = st.session_state.get(
        "_last_auto_sku",
        "",
    )

    if "main_sku" not in st.session_state:
        st.session_state["main_sku"] = auto_sku

    elif st.session_state["main_sku"] == last_auto_sku:
        st.session_state["main_sku"] = auto_sku

    st.session_state["_last_auto_sku"] = auto_sku

    main_sku = st.text_input(
        "Product Reference Code / SKU",
        key="main_sku",
        help=(
            "Automatically generated from Product Name + Product Type. "
            "You can still edit it manually."
        ),
    )

    if st.button("Reset SKU to Auto"):
        st.session_state["main_sku"] = auto_sku
        st.session_state["_last_auto_sku"] = auto_sku
        st.rerun()

    parent_id = None

else:
    parent_id = st.number_input(
        "Parent ID",
        min_value=1,
        step=1,
        value=10000,
        key="parent_id",
    )

    main_sku = ""


# =========================================================
# PUBLIC / PRIVATE
# =========================================================

visibility = st.radio(
    "Product Status",
    ["Public", "Private"],
    horizontal=True,
    key="visibility",
)

published_value = 1 if visibility == "Public" else 0


# =========================================================
# DEFAULTS
# =========================================================

size_data = []
parse_error = None
invalid_lines = []

selected_sofa_varieties = []
final_sofa_colors = []

selected_bedframe_varieties = []
final_bedframe_colors = []
include_normal_fabric = False


# =========================================================
# SOFA UI
# =========================================================

if product_type == "Sofa":
    st.subheader("Easy Clean Fabric")

    selected_sofa_varieties = st.multiselect(
        "Choose Fabric Code",
        EASY_CLEAN_VARIETIES,
        default=EASY_CLEAN_VARIETIES,
        key="sofa_varieties",
    )

    st.subheader("Available Colors")

    selected_sofa_colors = render_color_selector(
        "sofa",
        selected_sofa_varieties,
    )

    sofa_custom_colors = st.text_area(
        "Add New Colors (Optional)",
        key="sofa_custom_colors",
    )

    final_sofa_colors = unique_list(
        selected_sofa_colors
        + parse_custom_colors(sofa_custom_colors)
    )

    st.subheader("Sofa Size & West Malaysia Price")

    sofa_bulk = st.text_area(
        "Paste Size + Price from Excel",
        height=220,
        key="sofa_bulk",
    )

    size_data, invalid_lines = parse_sofa_size_price(
        sofa_bulk
    )


# =========================================================
# BEDFRAME UI
# =========================================================

elif product_type == "Bedframe":
    st.subheader("Easy Clean Fabric")

    selected_bedframe_varieties = st.multiselect(
        "Choose Easy Clean Fabric Code",
        EASY_CLEAN_VARIETIES,
        default=EASY_CLEAN_VARIETIES,
        key="bedframe_varieties",
    )

    include_normal_fabric = st.checkbox(
        "Include Normal Fabric",
        value=False,
        key="bedframe_normal_fabric",
    )

    st.subheader("Available Colors")

    selected_bedframe_colors = render_color_selector(
        "bedframe",
        selected_bedframe_varieties,
    )

    bedframe_custom_colors = st.text_area(
        "Add New Easy Clean Colors (Optional)",
        key="bedframe_custom_colors",
    )

    final_bedframe_colors = unique_list(
        selected_bedframe_colors
        + parse_custom_colors(bedframe_custom_colors)
    )

    st.subheader("Bedframe Sizes")

    bedframe_selected_raw = st.multiselect(
        "Choose Size",
        SIZE_ORDER,
        default=["King", "Queen"],
        key="bedframe_sizes",
    )

    selected_bedframe_sizes = [
        size
        for size in SIZE_ORDER
        if size in bedframe_selected_raw
    ]

    if selected_bedframe_sizes:
        st.info(
            "Paste prices in this order: "
            + " → ".join(selected_bedframe_sizes)
        )

    bedframe_bulk = st.text_area(
        "Paste West Malaysia Price Only",
        height=180,
        key="bedframe_bulk",
    )

    if bedframe_bulk.strip():
        size_data, parse_error = parse_price_only(
            bedframe_bulk,
            selected_bedframe_sizes,
        )


# =========================================================
# MATTRESS UI
# =========================================================

else:
    st.subheader("Mattress Sizes")

    mattress_selected_raw = st.multiselect(
        "Choose Size",
        SIZE_ORDER,
        default=["King", "Queen"],
        key="mattress_sizes",
    )

    selected_mattress_sizes = [
        size
        for size in SIZE_ORDER
        if size in mattress_selected_raw
    ]

    if selected_mattress_sizes:
        st.info(
            "Paste prices in this order: "
            + " → ".join(selected_mattress_sizes)
        )

    mattress_bulk = st.text_area(
        "Paste West Malaysia Price Only",
        height=180,
        key="mattress_bulk",
    )

    if mattress_bulk.strip():
        size_data, parse_error = parse_price_only(
            mattress_bulk,
            selected_mattress_sizes,
        )


# =========================================================
# ERRORS
# =========================================================

if invalid_lines:
    st.warning(
        "These Sofa rows could not be read:\n"
        + "\n".join(invalid_lines)
    )

if parse_error:
    st.error(parse_error)


# =========================================================
# PRICE PREVIEW
# =========================================================

if size_data:
    preview_rows = []

    for item in size_data:
        if (
            product_type == "Bedframe"
            and include_normal_fabric
            and selected_bedframe_varieties
        ):
            preview_rows.append({
                "Size": item["size"],
                "Normal Fabric West": item["price"],
                "Normal Fabric East": item["price"] + 1000,
                "Easy Clean West": item["price"] + 250,
                "Easy Clean East": item["price"] + 1250,
            })

        else:
            preview_rows.append({
                "Size": item["size"],
                "West Malaysia": item["price"],
                "East Malaysia": item["price"] + 1000,
            })

    st.subheader("Price Preview")

    st.dataframe(
        pd.DataFrame(preview_rows),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# BUTTONS
# =========================================================

col1, col2 = st.columns(2)

with col1:
    generate_clicked = st.button(
        "Generate CSV",
        type="primary",
        use_container_width=True,
    )

with col2:
    st.button(
        "Clear All",
        on_click=clear_form,
        use_container_width=True,
    )


# =========================================================
# GENERATE CSV
# =========================================================

if generate_clicked:
    errors = []

    if not product_name.strip():
        errors.append("Product Name cannot be empty.")

    if id_mode == "Auto ID" and not main_sku.strip():
        errors.append(
            "Auto ID requires a Product Reference Code / SKU."
        )

    if not size_data:
        errors.append("No valid Size / Price data found.")

    if parse_error:
        errors.append(parse_error)

    if product_type == "Sofa":
        if not selected_sofa_varieties:
            errors.append(
                "Sofa requires at least one Easy Clean Fabric Code."
            )

        if not final_sofa_colors:
            errors.append(
                "Sofa requires at least one Color."
            )

    if product_type == "Bedframe":
        if (
            not selected_bedframe_varieties
            and not include_normal_fabric
        ):
            errors.append(
                "Bedframe requires Easy Clean and/or Normal Fabric."
            )

        if (
            selected_bedframe_varieties
            and not final_bedframe_colors
        ):
            errors.append(
                "Easy Clean Bedframe requires at least one Color."
            )

    if errors:
        for error in errors:
            st.error(error)

    else:
        if product_type == "Sofa":
            df = generate_sofa(
                product_name.strip(),
                published_value,
                size_data,
                id_mode,
                parent_id,
                main_sku,
                selected_sofa_varieties,
                final_sofa_colors,
            )

        elif product_type == "Bedframe":
            df = generate_bedframe(
                product_name.strip(),
                published_value,
                size_data,
                id_mode,
                parent_id,
                main_sku,
                selected_bedframe_varieties,
                final_bedframe_colors,
                include_normal_fabric,
            )

        else:
            df = generate_mattress(
                product_name.strip(),
                published_value,
                size_data,
                id_mode,
                parent_id,
                main_sku,
            )

        csv_bytes = (
            df.to_csv(index=False)
            .encode("utf-8-sig")
        )

        st.success(
            f"CSV Generated! {len(df) - 1} variation rows."
        )

        st.dataframe(
            df.head(20),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name=f"{safe_filename(product_name)} Import.csv",
            mime="text/csv",
            use_container_width=True,
        )
