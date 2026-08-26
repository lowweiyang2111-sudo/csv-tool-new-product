import re
import streamlit as st
import pandas as pd


# =========================================================
# BASIC SETTINGS
# =========================================================

EAST_MALAYSIA_SURCHARGE = 1000
EASY_CLEAN_SURCHARGE_WHEN_NORMAL_SELECTED = 250

SIZE_ORDER = [
    "King",
    "Queen",
    "Super Single",
    "Single",
]

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


# =========================================================
# CSV COLUMNS
# Sofa / Bedframe:
# Size/Seater -> Shipping -> Material -> Series -> Variety -> Color
# =========================================================

FURNITURE_COLUMNS = [
    "ID",
    "Type",
    "SKU",
    "Name",
    "Published",
    "Visibility in catalog",
    "Categories",
    "Parent",

    "Attribute 1 name",
    "Attribute 1 value(s)",
    "Attribute 1 visible",
    "Attribute 1 global",

    "Attribute 2 name",
    "Attribute 2 value(s)",
    "Attribute 2 visible",
    "Attribute 2 global",

    "Attribute 3 name",
    "Attribute 3 value(s)",
    "Attribute 3 visible",
    "Attribute 3 global",

    "Attribute 4 name",
    "Attribute 4 value(s)",
    "Attribute 4 visible",
    "Attribute 4 global",

    "Attribute 5 name",
    "Attribute 5 value(s)",
    "Attribute 5 visible",
    "Attribute 5 global",

    "Attribute 6 name",
    "Attribute 6 value(s)",
    "Attribute 6 visible",
    "Attribute 6 global",

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
    """
    Example:
    1MR (26")    3,790.00
    2MRR (26")   6,290.00
    """
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

            result.append({
                "size": size,
                "price": price,
            })

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
            f"You selected {len(selected_sizes)} size(s), so please paste "
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


def safe_filename(name):
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name.strip())
    return cleaned or "product"


def unique_list(values):
    result = []

    for value in values:
        if value not in result:
            result.append(value)

    return result


def generate_auto_sku(product_name, product_type):
    clean_name = re.sub(
        r"[^A-Za-z0-9]+",
        "-",
        product_name.strip(),
    ).strip("-")

    if not clean_name:
        return ""

    return f"{clean_name}-{product_type}".upper()


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


def normalize_custom_color(variety, raw_color):
    """
    If user types:
        Cream
    -> Loro Cream

    If user types:
        Loro Cream
    -> Loro Cream
    """
    color = raw_color.strip()

    if not color:
        return ""

    if color.lower().startswith(variety.lower() + " "):
        suffix = color[len(variety):].strip()
        return f"{variety} {suffix}".strip()

    return f"{variety} {color}".strip()


def parse_custom_colors_for_variety(variety, text):
    if not text.strip():
        return []

    raw_values = re.split(r"[\n,]+", text)

    colors = []

    for raw in raw_values:
        color = normalize_custom_color(variety, raw)

        if color:
            colors.append(color)

    return unique_list(colors)


def clear_form():
    fixed_keys = {
        "product_name",
        "main_sku",
        "_last_auto_sku",
        "parent_id",
        "sofa_bulk",
        "bedframe_bulk",
        "mattress_bulk",
        "sofa_varieties",
        "bedframe_varieties",
        "bedframe_series",
        "bedframe_sizes",
        "mattress_sizes",
        "visibility",
    }

    dynamic_prefixes = (
        "sofa_colors_",
        "sofa_custom_",
        "bedframe_colors_",
        "bedframe_custom_",
    )

    for key in list(st.session_state.keys()):
        if key in fixed_keys or key.startswith(dynamic_prefixes):
            del st.session_state[key]


# =========================================================
# COLOR UI
# Each selected variety owns its own color list.
# This is important so Loro only creates Loro colors, etc.
# =========================================================

def render_variety_color_selectors(prefix, selected_varieties):
    selected_map = {}

    if not selected_varieties:
        return selected_map

    st.subheader("Colors")
    st.caption(
        "Each Variety has its own colors. "
        "Only the colors selected under that Variety will be generated."
    )

    for variety in selected_varieties:
        safe_key = re.sub(r"[^A-Za-z0-9]+", "_", variety).lower()
        default_colors = FABRIC_COLORS.get(variety, [])

        with st.expander(f"{variety} Colors", expanded=False):
            selected_colors = st.multiselect(
                f"Choose {variety} Colors",
                options=default_colors,
                default=default_colors,
                key=f"{prefix}_colors_{safe_key}",
            )

            custom_text = st.text_area(
                f"Add New {variety} Colors (Optional)",
                key=f"{prefix}_custom_{safe_key}",
                placeholder=(
                    "One color per line.\n"
                    "You can type only the color name, e.g.\n"
                    "Cream\nBlue Grey"
                ),
                height=100,
            )

            custom_colors = parse_custom_colors_for_variety(
                variety,
                custom_text,
            )

            selected_map[variety] = unique_list(
                selected_colors + custom_colors
            )

            st.caption(
                f"{len(selected_map[variety])} color(s) selected for {variety}."
            )

    return selected_map


# =========================================================
# COMMON FURNITURE PARENT
# =========================================================

def build_furniture_parent(
    product_type,
    name,
    published,
    id_mode,
    parent_id,
    main_sku,
    sizes,
    series_values,
    variety_values,
    color_values,
):
    first_attribute_name = (
        "Seater"
        if product_type == "Sofa"
        else "Size"
    )

    return {
        "ID": get_id_value(id_mode, parent_id),
        "Type": "variable",
        "SKU": get_parent_sku(id_mode, main_sku),
        "Name": name,
        "Published": published,
        "Visibility in catalog": "visible",
        "Categories": product_type,
        "Parent": "",
        "Attribute 1 name": first_attribute_name,
        "Attribute 1 value(s)": ", ".join(sizes),
        "Attribute 1 visible": 1,
        "Attribute 1 global": 0,

        "Attribute 2 name": "Shipping",
        "Attribute 2 value(s)": "West Malaysia, East Malaysia",
        "Attribute 2 visible": 1,
        "Attribute 2 global": 0,

        "Attribute 3 name": "Material",
        "Attribute 3 value(s)": "Fabric",
        "Attribute 3 visible": 1,
        "Attribute 3 global": 0,

        "Attribute 4 name": "Series",
        "Attribute 4 value(s)": ", ".join(series_values),
        "Attribute 4 visible": 1,
        "Attribute 4 global": 0,

        "Attribute 5 name": "Variety",
        "Attribute 5 value(s)": ", ".join(variety_values),
        "Attribute 5 visible": 1,
        "Attribute 5 global": 0,

        "Attribute 6 name": "Color",
        "Attribute 6 value(s)": ", ".join(color_values),
        "Attribute 6 visible": 1,
        "Attribute 6 global": 1,
        "Regular price": "",
        "Stock": "",
        "In stock?": "",
    }


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
    selected_varieties,
    colors_by_variety,
):
    rows = []

    sizes = [
        item["size"]
        for item in size_data
    ]

    # Parent keeps all colors selected in the tool.
    # Variations intentionally leave Color blank, matching the
    # working WooCommerce export. This lets the storefront's
    # swatch/dependency logic filter colors after Variety is chosen.
    all_colors = []

    for variety in selected_varieties:
        all_colors.extend(
            colors_by_variety.get(variety, [])
        )

    all_colors = unique_list(all_colors)

    parent_row = build_furniture_parent(
        product_type="Sofa",
        name=name,
        published=published,
        id_mode=id_mode,
        parent_id=parent_id,
        main_sku=main_sku,
        sizes=sizes,
        series_values=["Easy Clean"],
        variety_values=selected_varieties,
        color_values=all_colors,
    )

    rows.append(parent_row)

    parent_reference = get_parent_reference(
        id_mode,
        parent_id,
        main_sku,
    )

    variation_index = 1

    for item in size_data:
        size = item["size"]
        west_price = item["price"]

        for shipping in [
            "West Malaysia",
            "East Malaysia",
        ]:
            price = (
                west_price
                if shipping == "West Malaysia"
                else west_price + EAST_MALAYSIA_SURCHARGE
            )

            # IMPORTANT: one variation per Variety, not per Color.
            # This matches the known-good WordPress export.
            for variety in selected_varieties:
                row = {
                    "ID": get_id_value(
                        id_mode,
                        parent_id,
                        variation_index,
                    ),
                    "Type": "variation",
                    "SKU": "",
                    "Name": name,
                    "Published": 1,
                    "Visibility in catalog": "visible",
                    "Categories": "Sofa",
                    "Parent": parent_reference,

                    "Attribute 1 name": "Seater",
                    "Attribute 1 value(s)": size,
                    "Attribute 1 visible": "",
                    "Attribute 1 global": 0,

                    "Attribute 2 name": "Shipping",
                    "Attribute 2 value(s)": shipping,
                    "Attribute 2 visible": "",
                    "Attribute 2 global": 0,

                    "Attribute 3 name": "Material",
                    "Attribute 3 value(s)": "Fabric",
                    "Attribute 3 visible": "",
                    "Attribute 3 global": 0,

                    "Attribute 4 name": "Series",
                    "Attribute 4 value(s)": "Easy Clean",
                    "Attribute 4 visible": "",
                    "Attribute 4 global": 0,

                    "Attribute 5 name": "Variety",
                    "Attribute 5 value(s)": variety,
                    "Attribute 5 visible": "",
                    "Attribute 5 global": 0,

                    "Attribute 6 name": "Color",
                    "Attribute 6 value(s)": "",
                    "Attribute 6 visible": "",
                    "Attribute 6 global": 1,

                    "Regular price": price,
                    "Stock": 10,
                    "In stock?": 1,
                }

                rows.append(row)
                variation_index += 1

    return pd.DataFrame(
        rows,
        columns=FURNITURE_COLUMNS,
    )


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
    selected_series,
    selected_varieties,
    colors_by_variety,
):
    rows = []

    sizes = [
        item["size"]
        for item in size_data
    ]

    include_easy_clean = (
        "Easy Clean" in selected_series
    )

    include_normal_fabric = (
        "Normal Fabric" in selected_series
    )

    # Parent must list every selectable Variety.
    parent_varieties = []

    if include_easy_clean:
        parent_varieties.extend(selected_varieties)

    if include_normal_fabric:
        parent_varieties.append("Normal Fabric")

    parent_varieties = unique_list(parent_varieties)

    # Parent carries all Color terms. Variations leave Color blank,
    # exactly like the known-good WordPress export.
    all_colors = []

    if include_easy_clean:
        for variety in selected_varieties:
            all_colors.extend(
                colors_by_variety.get(variety, [])
            )

    # User's requested Normal Fabric color code.
    if include_normal_fabric:
        all_colors.append("Normal Fabric")

    all_colors = unique_list(all_colors)

    parent_row = build_furniture_parent(
        product_type="Bedframe",
        name=name,
        published=published,
        id_mode=id_mode,
        parent_id=parent_id,
        main_sku=main_sku,
        sizes=sizes,
        series_values=selected_series,
        variety_values=parent_varieties,
        color_values=all_colors,
    )

    rows.append(parent_row)

    parent_reference = get_parent_reference(
        id_mode,
        parent_id,
        main_sku,
    )

    variation_index = 1

    for item in size_data:
        size = item["size"]
        base_west_price = item["price"]

        # Normal only: pasted price = Normal Fabric price
        # Easy Clean only: pasted price = Easy Clean price
        # Both selected: Easy Clean = Normal Fabric + RM250
        normal_west_price = base_west_price

        easy_clean_west_price = (
            base_west_price
            + EASY_CLEAN_SURCHARGE_WHEN_NORMAL_SELECTED
            if include_normal_fabric and include_easy_clean
            else base_west_price
        )

        for shipping in [
            "West Malaysia",
            "East Malaysia",
        ]:
            shipping_surcharge = (
                0
                if shipping == "West Malaysia"
                else EAST_MALAYSIA_SURCHARGE
            )

            # Normal Fabric: one variation per size + shipping.
            # Color is blank in the variation, matching the good export.
            if include_normal_fabric:
                row = {
                    "ID": get_id_value(
                        id_mode,
                        parent_id,
                        variation_index,
                    ),
                    "Type": "variation",
                    "SKU": "",
                    "Name": name,
                    "Published": 1,
                    "Visibility in catalog": "visible",
                    "Categories": "Bedframe",
                    "Parent": parent_reference,

                    "Attribute 1 name": "Size",
                    "Attribute 1 value(s)": size,
                    "Attribute 1 visible": "",
                    "Attribute 1 global": 0,

                    "Attribute 2 name": "Shipping",
                    "Attribute 2 value(s)": shipping,
                    "Attribute 2 visible": "",
                    "Attribute 2 global": 0,

                    "Attribute 3 name": "Material",
                    "Attribute 3 value(s)": "Fabric",
                    "Attribute 3 visible": "",
                    "Attribute 3 global": 0,

                    "Attribute 4 name": "Series",
                    "Attribute 4 value(s)": "Normal Fabric",
                    "Attribute 4 visible": "",
                    "Attribute 4 global": 0,

                    "Attribute 5 name": "Variety",
                    "Attribute 5 value(s)": "Normal Fabric",
                    "Attribute 5 visible": "",
                    "Attribute 5 global": 0,

                    "Attribute 6 name": "Color",
                    "Attribute 6 value(s)": "",
                    "Attribute 6 visible": "",
                    "Attribute 6 global": 1,

                    "Regular price": (
                        normal_west_price
                        + shipping_surcharge
                    ),
                    "Stock": 10,
                    "In stock?": 1,
                }

                rows.append(row)
                variation_index += 1

            # Easy Clean: one variation per selected Variety.
            # Do NOT create one variation per color.
            if include_easy_clean:
                for variety in selected_varieties:
                    row = {
                        "ID": get_id_value(
                            id_mode,
                            parent_id,
                            variation_index,
                        ),
                        "Type": "variation",
                        "SKU": "",
                        "Name": name,
                        "Published": 1,
                        "Visibility in catalog": "visible",
                        "Categories": "Bedframe",
                        "Parent": parent_reference,

                        "Attribute 1 name": "Size",
                        "Attribute 1 value(s)": size,
                        "Attribute 1 visible": "",
                        "Attribute 1 global": 0,

                        "Attribute 2 name": "Shipping",
                        "Attribute 2 value(s)": shipping,
                        "Attribute 2 visible": "",
                        "Attribute 2 global": 0,

                        "Attribute 3 name": "Material",
                        "Attribute 3 value(s)": "Fabric",
                        "Attribute 3 visible": "",
                        "Attribute 3 global": 0,

                        "Attribute 4 name": "Series",
                        "Attribute 4 value(s)": "Easy Clean",
                        "Attribute 4 visible": "",
                        "Attribute 4 global": 0,

                        "Attribute 5 name": "Variety",
                        "Attribute 5 value(s)": variety,
                        "Attribute 5 visible": "",
                        "Attribute 5 global": 0,

                        "Attribute 6 name": "Color",
                        "Attribute 6 value(s)": "",
                        "Attribute 6 visible": "",
                        "Attribute 6 global": 1,

                        "Regular price": (
                            easy_clean_west_price
                            + shipping_surcharge
                        ),
                        "Stock": 10,
                        "In stock?": 1,
                    }

                    rows.append(row)
                    variation_index += 1

    return pd.DataFrame(
        rows,
        columns=FURNITURE_COLUMNS,
    )


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

    sizes = [
        item["size"]
        for item in size_data
    ]

    parent_reference = get_parent_reference(
        id_mode,
        parent_id,
        main_sku,
    )

    parent_row = {
        "ID": get_id_value(
            id_mode,
            parent_id,
        ),
        "Type": "variable",
        "SKU": get_parent_sku(
            id_mode,
            main_sku,
        ),
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

        for shipping in [
            "West Malaysia",
            "East Malaysia",
        ]:
            price = (
                west_price
                if shipping == "West Malaysia"
                else west_price + EAST_MALAYSIA_SURCHARGE
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
                "Published": 1,
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

    return pd.DataFrame(
        rows,
        columns=MATTRESS_COLUMNS,
    )


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
    [
        "Sofa",
        "Bedframe",
        "Mattress",
    ],
    horizontal=True,
    key="product_type",
)


# =========================================================
# ID METHOD
# =========================================================

id_mode = st.radio(
    "WordPress ID Method",
    [
        "Auto ID",
        "Manual ID",
    ],
    horizontal=True,
    key="id_mode",
    help=(
        "Auto ID: WordPress generates the IDs. "
        "The main variable SKU is used as the Parent reference.\n\n"
        "Manual ID: Enter the Parent ID yourself. "
        "Variation IDs increase automatically and Parent uses id:xxxx."
    ),
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

    elif (
        st.session_state["main_sku"] == last_auto_sku
        or not st.session_state["main_sku"].strip()
    ):
        st.session_state["main_sku"] = auto_sku

    st.session_state["_last_auto_sku"] = auto_sku

    main_sku = st.text_input(
        "Product Reference Code / SKU",
        key="main_sku",
        help=(
            "Generated automatically from Product Name + Product Type. "
            "You can edit it manually."
        ),
    )

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
    [
        "Public",
        "Private",
    ],
    horizontal=True,
    key="visibility",
)

published_value = (
    1
    if visibility == "Public"
    else 0
)


# =========================================================
# DEFAULTS
# =========================================================

size_data = []
parse_error = None
invalid_lines = []

selected_sofa_varieties = []
sofa_colors_by_variety = {}

selected_bedframe_series = []
selected_bedframe_varieties = []
bedframe_colors_by_variety = {}


# =========================================================
# SOFA UI
# =========================================================

if product_type == "Sofa":
    st.subheader("Material")
    st.selectbox(
        "Material",
        ["Fabric"],
        disabled=True,
        key="sofa_material",
    )

    st.subheader("Series")
    st.selectbox(
        "Series",
        ["Easy Clean"],
        disabled=True,
        key="sofa_series",
    )

    st.subheader("Variety")

    selected_sofa_varieties = st.multiselect(
        "Choose Easy Clean Variety",
        EASY_CLEAN_VARIETIES,
        default=EASY_CLEAN_VARIETIES,
        key="sofa_varieties",
    )

    sofa_colors_by_variety = render_variety_color_selectors(
        "sofa",
        selected_sofa_varieties,
    )

    st.subheader(
        "Sofa Seater / Size & West Malaysia Price"
    )

    sofa_bulk = st.text_area(
        "Paste Size + Price from Excel",
        height=220,
        key="sofa_bulk",
        placeholder=(
            '1MR (26")    3,790.00\n'
            '2MRR (26")   6,290.00'
        ),
    )

    size_data, invalid_lines = (
        parse_sofa_size_price(
            sofa_bulk
        )
    )


# =========================================================
# BEDFRAME UI
# =========================================================

elif product_type == "Bedframe":
    st.subheader("Material")
    st.selectbox(
        "Material",
        ["Fabric"],
        disabled=True,
        key="bedframe_material",
    )

    st.subheader("Series")

    selected_bedframe_series = st.multiselect(
        "Choose Series",
        [
            "Easy Clean",
            "Normal Fabric",
        ],
        default=[
            "Easy Clean",
        ],
        key="bedframe_series",
    )

    if "Easy Clean" in selected_bedframe_series:
        st.subheader("Variety")

        selected_bedframe_varieties = st.multiselect(
            "Choose Easy Clean Variety",
            EASY_CLEAN_VARIETIES,
            default=EASY_CLEAN_VARIETIES,
            key="bedframe_varieties",
        )

        bedframe_colors_by_variety = (
            render_variety_color_selectors(
                "bedframe",
                selected_bedframe_varieties,
            )
        )

    if "Normal Fabric" in selected_bedframe_series:
        st.info(
            "Normal Fabric uses:\n"
            "Series = Normal Fabric\n"
            "Variety = Normal Fabric\n"
            "Color = Normal Fabric"
        )

    st.subheader("Bedframe Sizes")

    raw_bedframe_sizes = st.multiselect(
        "Choose Size",
        SIZE_ORDER,
        default=[
            "King",
            "Queen",
        ],
        key="bedframe_sizes",
    )

    selected_bedframe_sizes = [
        size
        for size in SIZE_ORDER
        if size in raw_bedframe_sizes
    ]

    if selected_bedframe_sizes:
        st.info(
            "Paste prices in this order: "
            + " → ".join(
                selected_bedframe_sizes
            )
        )

    if (
        "Normal Fabric" in selected_bedframe_series
        and "Easy Clean" in selected_bedframe_series
    ):
        st.caption(
            "The pasted price is the Normal Fabric price. "
            "Easy Clean will automatically be + RM250."
        )

    elif "Normal Fabric" in selected_bedframe_series:
        st.caption(
            "The pasted price is the Normal Fabric price."
        )

    elif "Easy Clean" in selected_bedframe_series:
        st.caption(
            "The pasted price is the Easy Clean price."
        )

    bedframe_bulk = st.text_area(
        "Paste West Malaysia Price Only",
        height=180,
        key="bedframe_bulk",
        placeholder=(
            "2,699.00\n"
            "2,499.00"
        ),
    )

    if bedframe_bulk.strip():
        size_data, parse_error = (
            parse_price_only(
                bedframe_bulk,
                selected_bedframe_sizes,
            )
        )


# =========================================================
# MATTRESS UI
# =========================================================

else:
    st.subheader("Mattress Sizes")

    raw_mattress_sizes = st.multiselect(
        "Choose Size",
        SIZE_ORDER,
        default=[
            "King",
            "Queen",
        ],
        key="mattress_sizes",
    )

    selected_mattress_sizes = [
        size
        for size in SIZE_ORDER
        if size in raw_mattress_sizes
    ]

    if selected_mattress_sizes:
        st.info(
            "Paste prices in this order: "
            + " → ".join(
                selected_mattress_sizes
            )
        )

    mattress_bulk = st.text_area(
        "Paste West Malaysia Price Only",
        height=180,
        key="mattress_bulk",
        placeholder=(
            "2,599.00\n"
            "1,599.00"
        ),
    )

    if mattress_bulk.strip():
        size_data, parse_error = (
            parse_price_only(
                mattress_bulk,
                selected_mattress_sizes,
            )
        )


# =========================================================
# INPUT WARNINGS
# =========================================================

if invalid_lines:
    st.warning(
        "These Sofa rows could not be read:\n"
        + "\n".join(
            invalid_lines
        )
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
            and "Normal Fabric"
            in selected_bedframe_series
            and "Easy Clean"
            in selected_bedframe_series
        ):
            preview_rows.append({
                "Size": item["size"],
                "Normal Fabric West": item["price"],
                "Normal Fabric East": (
                    item["price"]
                    + EAST_MALAYSIA_SURCHARGE
                ),
                "Easy Clean West": (
                    item["price"]
                    + EASY_CLEAN_SURCHARGE_WHEN_NORMAL_SELECTED
                ),
                "Easy Clean East": (
                    item["price"]
                    + EASY_CLEAN_SURCHARGE_WHEN_NORMAL_SELECTED
                    + EAST_MALAYSIA_SURCHARGE
                ),
            })

        else:
            preview_rows.append({
                "Size": item["size"],
                "West Malaysia": item["price"],
                "East Malaysia": (
                    item["price"]
                    + EAST_MALAYSIA_SURCHARGE
                ),
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
    clear_clicked = st.button(
        "Clear All",
        use_container_width=True,
    )

if clear_clicked:
    clear_form()
    st.rerun()


# =========================================================
# VALIDATE + GENERATE
# =========================================================

if generate_clicked:
    errors = []

    if not product_name.strip():
        errors.append(
            "Product Name cannot be empty."
        )

    if (
        id_mode == "Auto ID"
        and not main_sku.strip()
    ):
        errors.append(
            "Auto ID requires a Product Reference Code / SKU."
        )

    if not size_data:
        errors.append(
            "No valid Size / Price data found."
        )

    if parse_error:
        errors.append(
            parse_error
        )

    # -----------------------------------------------------
    # SOFA VALIDATION
    # -----------------------------------------------------

    if product_type == "Sofa":
        if not selected_sofa_varieties:
            errors.append(
                "Please select at least one Sofa Variety."
            )

        for variety in selected_sofa_varieties:
            if not sofa_colors_by_variety.get(
                variety,
                [],
            ):
                errors.append(
                    f"{variety} must have at least one Color."
                )

    # -----------------------------------------------------
    # BEDFRAME VALIDATION
    # -----------------------------------------------------

    if product_type == "Bedframe":
        if not selected_bedframe_series:
            errors.append(
                "Please select at least one Bedframe Series."
            )

        if (
            "Easy Clean" in selected_bedframe_series
            and not selected_bedframe_varieties
        ):
            errors.append(
                "Easy Clean requires at least one Variety."
            )

        if "Easy Clean" in selected_bedframe_series:
            for variety in selected_bedframe_varieties:
                if not bedframe_colors_by_variety.get(
                    variety,
                    [],
                ):
                    errors.append(
                        f"{variety} must have at least one Color."
                    )

    # -----------------------------------------------------
    # SHOW ERRORS OR GENERATE
    # -----------------------------------------------------

    if errors:
        for error in errors:
            st.error(error)

    else:
        if product_type == "Sofa":
            df = generate_sofa(
                name=product_name.strip(),
                published=published_value,
                size_data=size_data,
                id_mode=id_mode,
                parent_id=parent_id,
                main_sku=main_sku,
                selected_varieties=selected_sofa_varieties,
                colors_by_variety=sofa_colors_by_variety,
            )

        elif product_type == "Bedframe":
            df = generate_bedframe(
                name=product_name.strip(),
                published=published_value,
                size_data=size_data,
                id_mode=id_mode,
                parent_id=parent_id,
                main_sku=main_sku,
                selected_series=selected_bedframe_series,
                selected_varieties=selected_bedframe_varieties,
                colors_by_variety=bedframe_colors_by_variety,
            )

        else:
            df = generate_mattress(
                name=product_name.strip(),
                published=published_value,
                size_data=size_data,
                id_mode=id_mode,
                parent_id=parent_id,
                main_sku=main_sku,
            )

        csv_bytes = (
            df.to_csv(index=False)
            .encode("utf-8-sig")
        )

        st.success(
            f"CSV Generated! "
            f"{len(df) - 1} variation row(s)."
        )

        st.dataframe(
            df.head(30),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name=(
                f"{safe_filename(product_name)} Import.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )
