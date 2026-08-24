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
    "Loro"
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
        "FG66151 Teal"
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
        "FG66252 Red Orange"
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
        "FG66353 Teal"
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
        "Guardian Teal"
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
        "Embony Teal"
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
        "Wave Slate"
    ],

    "Loro": [
        "Loro Beige",
        "Loro Silver",
        "Loro Grey",
        "Loro Bronze",
        "Loro Teal",
        "Loro Light Grey",
        "Loro Granite",
        "Loro Slate"
    ]
}


# =========================================================
# SIZE ORDER
# =========================================================

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
# BASIC HELPERS
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


def safe_filename(name):

    cleaned = re.sub(
        r'[\\/:*?"<>|]+',
        "_",
        name.strip()
    )

    return cleaned or "product"


def unique_list(values):

    result = []

    for value in values:

        if value not in result:
            result.append(value)

    return result


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


def get_colors_for_varieties(varieties):

    result = []

    for variety in varieties:

        result.extend(
            FABRIC_COLORS.get(
                variety,
                []
            )
        )

    return result


# =========================================================
# SOFA SIZE + PRICE
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

            invalid.append(raw_line)

            continue

        try:

            price = parse_price(
                parts[-1]
            )

            size = " ".join(
                parts[:-1]
            ).strip()

            if not size:
                raise ValueError()

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
# BEDFRAME / MATTRESS PRICE
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
            f"你选择了 {len(selected_sizes)} 个 Size，"
            f"所以需要 {len(selected_sizes)} 个价格。"
            f"现在只有 {len(price_lines)} 个。"
        )

    result = []

    try:

        for size, price_line in zip(
            selected_sizes,
            price_lines
        ):

            result.append({
                "size": size,
                "price": parse_price(
                    price_line
                )
            })

    except Exception:

        return [], (
            "有价格无法读取。"
            "请使用例如 2699 或 2,699.00。"
        )

    return result, None


# =========================================================
# ID / SKU SYSTEM
# =========================================================

def get_id_value(
    id_mode,
    parent_id,
    variation_index=None
):

    if id_mode == "Auto ID":

        return ""

    if variation_index is None:

        return int(parent_id)

    return (
        int(parent_id)
        + variation_index
    )


def get_parent_reference(
    id_mode,
    parent_id,
    main_sku
):

    if id_mode == "Auto ID":

        return main_sku.strip()

    return f"id:{int(parent_id)}"


def get_parent_sku(
    id_mode,
    main_sku
):

    if id_mode == "Auto ID":

        return main_sku.strip()

    return ""


# =========================================================
# CLEAR FORM
# =========================================================

def clear_form():

    keys = [
        "product_name",
        "main_sku",
        "parent_id",

        "sofa_bulk",
        "bedframe_bulk",
        "mattress_bulk",

        "sofa_varieties",
        "bedframe_varieties",

        "sofa_custom_colors",
        "bedframe_custom_colors",

        "sofa_color_select_all",
        "bedframe_color_select_all",

        "sofa_selected_colors",
        "bedframe_selected_colors",

        "bedframe_sizes",
        "mattress_sizes",

        "bedframe_normal_fabric"
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


    # =====================================================
    # SOFA PARENT
    # =====================================================

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
            ", ".join(sizes),

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
            ", ".join(varieties),

        "Attribute 6 name":
            "Color",

        "Attribute 6 value(s)":
            ", ".join(colors),

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


    # =====================================================
    # SOFA VARIATIONS
    # =====================================================

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
    easy_clean_varieties,
    easy_clean_colors,
    include_normal_fabric
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


    # =====================================================
    # PARENT SERIES
    # =====================================================

    series_values = []

    if easy_clean_varieties:

        series_values.append(
            "Easy Clean"
        )

    if include_normal_fabric:

        series_values.append(
            "Normal Fabric"
        )


    # =====================================================
    # PARENT VARIETY
    # =====================================================

    variety_values = list(
        easy_clean_varieties
    )

    if include_normal_fabric:

        variety_values.append(
            "Normal Fabric"
        )


    # =====================================================
    # PARENT COLOR
    # =====================================================

    color_values = list(
        easy_clean_colors
    )

    # Normal Fabric colour code = Normal Fabric
    if include_normal_fabric:

        color_values.append(
            "Normal Fabric"
        )


    color_values = unique_list(
        color_values
    )


    # =====================================================
    # BEDFRAME PARENT
    # =====================================================

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
            ",".join(sizes),

        "Attribute 4 name":
            "Shipping",

        "Attribute 4 value(s)":
            "West Malaysia,East Malaysia",

        "Attribute 5 name":
            "Series",

        "Attribute 5 value(s)":
            ",".join(
                series_values
            ),

        "Attribute 6 name":
            "Variety",

        "Attribute 6 value(s)":
            ",".join(
                variety_values
            ),

        "Attribute 7 name":
            "Color",

        "Attribute 7 value(s)":
            ",".join(
                color_values
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


    # =====================================================
    # BEDFRAME VARIATIONS
    # =====================================================

    for item in size_data:

        size = item["size"]

        base_price = (
            item["price"]
        )


        # -------------------------------------------------
        # NORMAL FABRIC
        #
        # If Normal Fabric selected:
        # pasted price = Normal Fabric price
        # -------------------------------------------------

        if include_normal_fabric:

            normal_west_price = (
                base_price
            )


            for shipping in [
                "West Malaysia",
                "East Malaysia"
            ]:

                normal_price = (
                    normal_west_price
                    if shipping
                       == "West Malaysia"
                    else normal_west_price
                         + 1000
                )


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
                        "Normal Fabric",

                    "Attribute 6 name":
                        "Variety",

                    "Attribute 6 value(s)":
                        "Normal Fabric",

                    "Attribute 7 name":
                        "Color",

                    "Attribute 7 value(s)":
                        "",

                    "Regular price":
                        normal_price,

                    "Stock":
                        10,

                    "In stock?":
                        1,

                    "Parent":
                        parent_reference,

                    "SKU":
                        ""
                }


                rows.append(
                    row
                )

                variation_index += 1


        # -------------------------------------------------
        # EASY CLEAN
        #
        # If Normal Fabric is also selected:
        # Easy Clean = Normal Fabric + RM250
        #
        # If Normal Fabric is NOT selected:
        # pasted price = Easy Clean price
        # -------------------------------------------------

        if easy_clean_varieties:

            if include_normal_fabric:

                easy_clean_west_price = (
                    base_price + 250
                )

            else:

                easy_clean_west_price = (
                    base_price
                )


            for shipping in [
                "West Malaysia",
                "East Malaysia"
            ]:

                easy_clean_price = (
                    easy_clean_west_price
                    if shipping
                       == "West Malaysia"
                    else easy_clean_west_price
                         + 1000
                )


                for variety in (
                    easy_clean_varieties
                ):

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
                            easy_clean_price,

                        "Stock":
                            10,

                        "In stock?":
                            1,

                        "Parent":
                            parent_reference,

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


    # =====================================================
    # MATTRESS PARENT
    # =====================================================

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


    # =====================================================
    # MATTRESS VARIATIONS
    # =====================================================

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
    page_title="MPO/MELI New Product CSV",
    layout="centered"
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
# ID METHOD
# =========================================================

id_mode = st.radio(
    "WordPress ID Method",
    [
        "Auto ID",
        "Manual ID"
    ],
    horizontal=True,
    help=(
        "Auto ID：ID 留空，由 WordPress 自动生成。"
        "Main Variable SKU 必填，"
        "Variation Parent 跟 Main SKU。\n\n"
        "Manual ID：自己填写 Parent ID，"
        "Variation ID 自动 +1，"
        "Parent = id:xxx，SKU 全部留空。"
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
# AUTO / MANUAL ID
# =========================================================

if id_mode == "Auto ID":

    main_sku = st.text_input(
        "Main Variable SKU",
        key="main_sku",
        placeholder="Example: AUTUMN-BEDFRAME",
        help=(
            "Auto ID 模式只有 Main Variable "
            "需要 SKU。Variation SKU 留空。"
        )
    )

    parent_id = None


else:

    parent_id = st.number_input(
        "Parent ID",
        min_value=1,
        step=1,
        value=10000,
        key="parent_id"
    )

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
# DEFAULT VARIABLES
# =========================================================

size_data = []

parse_error = None

invalid_lines = []


# =========================================================
# SOFA UI
# =========================================================

if product_type == "Sofa":

    # -----------------------------------------------------
    # FABRIC
    # -----------------------------------------------------

    st.subheader(
        "Easy Clean Fabric"
    )


    selected_sofa_varieties = (
        st.multiselect(
            "Choose Fabric Code",
            EASY_CLEAN_VARIETIES,
            default=EASY_CLEAN_VARIETIES,
            key="sofa_varieties"
        )
    )


    # -----------------------------------------------------
    # COLORS
    # -----------------------------------------------------

    st.subheader(
        "Available Colors"
    )


    sofa_available_colors = (
        get_colors_for_varieties(
            selected_sofa_varieties
        )
    )


    sofa_select_all = st.checkbox(
        "Select All Available Colors",
        value=True,
        key="sofa_color_select_all"
    )


    if sofa_select_all:

        selected_sofa_colors = (
            sofa_available_colors
        )

        if selected_sofa_colors:

            st.caption(
                f"{len(selected_sofa_colors)} "
                f"colors selected."
            )

    else:

        selected_sofa_colors = (
            st.multiselect(
                "Choose Colors",
                sofa_available_colors,
                key="sofa_selected_colors"
            )
        )


    sofa_custom_colors = st.text_area(
        "Add New Colors (Optional)",
        key="sofa_custom_colors",
        placeholder=
"""One color per line

Example:
FG66151 Cream
Wave Light Beige"""
    )


    final_sofa_colors = unique_list(
        selected_sofa_colors
        + parse_custom_colors(
            sofa_custom_colors
        )
    )


    # -----------------------------------------------------
    # SIZE + PRICE
    # -----------------------------------------------------

    st.subheader(
        "Sofa Size & West Malaysia Price"
    )


    sofa_bulk = st.text_area(
        "Paste Size + Price from Excel",
        height=220,
        key="sofa_bulk",
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

    # -----------------------------------------------------
    # EASY CLEAN
    # -----------------------------------------------------

    st.subheader(
        "Easy Clean Fabric"
    )


    selected_bedframe_varieties = (
        st.multiselect(
            "Choose Easy Clean Fabric Code",
            EASY_CLEAN_VARIETIES,
            default=EASY_CLEAN_VARIETIES,
            key="bedframe_varieties"
        )
    )


    # -----------------------------------------------------
    # NORMAL FABRIC
    # -----------------------------------------------------

    include_normal_fabric = st.checkbox(
        "Include Normal Fabric",
        value=False,
        key="bedframe_normal_fabric"
    )


    if include_normal_fabric:

        st.info(
            "Normal Fabric selected: "
            "the prices you paste below are "
            "Normal Fabric prices. "
            "Easy Clean will automatically be "
            "+ RM250."
        )

    else:

        st.caption(
            "Normal Fabric not selected: "
            "the prices you paste below are "
            "Easy Clean prices."
        )


    # -----------------------------------------------------
    # COLORS
    # -----------------------------------------------------

    st.subheader(
        "Available Colors"
    )


    bedframe_available_colors = (
        get_colors_for_varieties(
            selected_bedframe_varieties
        )
    )


    bedframe_select_all = st.checkbox(
        "Select All Available Colors",
        value=True,
        key="bedframe_color_select_all"
    )


    if bedframe_select_all:

        selected_bedframe_colors = (
            bedframe_available_colors
        )

        if selected_bedframe_colors:

            st.caption(
                f"{len(selected_bedframe_colors)} "
                f"Easy Clean colors selected."
            )

    else:

        selected_bedframe_colors = (
            st.multiselect(
                "Choose Easy Clean Colors",
                bedframe_available_colors,
                key="bedframe_selected_colors"
            )
        )


    bedframe_custom_colors = st.text_area(
        "Add New Easy Clean Colors (Optional)",
        key="bedframe_custom_colors",
        placeholder=
"""One color per line

Example:
Embony Cream
Wave Blue Grey"""
    )


    final_bedframe_colors = (
        unique_list(
            selected_bedframe_colors
            + parse_custom_colors(
                bedframe_custom_colors
            )
        )
    )


    if include_normal_fabric:

        st.caption(
            'Normal Fabric Color Code: "Normal Fabric"'
        )


    # -----------------------------------------------------
    # SIZE
    # -----------------------------------------------------

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
            key="bedframe_sizes"
        )
    )


    selected_bedframe_sizes = [
        size
        for size in SIZE_ORDER
        if size in bedframe_selected_raw
    ]


    if selected_bedframe_sizes:

        st.info(
            "Paste prices in this order: "
            + " → ".join(
                selected_bedframe_sizes
            )
        )


    # -----------------------------------------------------
    # PRICE
    # -----------------------------------------------------

    bedframe_bulk = st.text_area(
        "Paste West Malaysia Price Only",
        height=180,
        key="bedframe_bulk",
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
            key="mattress_sizes"
        )
    )


    selected_mattress_sizes = [
        size
        for size in SIZE_ORDER
        if size in mattress_selected_raw
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

    preview_rows = []


    for item in size_data:

        # BEDFRAME WITH NORMAL FABRIC
        if (
            product_type == "Bedframe"
            and include_normal_fabric
        ):

            preview_rows.append({

                "Size":
                    item["size"],

                "Normal Fabric West":
                    item["price"],

                "Normal Fabric East":
                    item["price"] + 1000,

                "Easy Clean West":
                    item["price"] + 250,

                "Easy Clean East":
                    item["price"] + 1250
            })


        # NORMAL PREVIEW
        else:

            preview_rows.append({

                "Size":
                    item["size"],

                "West Malaysia":
                    item["price"],

                "East Malaysia":
                    item["price"] + 1000
            })


    preview = pd.DataFrame(
        preview_rows
    )


    st.subheader(
        "Price Preview"
    )


    st.dataframe(
        preview,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# BUTTONS
# =========================================================

col1, col2 = st.columns(2)


with col1:

    generate_clicked = st.button(
        "Generate CSV",
        type="primary",
        use_container_width=True
    )


with col2:

    st.button(
        "Clear All",
        on_click=clear_form,
        use_container_width=True
    )


# =========================================================
# GENERATE
# =========================================================

if generate_clicked:

    errors = []


    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------

    if not product_name.strip():

        errors.append(
            "Product Name 不能为空。"
        )


    if (
        id_mode == "Auto ID"
        and not main_sku.strip()
    ):

        errors.append(
            "Auto ID 模式必须填写 "
            "Main Variable SKU。"
        )


    if not size_data:

        errors.append(
            "没有有效的 Size / Price。"
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
                "Sofa 至少选择一个 "
                "Easy Clean Fabric Code。"
            )


        if not final_sofa_colors:

            errors.append(
                "Sofa 至少需要一个 Color。"
            )


    # -----------------------------------------------------
    # BEDFRAME VALIDATION
    # -----------------------------------------------------

    if product_type == "Bedframe":

        if (
            not selected_bedframe_varieties
            and not include_normal_fabric
        ):

            errors.append(
                "Bedframe 至少要选择 "
                "Easy Clean 或 Normal Fabric。"
            )


        if (
            selected_bedframe_varieties
            and not final_bedframe_colors
        ):

            errors.append(
                "有选择 Easy Clean Fabric，"
                "所以至少要选择一个 "
                "Easy Clean Color。"
            )


    # -----------------------------------------------------
    # SHOW ERRORS
    # -----------------------------------------------------

    if errors:

        for error in errors:

            st.error(
                error
            )


    # -----------------------------------------------------
    # GENERATE DATAFRAME
    # -----------------------------------------------------

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
                final_sofa_colors
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
                include_normal_fabric
            )


        else:

            df = generate_mattress(
                product_name.strip(),
                published_value,
                size_data,
                id_mode,
                parent_id,
                main_sku
            )


        # =================================================
        # EXPORT
        # =================================================

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
            df.head(20),
            use_container_width=True,
            hide_index=True
        )


        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name=(
                f"{safe_filename(product_name)} "
                f"Import.csv"
            ),
            mime="text/csv",
            use_container_width=True
        )
