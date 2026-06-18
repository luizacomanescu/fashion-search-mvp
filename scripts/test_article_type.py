import pandas as pd

df = pd.read_csv(
    "data/raw/fashion-product-images-dataset/styles.csv",
    on_bad_lines="skip"
)

print(df["articleType"].value_counts().head(50))