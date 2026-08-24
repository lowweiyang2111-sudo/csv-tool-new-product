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
    "Guardian",
]

SOFA_COLOR_VALUES = """FG66151 Beige, FG66151 Carolina Blue, FG66151 Cedar,
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

SOFA_COLOR_VALUES = " ".join(
    line.strip()
    for line in SOFA_COLOR_VALUES.splitlines()
)

BEDFRAME_VARIETIES = [
    "Embony",
    "Wave",
    "Loro",
]

# =========================================================
# LATEST WORDPRESS CSV COLUMNS
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
    "Attribute 1 name",
    "Attribute 1 value(s)",
    "Attribute 4 name",
    "Attribute 4 value(s)",
    "Attribute 5 name",
    "Attribute 5 value(s)",
    "Attribute 6 name",
    "Attribute 6 value(s)",
    "Regular price",
    "Stock",
    "In stock?",
    "Parent",
    "SKU",
]

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def parse_price(text):
    """
    Accept:
    2699
    2,699
    2,699.00
    RM 2,699.00
    """

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
    Sofa:
    copy Size + Price from Excel.

    Example:
    2LA + RADB (28")    4,590.00
    1S (28")            2,990.00
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

            size = " ".join(
                parts[:-1]
            ).strip()

            if not size:
                raise ValueError("Missing size")

            result.append({
                "size": size,
                "price": price
            })

        except Exception:
            invalid.append(raw_line)

    return result, invalid


def parse_price_only(text, sizes):
    """
    For Mattress / Bedframe.

    Only paste price:
    2699
    2499
    """

    price_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(price_lines) != len(sizes):

        return [], (
            f"需要 {len(sizes)} 个价格，"
            f"但目前贴了 {len(price_lines)} 个。"
        )

    result = []

    try:

        for size, price_line in zip(
            sizes,
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
            "请使用例如 2,699.00 或 2699。"
        )

    return result, None


def safe_filename(name):

    cleaned = re.sub(
        r'[\\/:*?"<>|]+',
        "_",
        name.strip()
    )

    return cleaned or "product"


# =========================================================
# ID / SKU LOGIC
# =========================================================

def get_id_value(
    id_mode,
    parent_id,
    variation_index=None
):

    # WordPress generate ID automatically
    if id_mode == "WordPress Auto ID":
        return ""

    # Parent row
    if variation_index is None:
        return int(parent_id)

    # Variation +1
    return int(parent_id) + variation_index


def get_parent_reference(
    id_mode,
    parent_id,
    main_sku
):

    # New WordPress method
    if id_mode == "WordPress Auto ID":
        return main_sku.strip()

    # Old/manual method
    return f"id:{int(parent_id)}"


def get_parent_sku(
    id_mode,
    main_sku
):

    if id_mode == "WordPress Auto ID":
        return main_sku.strip()

    return ""


# =========================================================
# CLEAR ALL
# =========================================================

def clear_form():

    keys_to_clear = [
        "product_name",
        "main_sku",
        "parent_id",
        "sofa_bulk",
        "bedframe_bulk",
        "mattress_bulk",
    ]

    for key in keys_to_clear:

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
            ", ".join(
                SOFA_VARIETIES
            ),

        "Attribute 6 name":
            "Color",

        "Attribute 6 value(s)":
            SOFA_COLOR_VALUES,

        "Regular price":
            "",

        "Stock":
            "",

        "In stock?":
            ""
    }

    rows.append(parent_row)

    variation_index = 1

    # ==========================
    # SOFA VARIATIONS
    # ==========================

    for item in size_data:

        size = item["size"]

        west_price = item["price"]

        for shipping in [
            "West Malaysia",
            "East Malaysia"
        ]:

            if shipping == "West Malaysia":

                price = west_price

            else:

                price = west_price + 1000

            for variety in SOFA_VARIETIES:

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

                rows.append(row)

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
            "Easy Clean",

        "Attribute 6 name":
            "Variety",

        "Attribute 6 value(s)":
            ",".join(
                BEDFRAME_VARIETIES
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

    rows.append(parent_row)

    variation_index = 1

    # ==========================
    # BEDFRAME VARIATIONS
    # ==========================

    for item in size_data:

        size = item["size"]

        west_price = item["price"]

        for shipping in [
            "West Malaysia",
            "East Malaysia"
        ]:

            if shipping == "West Malaysia":

                price = west_price

            else:

                # Your company rule
                price = west_price + 1000

            for variety in BEDFRAME_VARIETIES:

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

                    "Regular price":
                        price,

                    "Stock":
                        10,

                    "In stock?":
                        1,

                    "Parent":
                        parent_reference,

                    "SKU":
                        ""
                }

                rows.append(row)

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
            ", ".join(sizes),

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

    rows.append(parent_row)

    variation_index = 1

    # ==========================
    # MATTRESS VARIATIONS
    # ==========================

    for item in size_data:

        size = item["size"]

        west_price = item["price"]

        for shipping in [
            "West Malaysia",
            "East Malaysia"
        ]:

            if shipping == "West Malaysia":

                price = west_price

            else:

                price = west_price + 1000

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

            rows.append(row)

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
    horizontal=True,
    key="product_type"
)

# =========================================================
# ID METHOD
# =========================================================

id_mode = st.radio(
    "WordPress ID Method",
    [
        "WordPress Auto ID",
        "Manual ID"
    ],
    horizontal=True,
    key="id_mode",
    help=(
        "Auto ID: ID 留空，Variable SKU 必填，"
        "Variation Parent 跟 Variable SKU。\n\n"
        "Manual ID: 自己填 Parent ID，"
        "Variation ID 自动 +1，"
        "Parent = id:xxx。"
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

if id_mode == "WordPress Auto ID":

    main_sku = st.text_input(
        "Main Variable SKU (Required)",
        key="main_sku",
        placeholder="Example: AUTUMN-BEDFRAME",
        help=(
            "只有 main variable 需要 SKU。"
            "Variation SKU 会自动留空。"
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

if product_type in [
    "Sofa",
    "Mattress"
]:

    visibility = st.radio(
        "Product Status",
        [
            "Public",
            "Private"
        ],
        horizontal=True,
        key="visibility"
    )

    published_value = (
        1
        if visibility == "Public"
        else 0
    )

else:

    # Latest Bedframe template
    # does not contain Published column
    published_value = 1

# =========================================================
# SIZE / PRICE INPUT
# =========================================================

size_data = []

parse_error = None

invalid_lines = []

# =========================================================
# SOFA
# =========================================================

if product_type == "Sofa":

    st.subheader(
        "Sofa Size & West Malaysia Price"
    )

    sofa_bulk = st.text_area(
        "Paste Size + Price from Excel",
        height=220,
        key="sofa_bulk",
        placeholder="""2LA + RADB (28")    4,590.00
1S (28")              2,990.00
2S (28")              3,590.00"""
    )

    size_data, invalid_lines = (
        parse_sofa_size_price(
            sofa_bulk
        )
    )

# =========================================================
# BEDFRAME
# =========================================================

elif product_type == "Bedframe":

    st.subheader(
        "Bedframe West Malaysia Price"
    )

    st.caption(
        "2 个价格：King → Queen\n"
        "4 个价格：King → Queen → "
        "Super Single → Single"
    )

    bedframe_bulk = st.text_area(
        "Paste Price Only",
        height=180,
        key="bedframe_bulk",
        placeholder="""2,699.00
2,499.00
2,199.00
2,099.00"""
    )

    price_count = len([
        x
        for x in bedframe_bulk.splitlines()
        if x.strip()
    ])

    if price_count == 2:

        size_data, parse_error = (
            parse_price_only(
                bedframe_bulk,
                [
                    "King",
                    "Queen"
                ]
            )
        )

    elif price_count == 4:

        size_data, parse_error = (
            parse_price_only(
                bedframe_bulk,
                [
                    "King",
                    "Queen",
                    "Super Single",
                    "Single"
                ]
            )
        )

    elif price_count > 0:

        parse_error = (
            "Bedframe 只接受：\n"
            "2 个价格（King、Queen）\n"
            "或 4 个价格"
            "（King、Queen、Super Single、Single）。"
        )

# =========================================================
# MATTRESS
# =========================================================

else:

    st.subheader(
        "Mattress West Malaysia Price"
    )

    mattress_size_set = st.radio(
        "Mattress Sizes",
        [
            "Queen + King",
            "Single + Super Single + Queen + King"
        ],
        horizontal=True,
        key="mattress_size_set"
    )

    if mattress_size_set == "Queen + King":

        mattress_sizes = [
            "Queen",
            "King"
        ]

        mattress_placeholder = """1,599.00
2,599.00"""

    else:

        mattress_sizes = [
            "Single",
            "Super Single",
            "Queen",
            "King"
        ]

        mattress_placeholder = """1,099.00
1,299.00
1,599.00
2,599.00"""

    st.caption(
        "价格顺序必须跟选择的 Size 顺序一致。"
    )

    mattress_bulk = st.text_area(
        "Paste Price Only",
        height=180,
        key="mattress_bulk",
        placeholder=mattress_placeholder
    )

    if mattress_bulk.strip():

        size_data, parse_error = (
            parse_price_only(
                mattress_bulk,
                mattress_sizes
            )
        )

# =========================================================
# ERROR
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

    preview_df = pd.DataFrame([
        {
            "Size":
                item["size"],

            "West Malaysia":
                item["price"],

            "East Malaysia":
                item["price"] + 1000
        }
        for item in size_data
    ])

    st.dataframe(
        preview_df,
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

    if not product_name.strip():

        errors.append(
            "Product Name 不能为空。"
        )

    if (
        id_mode == "WordPress Auto ID"
        and not main_sku.strip()
    ):

        errors.append(
            "Auto ID 模式必须填写 "
            "Main Variable SKU。"
        )

    if not size_data:

        errors.append(
            "没有读取到有效的 Size / Price。"
        )

    if parse_error:

        errors.append(
            parse_error
        )

    if errors:

        for error in errors:

            st.error(
                error
            )

    else:

        # ==========================
        # SOFA
        # ==========================

        if product_type == "Sofa":

            df = generate_sofa(
                product_name.strip(),
                published_value,
                size_data,
                id_mode,
                parent_id,
                main_sku
            )

        # ==========================
        # BEDFRAME
        # ==========================

        elif product_type == "Bedframe":

            df = generate_bedframe(
                product_name.strip(),
                size_data,
                id_mode,
                parent_id,
                main_sku
            )

        # ==========================
        # MATTRESS
        # ==========================

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
        # EXPORT
        # ==========================

        csv_bytes = (
            df
            .to_csv(
                index=False
            )
            .encode(
                "utf-8-sig"
            )
        )

        st.success(
            f"CSV Generated — "
            f"{len(df) - 1} variation rows"
        )

        st.dataframe(
            df.head(12),
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
