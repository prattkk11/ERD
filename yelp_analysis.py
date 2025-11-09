import marimo

__generated_with = "0.6.14"
app = marimo.App(width="full")


# -------------------- IMPORTS & SETTINGS --------------------
@app.cell
def __():
    import pandas as pd
    import matplotlib.pyplot as plt
    import marimo as mo
    import warnings

    warnings.filterwarnings("ignore")
    return pd, plt, mo


# -------------------- LOAD DATA --------------------
@app.cell
def __(pd):
    # ✅ Load only sample rows for fast performance
    business = pd.read_json("yelp_academic_dataset_business.json", lines=True, nrows=10000)
    review = pd.read_json("yelp_academic_dataset_review.json", lines=True, nrows=10000)
    checkin = pd.read_json("yelp_academic_dataset_checkin.json", lines=True, nrows=5000)
    user = pd.read_json("yelp_academic_dataset_user.json", lines=True, nrows=5000)
    tip = pd.read_json("yelp_academic_dataset_tip.json", lines=True, nrows=5000)

    # ✅ Focus on restaurants only
    restaurants = business[business["categories"].fillna("").str.contains("Restaurant", case=False, na=False)]

    return business, review, checkin, user, tip, restaurants


# -------------------- USER CONTROLS --------------------
@app.cell
def __(mo, restaurants):
    # ✅ Dropdowns and slider (modern Marimo syntax)
    states = sorted(restaurants["state"].dropna().unique().tolist())
    state_select = mo.ui.dropdown(options=states, label="Select State", value="AZ")

    cuisines = ["All", "Italian", "Mexican", "Chinese", "Indian", "American"]
    cuisine_select = mo.ui.dropdown(options=cuisines, label="Cuisine Type", value="All")

    min_rating = mo.ui.slider(start=1, stop=5, step=0.5, label="Minimum Rating", value=3.5)

    mo.hstack([state_select, cuisine_select, min_rating])
    return state_select, cuisine_select, min_rating


# -------------------- CHART 1: RESTAURANT INSIGHTS --------------------
@app.cell
def __(pd, plt, mo, restaurants, review, state_select, cuisine_select, min_rating):
    # ✅ Filter data
    _filtered = restaurants[restaurants["state"] == state_select.value]

    if cuisine_select.value != "All":
        _filtered = _filtered[_filtered["categories"].fillna("").str.contains(cuisine_select.value, case=False)]

    _filtered = _filtered[_filtered["stars"] >= min_rating.value]

    # ✅ Top cities and ratings
    _top_cities = (
        _filtered.groupby("city")["business_id"]
        .count()
        .sort_values(ascending=False)
        .head(10)
    )

    _avg_ratings = (
        _filtered.groupby("city")["stars"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    # ✅ Visualization (unique variable names)
    _fig1, _ax1 = plt.subplots(1, 2, figsize=(10, 4))
    _top_cities.plot(kind="barh", ax=_ax1[0], title="Top 10 Cities by Restaurant Count")
    _avg_ratings.plot(kind="barh", ax=_ax1[1], color="orange", title="Top 10 Cities by Average Rating")
    plt.tight_layout()

    _insights = mo.md(f"""
    ### 🍽️ Yelp Restaurant Insights for `{state_select.value}`
    **Cuisine filter:** {cuisine_select.value}  
    **Minimum rating:** {min_rating.value}⭐  
    **Restaurants analyzed:** {len(_filtered):,}
    """)

    # ✅ Display insights and chart
    mo.vstack([_insights, _fig1])

    return _filtered, _top_cities, _avg_ratings, _fig1


# -------------------- CHART 2: REVIEW TRENDS --------------------
@app.cell
def __(_filtered, pd, review, mo, plt):
    # ✅ Monthly review activity
    _joined = review.merge(_filtered[["business_id", "name", "city"]], on="business_id", how="inner")
    _joined["date"] = pd.to_datetime(_joined["date"], errors="coerce")
    _monthly = _joined.groupby(_joined["date"].dt.to_period("M")).size()

    _fig2, _ax2 = plt.subplots(figsize=(8, 4))
    if not _monthly.empty:
        _monthly.plot(kind="line", ax=_ax2, title="📆 Review Volume Over Time")
        _ax2.set_xlabel("Month")
        _ax2.set_ylabel("Number of Reviews")
    else:
        _ax2.text(0.3, 0.5, "No review data available", fontsize=12)
    plt.tight_layout()

    _fig2

    return _joined, _monthly, _fig2


# -------------------- TABLE: TOP USERS --------------------
@app.cell
def __(mo, user):
    # ✅ Bonus: Top Yelp Users by Review Count
    # _top_users = user.nlargest(10, "review_count")[["name", "review_count"]]
    # 
    # mo.md("### 👥 Top 10 Active Yelp Users")
    # mo.ui.table(_top_users)
    # return _top_users
    pass


# -------------------- DASHBOARD SUMMARY --------------------
@app.cell
def __(mo):
    mo.md("""
    ---
    ## 🧠 Summary Dashboard

    - Use **dropdowns** to choose a State and Cuisine Type  
    - Adjust **slider** to change minimum rating  
    - Charts update instantly:
      1. Top 10 Cities by Restaurant Count  
      2. Top 10 Cities by Average Rating  
      
    - Fully interactive web dashboard using Yelp’s 5 datasets  
    ---
    """)
    return


# -------------------- RUN APP --------------------
if __name__ == "__main__":
    app.run()
