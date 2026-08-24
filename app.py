import re
import streamlit as st
import pandas as pd


# =========================================================
# FIXED VALUES
# =========================================================

SOFA_VARIETIES = [
    "FG66151",
    "FG66252",
    "FG66353",
    "Guardian"
]


SOFA_COLORS = [
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
    "Guardian Teal"
]


BEDFRAME_VARIETIES = [
    "Embony",
    "Wave",
    "Loro"
]


BEDFRAME_COLORS = [
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

    "Loro Beige",
    "Loro Silver",
    "Loro Grey",
    "Loro Bronze",
    "Loro Teal",
    "Loro Light Grey",
    "Loro Granite",
    "Loro Slate",

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
    "Embony Teal"
]


# =========================================================
# SIZE ORDER
# =========================================================

# Mattress 和 Bedframe 都统一使用这个顺序
SIZE_ORDER = [
    "King",
    "Queen",
    "Super Single",
    "Single"
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
    "In stock?"
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
    "In stock?"
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
    "SKU"
]


# =========================================================
# PRICE PARSER
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

    return int(
        round(
            float(cleaned)
        )
    )


# =========================================================
# SOFA SIZE + PRICE PARSER
# =========================================================

def parse_sofa_size_price(text):

    result = []
    invalid = []

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) < 2:

            invalid.append(
                raw_line
            )

            continue

        try:

            price = parse_price(
                parts[-1]
            )

            size = " ".join(
                parts[:-1]
            ).strip()

            if not size:
                raise ValueError(
                    "Missing size"
                )

            result.append({
                "size": size,
                "price": price
            })

        except Exception:

            invalid.append(
                raw_line
            )

    return result, invalid


# =========================================================
# BEDFRAME / MATTRESS PRICE PARSER
# =========================================================

def parse_price_only(
    text,
    selected_sizes
):

    price_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not selected_sizes:

        return [], (
            "请先选择至少一个 Size。"
        )

    if len(price_lines) != len(
        selected_sizes
    ):

        return [], (
            f"你选择了 "
            f"{len(selected_sizes)} 个 Size，"
            f"所以需要贴 "
            f"{len(selected_sizes)} 个价格；"
            f"现在有 "
            f"{len(price_lines)} 个。"
        )

    result = []

    try:

        for size, price_line in zip(
            selected_sizes,
            price_lines
        ):

            result.append({
                "size": size,
                "price":
                    parse_price(
                        price_line
                    )
            })

    except Exception:

        return [], (
            "有价格无法读取。"
            "请使用例如 2699 "
            "或 2,699.00。"
        )

    return result, None


# =========================================================
# CUSTOM COLOR
# =========================================================

def parse_custom_colors(text):

    if not text.strip():
        return []

    values = re.split(
        r"[\n,]+",
        text
    )

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


# =========================================================
# SAFE FILE NAME
# =========================================================

def safe_filename(name):

    cleaned = re.sub(
        r'[\\/:*?"<>|]+',
        "_",
        name.strip()
    )

    return cleaned or "product"


# =========================================================
# ID SYSTEM
# =========================================================

def get_id_value(
    id_mode,
    parent_id,
    variation_index=None
):

    # Auto ID:
    # WordPress 自动生成
    if id_mode == "Auto ID":
        return ""

    # Parent
    if variation_index is None:

        return int(
            parent_id
        )

    # Variation ID +1
    return (
        int(parent_id)
        + variation_index
    )


# =========================================================
# PARENT REFERENCE
# =========================================================

def get_parent_reference(
    id_mode,
    parent_id,
    main_sku
):

    # Auto ID:
    # variation Parent 跟 main SKU
    if id_mode == "Auto ID":

        return main_sku.strip()

    # Manual ID
    return (
        f"id:{int(parent_id)}"
    )


# =========================================================
# MAIN SKU
# =========================================================

def get_parent_sku(
    id_mode,
    main_sku
):

    # 只有 Auto ID 的 main variable
    # 才需要 SKU
    if id_mode == "Auto ID":

        return main_sku.strip()

    # Manual ID 全部 SKU 空
    return ""


# =========================================================
# CLEAR ALL
# =========================================================

def clear_form():

    keys = [
        "product_name",
        "main_sku",
        "parent_id",

        "sofa_bulk",
        "bedframe_bulk",
        "mattress_bulk",

        "sofa_extra_colors",
        "bedframe_extra_colors",

        "sofa_varieties",
        "sofa_colors",

        "bedframe_varieties",
        "bedframe_colors",

        "bedframe_sizes",
        "mattress_sizes"
    ]

    for key in keys:

        if key in st.session_state:

            del st.session_state[
                key
            ]


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
    colors
):

    rows = []

    sizes = [
        item["size"]
        for item in size_data
    ]

    parent_reference = (
        get_parent_reference(
            id_mode,
            parent_id,
            main_sku
        )
    )

    # ==========================
    # SOFA PARENT
    # ==========================

    parent_row = {

        "ID":
            get_id_value(
                id_mode,
                parent_id
            ),

        "Type":
            "variable",

        "SKU":
            get_parent_sku(
                id_mode,
                main_sku
            ),

        "Name":
            name,

        "Published":
            published,

        "Visibility in catalog":
            "visible",

        "Parent":
            "",

        "Attribute 1 name":
            "Seater",

        "Attribute 1 value(s)":
            ", ".join(
                sizes
            ),

        "Attribute 2 name":
            "Shipping",

        "Attribute 2 value(s)":
            "West Malaysia, East Malaysia",

        "Attribute 3 name":
            "Material",

        "Attribute 3 value(s)":
            "Fabric",

        "Attribute 4 name":
            "Series",

        "Attribute 4 value(s)":
            "Easy Clean",

        "Attribute 5 name":
            "Variety",

        "Attribute 5 value(s)":
            ", ".join(
                varieties
            ),

        "Attribute 6 name":
            "Color",

        "Attribute 6 value(s)":
            ", ".join(
                colors
            ),

        "Regular price":
            "",

        "Stock":
            "",

        "In stock?":
            ""
    }

    rows.append(
        parent_row
    )

    variation_index = 1

    # ==========================
    # SOFA VARIATIONS
    # ==========================

    for item in size_data:

        size = item["size"]

        west_price = (
            item["price"]
        )

        for shipping in [
            "West Malaysia",
            "East Malaysia"
        ]:

            price = (
                west_price
                if shipping
                   == "West Malaysia"
                else west_price + 1000
            )

            for variety in varieties:

                row = {

                    "ID":
                        get_id_value(
                            id_mode,
                            parent_id,
                            variation_index
                        ),

                    "Type":
                        "variation",

                    # Variation SKU 空
                    "SKU":
                        "",

                    "Name":
                        name,

                    "Published":
                        published,

                    "Visibility in catalog":
                        "visible",

                    "Parent":
                        parent_reference,

                    "Attribute 1 name":
                        "Seater",

                    "Attribute 1 value(s)":
                        size,

                    "Attribute 2 name":
                        "Shipping",

                    "Attribute 2 value(s)":
                        shipping,

                    "Attribute 3 name":
                        "Material",

                    "Attribute 3 value(s)":
                        "Fabric",

                    "Attribute 4 name":
                        "Series",

                    "Attribute 4 value(s)":
                        "Easy Clean",

                    "Attribute 5 name":
                        "Variety",

                    "Attribute 5 value(s)":
                        variety,

                    "Attribute 6 name":
                        "Color",

                    "Attribute 6 value(s)":
                        "",

                    "Regular price":
                        price,

                    "Stock":
                        10,

                    "In stock?":
                        1
                }

                rows.append(
                    row
                )

                variation_index += 1

    return pd.DataFrame(
        rows,
        columns=SOFA_COLUMNS
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
    varieties,
    colors
):

    rows = []

    sizes = [
        item["size"]
        for item in size_data
    ]

    parent_reference = (
        get_parent_reference(
            id_mode,
            parent_id,
            main_sku
        )
    )

    # ==========================
    # BEDFRAME PARENT
    # ==========================

    parent_row = {

        "ID":
            get_id_value(
                id_mode,
                parent_id
            ),

        "Name":
            name,

        "Type":
            "variable",

        "Categories":
            "Bedframe",

        "Published":
            published,

        "Visibility in catalog":
            "visible",

        "Attribute 1 name":
            "Size",

        "Attribute 1 value(s)":
            ",".join(
                sizes
            ),

        "Attribute 4 name":
            "Shipping",

        "Attribute 4 value(s)":
            "West Malaysia,East Malaysia",

        "Attribute 5 name":
            "Series",

        "Attribute 5 value(s)":
            "Easy Clean",

        "Attribute 6 name":
            "Variety",

        "Attribute 6 value(s)":
            ",".join(
                varieties
            ),

        # 你要求新增 Bedframe Color
        "Attribute 7 name":
            "Color",

        "Attribute 7 value(s)":
            ", ".join(
                colors
            ),

        "Regular price":
            "",

        "Stock":
            "",

        "In stock?":
            "",

        "Parent":
            "",

        "SKU":
            get_parent_sku(
                id_mode,
                main_sku
            )
    }

    rows.append(
        parent_row
    )

    variation_index = 1

    # ==========================
    # BEDFRAME VARIATIONS
    # ==========================

    for item in size_data:

        size = item["size"]

        west_price = (
            item["price"]
        )

        for shipping in [
            "West Malaysia",
            "East Malaysia"
        ]:

            price = (
                west_price
                if shipping
                   == "West Malaysia"
                else west_price + 1000
            )

            for variety in varieties:

                row = {

                    "ID":
                        get_id_value(
                            id_mode,
                            parent_id,
                            variation_index
                        ),

                    "Name":
                        name,

                    "Type":
                        "variation",

                    "Categories":
                        "Bedframe",

                    "Published":
                        published,

                    "Visibility in catalog":
                        "visible",

                    "Attribute 1 name":
                        "Size",

                    "Attribute 1 value(s)":
                        size,

                    "Attribute 4 name":
                        "Shipping",

                    "Attribute 4 value(s)":
                        shipping,

                    "Attribute 5 name":
                        "Series",

                    "Attribute 5 value(s)":
                        "Easy Clean",

                    "Attribute 6 name":
                        "Variety",

                    "Attribute 6 value(s)":
                        variety,

                    "Attribute 7 name":
                        "Color",

                    "Attribute 7 value(s)":
                        "",

                    "Regular price":
                        price,

                    "Stock":
                        10,

                    "In stock?":
                        1,

                    "Parent":
                        parent_reference,

                    # Variation SKU 空
                    "SKU":
                        ""
                }

                rows.append(
                    row
                )

                variation_index += 1

    return pd.DataFrame(
        rows,
        columns=BEDFRAME_COLUMNS
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
    main_sku
):

    rows = []

    sizes = [
        item["size"]
        for item in size_data
    ]

    parent_reference = (
        get_parent_reference(
            id_mode,
            parent_id,
            main_sku
        )
    )

    # ==========================
    # MATTRESS PARENT
    # ==========================

    parent_row = {

        "ID":
            get_id_value(
                id_mode,
                parent_id
            ),

        "Type":
            "variable",

        "SKU":
            get_parent_sku(
                id_mode,
                main_sku
            ),

        "Name":
            name,

        "Published":
            published,

        "Visibility in catalog":
            "visible",

        "Parent":
            "",

        "Attribute 1 name":
            "Size",

        "Attribute 1 value(s)":
            ", ".join(
                sizes
            ),

        "Attribute 2 name":
            "Shipping",

        "Attribute 2 value(s)":
            "West Malaysia, East Malaysia",

        "Attribute 3 name":
            "",

        "Attribute 3 value(s)":
            "",

        "Regular price":
            "",

        "Stock":
            "",

        "In stock?":
            ""
    }

    rows.append(
        parent_row
    )

    variation_index = 1

    # ==========================
    # MATTRESS VARIATIONS
    # ==========================

    for item in size_data:

        size = item["size"]

        west_price = (
            item["price"]
        )

        for shipping in [
            "West Malaysia",
            "East Malaysia"
        ]:

            price = (
                west_price
                if shipping
                   == "West Malaysia"
                else west_price + 1000
            )

            row = {

                "ID":
                    get_id_value(
                        id_mode,
                        parent_id,
                        variation_index
                    ),

                "Type":
                    "variation",

                # Variation SKU 空
                "SKU":
                    "",

                "Name":
                    name,

                "Published":
                    published,

                "Visibility in catalog":
                    "visible",

                "Parent":
                    parent_reference,

                "Attribute 1 name":
                    "Size",

                "Attribute 1 value(s)":
                    size,

                "Attribute 2 name":
                    "Shipping",

                "Attribute 2 value(s)":
                    shipping,

                "Attribute 3 name":
                    "",

                "Attribute 3 value(s)":
                    "",

                "Regular price":
                    price,

                "Stock":
                    10,

                "In stock?":
                    1
            }

            rows.append(
                row
            )

            variation_index += 1

    return pd.DataFrame(
        rows,
        columns=MATTRESS_COLUMNS
    )


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title=
        "MPO/MELI New Product CSV",

    layout=
        "centered"
)


st.title(
    "MPO/MELI New Product CSV"
)


# =========================================================
# PRODUCT TYPE
# =========================================================

product_type = st.radio(
    "Product Type",

    [
        "Sofa",
        "Bedframe",
        "Mattress"
    ],

    horizontal=True
)


# =========================================================
# WORDPRESS ID METHOD
# =========================================================

id_mode = st.radio(
    "WordPress ID Method",

    [
        "Auto ID",
        "Manual ID"
    ],

    horizontal=True,

    help=(
        "Auto ID：ID 留空，"
        "由 WordPress 自动生成；"
        "Main Variable SKU 必填，"
        "Variation Parent 跟这个 SKU。"
        "\n\n"
        "Manual ID：自己填写 Parent ID；"
        "Variation ID 自动 +1，"
        "Parent 使用 id:xxx；"
        "SKU 全部留空。"
    )
)


# =========================================================
# PRODUCT NAME
# =========================================================

product_name = st.text_input(
    "Product Name",
    key="product_name"
)


# =========================================================
# AUTO ID / MANUAL ID
# =========================================================

if id_mode == "Auto ID":

    main_sku = st.text_input(
        "Main Variable SKU",

        key=
            "main_sku",

        placeholder=
            "Example: AUTUMN-BEDFRAME",

        help=(
            "Auto ID 模式只有 "
            "Main Variable 要填 SKU。"
            "Variation SKU 会留空。"
        )
    )

    parent_id = None


else:

    parent_id = st.number_input(
        "Parent ID",

        min_value=1,

        step=1,

        value=10000,

        key=
            "parent_id"
    )

    # Manual ID 不需要 SKU
    main_sku = ""


# =========================================================
# PUBLIC / PRIVATE
# =========================================================

visibility = st.radio(
    "Product Status",

    [
        "Public",
        "Private"
    ],

    horizontal=True
)


published_value = (
    1
    if visibility == "Public"
    else 0
)


# =========================================================
# DEFAULT
# =========================================================

size_data = []

parse_error = None

invalid_lines = []


# =========================================================
# SOFA UI
# =========================================================

if product_type == "Sofa":

    st.subheader(
        "Sofa Variety"
    )


    selected_sofa_varieties = (
        st.multiselect(

            "Choose Variety",

            SOFA_VARIETIES,

            default=
                SOFA_VARIETIES,

            key=
                "sofa_varieties"
        )
    )


    st.subheader(
        "Sofa Colors"
    )


    selected_sofa_colors = (
        st.multiselect(

            "Choose Colors",

            SOFA_COLORS,

            default=
                SOFA_COLORS,

            key=
                "sofa_colors"
        )
    )


    sofa_extra_colors = (
        st.text_area(

            "Add New Colors (Optional)",

            key=
                "sofa_extra_colors",

            placeholder=
"""One color per line

Example:
FG66151 Cream
Guardian Blue Grey"""
        )
    )


    final_sofa_colors = (
        unique_list(

            selected_sofa_colors

            + parse_custom_colors(
                sofa_extra_colors
            )
        )
    )


    st.subheader(
        "Sofa Size & West Malaysia Price"
    )


    sofa_bulk = st.text_area(

        "Paste Size + Price from Excel",

        height=220,

        key=
            "sofa_bulk",

        placeholder=
"""2LA + RADB (28")    4,590.00
1S (28")              2,990.00
2S (28")              3,590.00"""
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

    st.subheader(
        "Bedframe Variety"
    )


    selected_bedframe_varieties = (
        st.multiselect(

            "Choose Variety",

            BEDFRAME_VARIETIES,

            default=
                BEDFRAME_VARIETIES,

            key=
                "bedframe_varieties"
        )
    )


    st.subheader(
        "Bedframe Colors"
    )


    selected_bedframe_colors = (
        st.multiselect(

            "Choose Colors",

            BEDFRAME_COLORS,

            default=
                BEDFRAME_COLORS,

            key=
                "bedframe_colors"
        )
    )


    bedframe_extra_colors = (
        st.text_area(

            "Add New Colors (Optional)",

            key=
                "bedframe_extra_colors",

            placeholder=
"""One color per line

Example:
Wave Cream
Embony Light Beige"""
        )
    )


    final_bedframe_colors = (
        unique_list(

            selected_bedframe_colors

            + parse_custom_colors(
                bedframe_extra_colors
            )
        )
    )


    # ==========================
    # BEDFRAME SIZE
    # ==========================

    st.subheader(
        "Bedframe Sizes"
    )


    bedframe_selected_raw = (
        st.multiselect(

            "Choose Size",

            SIZE_ORDER,

            default=[
                "King",
                "Queen"
            ],

            key=
                "bedframe_sizes"
        )
    )


    # 强制 K → Q → SS → S
    selected_bedframe_sizes = [

        size

        for size in SIZE_ORDER

        if size
        in bedframe_selected_raw
    ]


    if selected_bedframe_sizes:

        st.info(
            "Paste prices in this order: "
            + " → ".join(
                selected_bedframe_sizes
            )
        )


    bedframe_bulk = st.text_area(

        "Paste West Malaysia Price Only",

        height=180,

        key=
            "bedframe_bulk",

        placeholder=
"""2,699.00
2,499.00"""
    )


    if bedframe_bulk.strip():

        size_data, parse_error = (
            parse_price_only(

                bedframe_bulk,

                selected_bedframe_sizes
            )
        )


# =========================================================
# MATTRESS UI
# =========================================================

else:

    st.subheader(
        "Mattress Sizes"
    )


    mattress_selected_raw = (
        st.multiselect(

            "Choose Size",

            SIZE_ORDER,

            default=[
                "King",
                "Queen"
            ],

            key=
                "mattress_sizes"
        )
    )


    # 强制 K → Q → SS → S
    selected_mattress_sizes = [

        size

        for size in SIZE_ORDER

        if size
        in mattress_selected_raw
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

        key=
            "mattress_bulk",

        placeholder=
"""2,599.00
1,599.00"""
    )


    if mattress_bulk.strip():

        size_data, parse_error = (
            parse_price_only(

                mattress_bulk,

                selected_mattress_sizes
            )
        )


# =========================================================
# ERRORS
# =========================================================

if invalid_lines:

    st.warning(
        "以下 Sofa 行无法读取：\n"
        + "\n".join(
            invalid_lines
        )
    )


if parse_error:

    st.error(
        parse_error
    )


# =========================================================
# PRICE PREVIEW
# =========================================================

if size_data:

    preview = pd.DataFrame([

        {
            "Size":
                item["size"],

            "West Malaysia":
                item["price"],

            "East Malaysia":
                item["price"]
                + 1000
        }

        for item in size_data
    ])


    st.subheader(
        "Price Preview"
    )


    st.dataframe(
        preview,

        use_container_width=True,

        hide_index=True
    )


# =========================================================
# BUTTON
# =========================================================

col1, col2 = st.columns(
    2
)


with col1:

    generate_clicked = (
        st.button(

            "Generate CSV",

            type=
                "primary",

            use_container_width=
                True
        )
    )


with col2:

    st.button(

        "Clear All",

        on_click=
            clear_form,

        use_container_width=
            True
    )


# =========================================================
# GENERATE CSV
# =========================================================

if generate_clicked:

    errors = []


    # Product name
    if not product_name.strip():

        errors.append(
            "Product Name 不能为空。"
        )


    # Auto ID 必须 main SKU
    if (
        id_mode == "Auto ID"
        and not main_sku.strip()
    ):

        errors.append(
            "Auto ID 模式必须填写 "
            "Main Variable SKU。"
        )


    # Size / Price
    if not size_data:

        errors.append(
            "没有有效的 Size / Price。"
        )


    if parse_error:

        errors.append(
            parse_error
        )


    # Sofa validation
    if product_type == "Sofa":

        if not selected_sofa_varieties:

            errors.append(
                "Sofa 至少选择一个 Variety。"
            )


        if not final_sofa_colors:

            errors.append(
                "Sofa 至少选择一个 Color。"
            )


    # Bedframe validation
    if product_type == "Bedframe":

        if not selected_bedframe_varieties:

            errors.append(
                "Bedframe 至少选择一个 Variety。"
            )


        if not final_bedframe_colors:

            errors.append(
                "Bedframe 至少选择一个 Color。"
            )


    # ==========================
    # SHOW ERRORS
    # ==========================

    if errors:

        for error in errors:

            st.error(
                error
            )


    # ==========================
    # GENERATE
    # ==========================

    else:

        # Sofa
        if product_type == "Sofa":

            df = generate_sofa(

                product_name.strip(),

                published_value,

                size_data,

                id_mode,

                parent_id,

                main_sku,

                selected_sofa_varieties,

                final_sofa_colors
            )


        # Bedframe
        elif product_type == "Bedframe":

            df = generate_bedframe(

                product_name.strip(),

                published_value,

                size_data,

                id_mode,

                parent_id,

                main_sku,

                selected_bedframe_varieties,

                final_bedframe_colors
            )


        # Mattress
        else:

            df = generate_mattress(

                product_name.strip(),

                published_value,

                size_data,

                id_mode,

                parent_id,

                main_sku
            )


        # ==========================
        # CSV EXPORT
        # ==========================

        csv_bytes = (

            df.to_csv(
                index=False
            )

            .encode(
                "utf-8-sig"
            )
        )


        st.success(
            f"CSV Generated! "
            f"{len(df) - 1} variations"
        )


        st.dataframe(

            df.head(15),

            use_container_width=True,

            hide_index=True
        )


        st.download_button(

            "Download CSV",

            data=
                csv_bytes,

            file_name=
                f"{safe_filename(product_name)} Import.csv",

            mime=
                "text/csv",

            use_container_width=
                True
        )
