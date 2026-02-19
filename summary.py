def generate_summary(df):
    return {
        "Total Videos": len(df),
        "Total Views": int(df["views"].sum()),
        "Total Likes": int(df["likes"].sum()),
        "Total Comments": int(df["comments"].sum()),
        "Average Engagement": round((df["likes"] + df["comments"]).mean(), 2)
    }
